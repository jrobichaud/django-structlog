from unittest.mock import Mock, patch, call
from django.test import TestCase

from django_structlog import middlewares


class TestCeleryMiddleware(TestCase):

    def test_call(self):
        from django_structlog.celery.receivers import receiver_before_task_publish, receiver_after_task_publish
        mock_get_response = Mock()
        mock_request = Mock()
        with patch('celery.utils.dispatch.signal.Signal.connect') as mock_connect:
            middleware = middlewares.CeleryMiddleware(mock_get_response)

        middleware(mock_request)
        mock_get_response.assert_called_once_with(mock_request)
        mock_connect.assert_has_calls(
            [
                call(receiver_before_task_publish),
                call(receiver_after_task_publish),
            ]
        )

