from unittest.mock import patch, call

from django.test import TestCase

from django_structlog.celery import steps


class TestDjangoStructLogInitStep(TestCase):
    def test_call(self):
        from celery.signals import (
            before_task_publish,
            after_task_publish,
            task_prerun,
            task_retry,
            task_success,
            task_failure,
            task_revoked,
            task_unknown,
            task_rejected,
        )
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

        with patch(
            "celery.utils.dispatch.signal.Signal.connect", autospec=True
        ) as mock_connect:
            steps.DjangoStructLogInitStep(None)

        mock_connect.assert_has_calls(
            [
                call(before_task_publish, receiver_before_task_publish),
                call(after_task_publish, receiver_after_task_publish),
                call(task_prerun, receiver_task_pre_run),
                call(task_retry, receiver_task_retry),
                call(task_success, receiver_task_success),
                call(task_failure, receiver_task_failure),
                call(task_revoked, receiver_task_revoked),
                call(task_unknown, receiver_task_unknown),
                call(task_rejected, receiver_task_rejected),
            ]
        )
