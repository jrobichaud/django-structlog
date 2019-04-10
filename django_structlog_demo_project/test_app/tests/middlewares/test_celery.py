import logging
from unittest.mock import Mock

import structlog
from celery import shared_task
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from django_structlog import middlewares


class TestCeleryMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.logger = structlog.getLogger(__name__)

    def test_call(self):
        mock_get_response = Mock()
        mock_request = Mock()
        middleware = middlewares.CeleryMiddleware(mock_get_response)
        middleware(mock_request)
        mock_get_response.assert_called_once_with(mock_request)

    def test_task_enqueue(self):
        expected_uuid = '00000000-0000-0000-0000-000000000000'
        self.logger.bind(request_id=expected_uuid)

        @shared_task
        def test_task(value):  # pragma: no cover
            pass

        request = self.factory.get('/foo')
        request.user = AnonymousUser()

        # noinspection PyUnusedLocal
        middleware = middlewares.CeleryMiddleware(None)

        with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.INFO) as log_results:
            test_task.delay('foo')

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('INFO', record.levelname)
        self.assertIn('task_id', record.msg)
        self.assertIn(expected_uuid, record.msg['request_id'])

    def tearDown(self):
        self.logger.new()
