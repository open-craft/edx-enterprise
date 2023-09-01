"""
Tests for the xAPI models.
"""

import base64
import json
import unittest

import responses
from pytest import mark

from django.core.exceptions import ValidationError

from integrated_channels.xapi.models import XAPIAuthMethods, XAPILRSConfiguration
from test_utils import factories


@mark.django_db
class TestXAPILRSConfiguration(unittest.TestCase):
    """
    Tests for the ``XAPILRSConfiguration`` model.
    """

    def setUp(self):
        super().setUp()
        self.x_api_lrs_config = factories.XAPILRSConfigurationFactory()
        self.x_api_oauth_lrs_config = factories.XAPILRSConfigurationFactory(
            auth_method=XAPIAuthMethods.OAUTH2_CLIENT_CREDS
        )

    def test_string_representation(self):
        """
        Test the string representation of the model.
        """
        expected_string = '<XAPILRSConfiguration for Enterprise {enterprise_name}>'.format(
            enterprise_name=self.x_api_lrs_config.enterprise_customer.name,
        )
        assert expected_string == self.x_api_lrs_config.__repr__()

    def test_authorization_header(self):
        """
        Test the authorization header for the configuration.
        """
        expected_header = 'Basic {}'.format(
            base64.b64encode('{key}:{secret}'.format(
                key=self.x_api_lrs_config.key,
                secret=self.x_api_lrs_config.secret
            ).encode()).decode()
        )
        assert expected_header == self.x_api_lrs_config.authorization_header

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.x_api_oauth_lrs_config.auth_url,
                body=json.dumps({
                    'access_token': 'test_token',
                    'token_type': 'bearer',
                    'expires_in': 3600
                }),
                status=200,
                content_type="application/json"
            )
            expected_header = 'Bearer test_token'

            assert expected_header == self.x_api_oauth_lrs_config.authorization_header

    def test_auth_url_and_scope_are_required_oauth2_auth_method(self):
        """
        Test that a validation error is raised when the auth_url or scope is not set for auth method OAUTH2_CC.
        """
        conf = XAPILRSConfiguration(
            enterprise_customer=factories.EnterpriseCustomerFactory(),
            endpoint="https://xapi.endpoint",
            key="key",
            secret="secret",
            active=True,
            auth_method="OAUTH2_CC",
        )
        with self.assertRaises(ValidationError) as context:
            conf.full_clean()
            self.assertIn('auth_url', context.exception.message)
            self.assertIn('oauth_scope', context.exception.message)

        conf.auth_url = "https://auth.url"

        with self.assertRaises(ValidationError) as context:
            conf.full_clean()
            self.assertIn('oauth_scope', context.exception.message)

        conf.auth_url = None
        conf.oauth_scope = "xapi:write"

        with self.assertRaises(ValidationError) as context:
            conf.full_clean()
            self.assertIn('auth_url', context.exception.message)


@mark.django_db
class TestXAPILearnerDataTransmissionAudit(unittest.TestCase):
    """
    Tests for the ``XAPILearnerDataTransmissionAudit`` model.
    """

    def setUp(self):
        super().setUp()
        self.xapi_learner_transmission = factories.XAPILearnerDataTransmissionAuditFactory(
            user_id=factories.UserFactory().id,
            course_id='dummy'
        )

    def test_string_representation(self):
        """
        Test the string representation of the model.
        """
        expected_string = '<XAPILearnerDataTransmissionAudit {id} for enterprise enrollment {ece_id}, XAPI user ' \
                          '{user_id}, and course {course_id}>'.format(
                              id=self.xapi_learner_transmission.id,
                              ece_id=self.xapi_learner_transmission.enterprise_course_enrollment_id,
                              user_id=self.xapi_learner_transmission.user_id,
                              course_id=self.xapi_learner_transmission.course_id
                          )
        assert expected_string == str(self.xapi_learner_transmission)
