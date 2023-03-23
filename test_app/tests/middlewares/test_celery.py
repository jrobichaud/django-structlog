from unittest.mock import Mock, patch, call
from django.test import TestCase

from django_structlog import middlewares


class TestCeleryMiddleware(TestCase):
    def test_call(self):
        from celery.signals import before_task_publish, after_task_publish
        from django_structlog.celery.receivers import (
            receiver_before_task_publish,
            receiver_after_task_publish,
        )

        mock_request = Mock()
        mock_response = Mock()

        def get_response(request):
            return mock_response

        with patch(
            "celery.utils.dispatch.signal.Signal.connect", autospec=True
        ) as mock_connect:
            middleware = middlewares.CeleryMiddleware(get_response)

        response = middleware(mock_request)
        self.assertEqual(mock_response, response)

        mock_connect.assert_has_calls(
            [
                call(before_task_publish, receiver_before_task_publish),
                call(after_task_publish, receiver_after_task_publish),
            ]
        )

    async def test_async(self):
        from celery.signals import before_task_publish, after_task_publish
        from django_structlog.celery.receivers import (
            receiver_before_task_publish,
            receiver_after_task_publish,
        )

        mock_request = Mock()
        mock_response = Mock()

        async def get_response(request):
            return mock_response

        with patch(
            "celery.utils.dispatch.signal.Signal.connect", autospec=True
        ) as mock_connect:
            middleware = middlewares.CeleryMiddleware(get_response)

        response = await middleware(mock_request)
        self.assertEqual(mock_response, response)
        mock_connect.assert_has_calls(
            [
                call(before_task_publish, receiver_before_task_publish),
                call(after_task_publish, receiver_after_task_publish),
            ]
        )
