# -*- coding: utf-8 -*-
"""
Class for transmitting course metadata to Degreed.
"""

from __future__ import absolute_import, unicode_literals

import json

from integrated_channels.degreed.client import DegreedAPIClient
from integrated_channels.integrated_channel.transmitters.course_metadata import CourseTransmitter

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist


class DegreedCourseTransmitter(CourseTransmitter):
    """
    This transmitter transmits a course metadata export to Degreed.
    """

    def __init__(self, enterprise_configuration, client=DegreedAPIClient):
        """
        By default, use the ``DegreedAPIClient`` for course metadata transmission to Degreed.
        """
        super(DegreedCourseTransmitter, self).__init__(
            enterprise_configuration=enterprise_configuration,
            client=client
        )

    def transmit(self, payload):
        """
        Transmit the course metadata payload to the integrated channel.
        """
        total_transmitted = 0
        errors = []
        status_codes = []
        for course_metadata, method in payload.export():
            status_code, body = self.transmit_block(course_metadata, method=method)
            status_codes.append(str(status_code))
            error_message = body if status_code >= 400 else ''
            if error_message:
                errors.append(error_message)
            else:
                total_transmitted += len(course_metadata)

        error_message = ', '.join(errors) if errors else ''
        code_string = ', '.join(status_codes)

        # pylint: disable=invalid-name
        CatalogTransmissionAudit = apps.get_model('integrated_channel', 'CatalogTransmissionAudit')
        try:
            last_catalog_transmission = CatalogTransmissionAudit.objects.filter(
                error_message='',
                enterprise_customer_uuid=self.enterprise_configuration.enterprise_customer.uuid
            ).latest('created')
            last_audit_summary = json.loads(last_catalog_transmission.audit_summary)
        except ObjectDoesNotExist:
            last_audit_summary = {}

        CatalogTransmissionAudit(
            enterprise_customer_uuid=self.enterprise_configuration.enterprise_customer.uuid,
            total_courses=len(payload.courses),
            status=code_string,
            error_message=error_message,
            audit_summary=json.dumps(payload.resolve_removed_courses(last_audit_summary)),
        ).save()
