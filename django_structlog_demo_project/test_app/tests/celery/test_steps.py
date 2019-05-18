from unittest.mock import Mock, patch, call

from django.test import TestCase

from django_structlog.celery import steps


class TestDjangoStructLogInitStep(TestCase):
    def test_call(self):
        from django_structlog.celery.receivers import (
            receiver_before_task_publish,
            receiver_after_task_publish,
            receiver_task_pre_run,
            receiver_task_retry,
            receiver_task_success,
            receiver_task_failure,
            receiver_task_revoked,
            receiver_task_unknown,
            receiver_task_rejected,
        )

        with patch("celery.utils.dispatch.signal.Signal.connect") as mock_connect:
            steps.DjangoStructLogInitStep(None)

        mock_connect.assert_has_calls(
            [
                call(receiver_before_task_publish),
                call(receiver_after_task_publish),
                call(receiver_task_pre_run),
                call(receiver_task_retry),
                call(receiver_task_success),
                call(receiver_task_failure),
                call(receiver_task_revoked),
                call(receiver_task_unknown),
                call(receiver_task_rejected),
            ]
        )
