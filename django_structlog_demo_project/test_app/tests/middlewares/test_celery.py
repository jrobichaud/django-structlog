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
        with middlewares.CeleryMiddleware(mock_get_response) as middleware:
            middleware(mock_request)
        mock_get_response.assert_called_once_with(mock_request)

    def test_defer_task(self):
        expected_uuid = '00000000-0000-0000-0000-000000000000'

        request = self.factory.get('/foo')
        request.user = AnonymousUser()

        @shared_task
        def test_task(value):  # pragma: no cover
            pass

        with middlewares.CeleryMiddleware(None):
            with structlog.threadlocal.tmp_bind(self.logger):
                self.logger.bind(request_id=expected_uuid)
                with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.INFO) as log_results:
                    test_task.delay('foo')

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task enqueued', record.msg['event'])
        self.assertEqual('INFO', record.levelname)
        self.assertIn('task_id', record.msg)
        self.assertEqual(expected_uuid, record.msg['request_id'])

    def test_receiver_before_task_publish(self):
        expected_uuid = '00000000-0000-0000-0000-000000000000'
        expected_user_id = '1234'

        headers = {
            'kwargsrepr': "{}"
        }
        with middlewares.CeleryMiddleware() as middleware:
            with structlog.threadlocal.tmp_bind(self.logger):
                self.logger.bind(
                    request_id=expected_uuid,
                    user_id=expected_user_id
                )
                task_kwargs = {}
                middleware.receiver_before_task_publish(body=((), task_kwargs), headers=headers)

        self.assertDictEqual({
                '__django_structlog__': {
                    'request_id': expected_uuid,
                    'user_id': expected_user_id,
                }
            },
            task_kwargs
        )

    def test_receiver_after_task_publish(self):
        expected_task_id = '00000000-0000-0000-0000-000000000000'
        headers = {'id': expected_task_id}

        with middlewares.CeleryMiddleware(None) as middleware:
            with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.INFO) as log_results:
                middleware.receiver_after_task_publish(headers=headers)

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task enqueued', record.msg['event'])
        self.assertEqual('INFO', record.levelname)
        self.assertIn('task_id', record.msg)
        self.assertEqual(expected_task_id, record.msg['task_id'])

    def test_receiver_task_pre_run(self):
        expected_request_uuid = '00000000-0000-0000-0000-000000000000'
        task_id = '11111111-1111-1111-1111-111111111111'
        expected_user_id = '1234'
        task_kwargs = {
            '__django_structlog__': {
                'request_id': expected_request_uuid,
                'user_id': expected_user_id,
            }
        }
        with middlewares.CeleryMiddleware() as middleware:
            with structlog.threadlocal.tmp_bind(self.logger):
                self.logger.bind(foo='bar')

                structlog.threadlocal.as_immutable(self.logger)
                immutable_logger = structlog.threadlocal.as_immutable(self.logger)
                context = immutable_logger._context
                self.assertDictEqual({'foo': 'bar'}, context)

                middleware.receiver_task_pre_run(task_id, None, None, kwargs=task_kwargs)
                immutable_logger = structlog.threadlocal.as_immutable(self.logger)
                context = immutable_logger._context

        self.assertDictEqual({
            'task_id': task_id,
            'request_id': expected_request_uuid,
            'user_id': expected_user_id,
        }, context)

    def test_receiver_task_retry(self):
        expected_reason = 'foo'

        with middlewares.CeleryMiddleware() as middleware:
            with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.WARNING) as log_results:
                middleware.receiver_task_retry(reason=expected_reason)

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task retry', record.msg['event'])
        self.assertEqual('WARNING', record.levelname)
        self.assertIn('reason', record.msg)
        self.assertEqual(expected_reason, record.msg['reason'])

    def test_receiver_task_success(self):
        expected_result = 'foo'

        with middlewares.CeleryMiddleware() as middleware:
            with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.INFO) as log_results:
                middleware.receiver_task_success(result=expected_result)

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task success', record.msg['event'])
        self.assertEqual('INFO', record.levelname)
        self.assertIn('result', record.msg)
        self.assertEqual(expected_result, record.msg['result'])

    def test_receiver_task_failure(self):
        expected_exception = 'foo'

        with middlewares.CeleryMiddleware() as middleware:
            with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.ERROR) as log_results:
                middleware.receiver_task_failure(exception=Exception('foo'))

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task failure', record.msg['event'])
        self.assertEqual('ERROR', record.levelname)
        self.assertIn('error', record.msg)
        self.assertEqual(expected_exception, record.msg['error'])

    def test_receiver_task_revoked(self):
        with middlewares.CeleryMiddleware() as middleware:
            with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.WARNING) as log_results:
                middleware.receiver_task_revoked(terminated=True, signum=1, expired=False)

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task revoked', record.msg['event'])
        self.assertEqual('WARNING', record.levelname)
        self.assertIn('terminated', record.msg)
        self.assertTrue(record.msg['terminated'])
        self.assertIn('signum', record.msg)
        self.assertEqual(1, record.msg['signum'])
        self.assertIn('expired', record.msg)
        self.assertFalse(record.msg['expired'])

    def test_receiver_task_unknown(self):
        expected_message = 'foo'

        with middlewares.CeleryMiddleware() as middleware:
            with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.ERROR) as log_results:
                middleware.receiver_task_unknown(message=expected_message)

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task unknown', record.msg['event'])
        self.assertEqual('ERROR', record.levelname)
        self.assertIn('message', record.msg)
        self.assertEqual(expected_message, record.msg['message'])

    def test_receiver_task_rejected(self):
        expected_message = 'foo'

        with middlewares.CeleryMiddleware() as middleware:
            with self.assertLogs(logging.getLogger('django_structlog.middlewares.celery'), logging.ERROR) as log_results:
                middleware.receiver_task_rejected(message=expected_message)

        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertEqual('Task rejected', record.msg['event'])
        self.assertEqual('ERROR', record.levelname)
        self.assertIn('message', record.msg)
        self.assertEqual(expected_message, record.msg['message'])

    def tearDown(self):
        self.logger.new()
