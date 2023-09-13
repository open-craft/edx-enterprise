"""
Models for xAPI.
"""

import base64
from functools import cached_property

import requests

from django.contrib import auth
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel

from enterprise.models import EnterpriseCustomer
from integrated_channels.integrated_channel.models import LearnerDataTransmissionAudit

User = auth.get_user_model()


class XAPIAuthMethods(models.TextChoices):
    HTTP_BASIC = 'BASIC', _('HTTP Basic')
    OAUTH2_CLIENT_CREDS = 'OAUTH2_CC', _('OAuth 2.0 Client Credentials')


class XAPILRSConfiguration(TimeStampedModel):
    """
    xAPI LRS configurations.

    .. no_pii:
    """

    enterprise_customer = models.OneToOneField(
        EnterpriseCustomer,
        blank=False,
        null=False,
        help_text=_('Enterprise Customer associated with the configuration.'),
        on_delete=models.deletion.CASCADE
    )
    version = models.CharField(max_length=16, default='1.0.1', help_text=_('Version of xAPI.'))
    endpoint = models.URLField(help_text=_('URL of the LRS.'))
    key = models.CharField(max_length=255, verbose_name="Client ID", help_text=_('Key of xAPI LRS.'))
    secret = models.CharField(max_length=255, verbose_name="Client Secret", help_text=_('secret of xAPI LRS.'))
    active = models.BooleanField(
        blank=False,
        null=False,
        help_text=_('Is this configuration active?'),
    )
    auth_method = models.CharField(
        max_length=16,
        verbose_name="xAPI POST Authentication Method",
        choices=XAPIAuthMethods.choices,
        default=XAPIAuthMethods.HTTP_BASIC,
        help_text=_('The Authentication Method to use when sending the xAPI data to the endpoint.')
    )
    auth_url = models.URLField(
        blank=True,
        null=True,
        help_text=_("URL to use for authentication. Eg., Token URL for OAuth")
    )
    oauth_scope = models.CharField(
        max_length=255,
        verbose_name=_('OAuth scope'),
        blank=True,
        null=True,
        help_text=_('The "scope" to pass for OAuth authentication.')
    )
    plain_course_id_in_statements = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        verbose_name=_("Use plain Course ID in xAPI Statements"),
        help_text=_('Uses the plain course ID (eg., course-v1:X+Y+Z) instead of the URI format in xAPI statements.')
    )

    class Meta:
        app_label = 'xapi'

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return '<XAPILRSConfiguration for Enterprise {enterprise_name}>'.format(
            enterprise_name=self.enterprise_customer.name
        )

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()

    @property
    def authorization_header(self):
        """
        Authorization header for authenticating requests to LRS.
        """
        if self.auth_method == XAPIAuthMethods.OAUTH2_CLIENT_CREDS:
            return f'Bearer {self.access_token}'

        return 'Basic {}'.format(
            base64.b64encode('{key}:{secret}'.format(key=self.key, secret=self.secret).encode()).decode()
        )

    def clean(self):
        errors = {}
        # Don't allow OAuth2 Client Credentials method to be set without auth_url, or oauth_scope
        if self.auth_method == XAPIAuthMethods.OAUTH2_CLIENT_CREDS:
            if not self.auth_url:
                errors['auth_url'] = _("Authentication URL is required for the OAuth2 authentication method.")
            if not self.oauth_scope:
                errors['oauth_scope'] = _("OAuth scope is required for the OAuth2 authentication method.")

        if errors:
            raise ValidationError(errors)

    @cached_property
    def access_token(self):
        """
        Gets the access token from the OAuth2 Authentication endpoint return it.
        """
        if self.auth_method != XAPIAuthMethods.OAUTH2_CLIENT_CREDS:
            raise RuntimeError("Access Token can be fetched only for OAuth2 Client Credentials authenication method.")

        data = {
            "grant_type": "client_credentials",
            "scope": self.oauth_scope,
            "client_id": self.key,
            "client_secret": self.secret
        }
        response = requests.post(self.auth_url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]


class XAPILearnerDataTransmissionAudit(LearnerDataTransmissionAudit):
    """
    The payload we sent to XAPI at a given point in time for an enterprise course enrollment.

    .. no_pii:
    """

    user = models.ForeignKey(
        User,
        blank=False,
        null=False,
        related_name='xapi_transmission_audit',
        on_delete=models.CASCADE,
    )

    class Meta:
        app_label = 'xapi'
        unique_together = ("user", "course_id")

    def __str__(self):
        """
        Return a human-readable string representation of the object.
        """
        return (
            '<XAPILearnerDataTransmissionAudit {transmission_id} for enterprise enrollment '
            '{enterprise_course_enrollment_id}, XAPI user {user_id}, and course {course_id}>'.format(
                transmission_id=self.id,
                enterprise_course_enrollment_id=self.enterprise_course_enrollment_id,
                user_id=self.user.id,
                course_id=self.course_id
            )
        )
