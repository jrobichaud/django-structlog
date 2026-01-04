import logging
import unittest
from typing import Any, Type
from unittest.mock import Mock, call, patch

import django
import structlog
from django.core.cache import caches
from django.dispatch import receiver as django_receiver
from django.test import TestCase

from django_structlog.tasks import receivers, signals

if django.VERSION >= (6, 0):
    from django.tasks.base import (  # type: ignore[import-untyped]
        TaskResult,
        TaskResultStatus,
    )


@unittest.skipIf(django.VERSION < (6, 0), "Django 6.0+ required for native tasks")
class TestReceivers(TestCase):
    def setUp(self) -> None:
        self.logger = structlog.getLogger(__name__)
        self.cache = caches["django_structlog"]

    def tearDown(self) -> None:
        structlog.contextvars.clear_contextvars()
        self.cache.clear()

    def test_receiver_task_enqueued(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"
        expected_task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"

        structlog.contextvars.bind_contextvars(request_id=expected_uuid)

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = expected_task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.tasks.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_enqueued(
                sender=mock_sender, task_result=mock_task_result
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_enqueued", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertEqual(expected_task_id, record.msg["task_id"])
        self.assertEqual(expected_task_name, record.msg["task_name"])

        cached_context = self.cache.get(expected_task_id)
        self.assertIsNotNone(cached_context)
        self.assertEqual(expected_uuid, cached_context["request_id"])

    def test_signal_modify_context_before_task_publish(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"
        user_id = "1234"
        expected_parent_task_uuid = "11111111-1111-1111-1111-111111111111"
        expected_task_id = "22222222-2222-2222-2222-222222222222"
        expected_task_name = "test_app.tasks.test_task"

        @django_receiver(signals.modify_context_before_task_publish)
        def receiver_modify_context_before_task_publish(
            sender: Type[Any],
            signal: Any,
            context: Any,
            **kwargs: Any,
        ) -> None:
            keys_to_keep = {"request_id", "parent_task_id"}
            new_dict = {
                key_to_keep: context[key_to_keep]
                for key_to_keep in keys_to_keep
                if key_to_keep in context
            }
            context.clear()
            context.update(new_dict)

        structlog.contextvars.bind_contextvars(
            request_id=expected_uuid,
            user_id=user_id,
            task_id=expected_parent_task_uuid,
        )

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = expected_task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        receiver.receiver_task_enqueued(
            sender=mock_sender, task_result=mock_task_result
        )

        cached_context = self.cache.get(expected_task_id)
        self.assertIsNotNone(cached_context)
        self.assertEqual(expected_uuid, cached_context["request_id"])
        self.assertEqual(expected_parent_task_uuid, cached_context["parent_task_id"])
        self.assertNotIn("user_id", cached_context)

    def test_receiver_task_started(self) -> None:
        expected_request_uuid = "00000000-0000-0000-0000-000000000000"
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_user_id = "1234"
        expected_task_name = "test_app.tasks.test_task"

        self.cache.set(
            task_id,
            {
                "request_id": expected_request_uuid,
                "user_id": expected_user_id,
            },
        )

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name

        structlog.contextvars.bind_contextvars(foo="bar")
        context = structlog.contextvars.get_merged_contextvars(self.logger)
        self.assertDictEqual({"foo": "bar"}, context)

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.tasks.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_started(
                sender=mock_sender, task_result=mock_task_result
            )

        context = structlog.contextvars.get_merged_contextvars(self.logger)
        self.assertDictEqual(
            {
                "task_id": task_id,
                "request_id": expected_request_uuid,
                "user_id": expected_user_id,
            },
            context,
        )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_started", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertEqual(expected_task_name, record.msg["task"])

    def test_signal_bind_extra_task_metadata(self) -> None:
        @django_receiver(signals.bind_extra_task_metadata)
        def receiver_bind_extra_task_metadata(
            sender: Type[Any], signal: Any, task_result: Any = None, logger: Any = None
        ) -> None:
            structlog.contextvars.bind_contextvars(
                custom_field=task_result.custom_field
            )

        expected_custom_value = "custom_value"
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"

        self.cache.set(task_id, {})

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name
        mock_task_result.custom_field = expected_custom_value

        structlog.contextvars.bind_contextvars(foo="bar")
        context = structlog.contextvars.get_merged_contextvars(self.logger)
        self.assertDictEqual({"foo": "bar"}, context)

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        receiver.receiver_task_started(sender=mock_sender, task_result=mock_task_result)
        context = structlog.contextvars.get_merged_contextvars(self.logger)

        self.assertEqual(context["custom_field"], expected_custom_value)
        self.assertEqual(context["task_id"], task_id)

    def test_receiver_task_finished_success(self) -> None:
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name
        mock_task_result.status = TaskResultStatus.SUCCESSFUL

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.tasks.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_finished(
                sender=mock_sender, task_result=mock_task_result
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_succeeded", record.msg["event"])
        self.assertEqual("INFO", record.levelname)

    def test_signal_pre_task_succeeded(self) -> None:
        expected_result_value = "result_value"

        @django_receiver(signals.pre_task_succeeded)
        def receiver_pre_task_succeeded(
            sender: Type[Any],
            signal: Any,
            task_result: Any = None,
            logger: Any = None,
        ) -> None:
            structlog.contextvars.bind_contextvars(result=task_result.return_value)

        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name
        mock_task_result.status = TaskResultStatus.SUCCESSFUL
        mock_task_result.return_value = expected_result_value

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.tasks.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_finished(
                sender=mock_sender, task_result=mock_task_result
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_succeeded", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertIn("result", record.msg)
        self.assertEqual(expected_result_value, record.msg["result"])

    def test_receiver_task_finished_failed(self) -> None:
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"
        expected_exception_class = "builtins.ValueError"
        expected_traceback = (
            "Traceback (most recent call last):\n  File...\nValueError: test error"
        )

        mock_error = Mock()
        mock_error.exception_class_path = expected_exception_class
        mock_error.traceback = expected_traceback

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name
        mock_task_result.status = TaskResultStatus.FAILED
        mock_task_result.errors = [mock_error]

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.tasks.receivers"), logging.ERROR
        ) as log_results:
            receiver.receiver_task_finished(
                sender=mock_sender, task_result=mock_task_result
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_failed", record.msg["event"])
        self.assertEqual("ERROR", record.levelname)
        self.assertIn("exception_class", record.msg)
        self.assertEqual(expected_exception_class, record.msg["exception_class"])
        self.assertIn("traceback", record.msg)
        self.assertEqual(expected_traceback, record.msg["traceback"])

    def test_receiver_task_started_no_cached_context(self) -> None:
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name

        structlog.contextvars.bind_contextvars(foo="bar")

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.tasks.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_started(
                sender=mock_sender, task_result=mock_task_result
            )

        context = structlog.contextvars.get_merged_contextvars(self.logger)
        self.assertDictEqual({"task_id": task_id}, context)

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_started", record.msg["event"])

    def test_receiver_task_finished_other_status(self) -> None:
        """Test that no logging occurs for task status other than SUCCESSFUL or FAILED."""
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name
        mock_task_result.status = TaskResultStatus.RUNNING

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()

        # No logs should be produced for RUNNING status
        with self.assertRaises(AssertionError):
            with self.assertLogs(
                logging.getLogger("django_structlog.tasks.receivers"), logging.INFO
            ):
                receiver.receiver_task_finished(
                    sender=mock_sender, task_result=mock_task_result
                )

    def test_receiver_task_finished_failed_empty_errors(self) -> None:
        """Test task failure with empty errors list."""
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "test_app.tasks.test_task"

        mock_task_result = Mock(spec=TaskResult)
        mock_task_result.id = task_id
        mock_task_result.task = Mock()
        mock_task_result.task.module_path = expected_task_name
        mock_task_result.status = TaskResultStatus.FAILED
        mock_task_result.errors = []

        mock_sender = Mock()
        receiver = receivers.DjangoTaskReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.tasks.receivers"), logging.ERROR
        ) as log_results:
            receiver.receiver_task_finished(
                sender=mock_sender, task_result=mock_task_result
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_failed", record.msg["event"])
        self.assertEqual("ERROR", record.levelname)
        # Should not have exception_class or traceback when errors list is empty
        self.assertNotIn("exception_class", record.msg)
        self.assertNotIn("traceback", record.msg)


@unittest.skipIf(django.VERSION < (6, 0), "Django 6.0+ required for native tasks")
class TestConnectDjangoTaskSignals(TestCase):
    def test_call(self) -> None:
        from django.tasks.signals import (  # type: ignore[import-untyped]
            task_enqueued,
            task_finished,
            task_started,
        )

        from django_structlog.tasks.receivers import DjangoTaskReceiver

        receiver = DjangoTaskReceiver()
        with patch(
            "django.dispatch.dispatcher.Signal.connect", autospec=True
        ) as mock_connect:
            receiver.connect_signals()

        mock_connect.assert_has_calls(
            [
                call(task_started, receiver.receiver_task_started),
                call(task_finished, receiver.receiver_task_finished),
                call(task_enqueued, receiver.receiver_task_enqueued),
            ]
        )
