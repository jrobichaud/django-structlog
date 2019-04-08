import logging
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
import structlog

from django_structlog import middlewares


class TestRequestLoggingMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.logger = structlog.getLogger(__name__)

    def test_process_request_anonymous(self):
        middleware = middlewares.RequestLoggingMiddleware()
        request = self.factory.get('/foo')
        request.user = AnonymousUser()

        expected_uuid = '00000000-0000-0000-0000-000000000000'
        with patch('uuid.UUID.__str__', return_value=expected_uuid):
            middleware.process_request(request)

        self.assertEqual(expected_uuid, request.id)

        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")

        self.assertEqual(1, len(log_results.records))
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertIn('request_id', record.msg)
        self.assertEqual(expected_uuid, record.msg['request_id'])
        self.assertIn('user_id', record.msg)
        self.assertIsNone(record.msg['user_id'])

    def tearDown(self):
        self.logger.new()
