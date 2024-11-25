import logging
from signal import SIGTERM
from typing import Any, Optional, Type
from unittest.mock import Mock, patch, call, MagicMock

import structlog
from celery import shared_task
from django.contrib.auth.models import AnonymousUser
from django.dispatch import receiver as django_receiver
from django.test import TestCase, RequestFactory

from django_structlog.celery import receivers, signals


class TestReceivers(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.logger = structlog.getLogger(__name__)

    def tearDown(self) -> None:
        structlog.contextvars.clear_contextvars()

    def test_defer_task(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        @shared_task  # type: ignore[misc,unused-ignore]
        def test_task(value: Any) -> None:  # pragma: no cover
            pass

        receiver = receivers.CeleryReceiver()
        receiver.connect_signals()
        structlog.contextvars.bind_contextvars(request_id=expected_uuid)
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.INFO
        ) as log_results:
            test_task.delay("foo")
        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_enqueued", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertIn("child_task_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])

    def test_receiver_before_task_publish_celery_protocol_v2(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"
        expected_user_id = "1234"
        expected_parent_task_uuid = "11111111-1111-1111-1111-111111111111"

        headers: dict[str, Any] = {}
        structlog.contextvars.bind_contextvars(
            request_id=expected_uuid,
            user_id=expected_user_id,
            task_id=expected_parent_task_uuid,
        )
        receiver = receivers.CeleryReceiver()
        receiver.receiver_before_task_publish(headers=headers)

        self.assertDictEqual(
            {
                "__django_structlog__": {
                    "request_id": expected_uuid,
                    "user_id": expected_user_id,
                    "parent_task_id": expected_parent_task_uuid,
                }
            },
            headers,
        )

    def test_receiver_before_task_publish_celery_protocol_v1(self) -> None:
        """Protocol v1 does not allow to store metadata"""
        expected_uuid = "00000000-0000-0000-0000-000000000000"
        expected_user_id = "1234"
        expected_parent_task_uuid = "11111111-1111-1111-1111-111111111111"

        headers: dict[str, Any] = {}
        structlog.contextvars.bind_contextvars(
            request_id=expected_uuid,
            user_id=expected_user_id,
            task_id=expected_parent_task_uuid,
        )
        mock_current_app = MagicMock()
        mock_conf = MagicMock()
        mock_current_app.conf = mock_conf
        mock_conf.task_protocol = 1
        receiver = receivers.CeleryReceiver()
        with patch("django_structlog.celery.receivers.current_app", mock_current_app):
            receiver.receiver_before_task_publish(headers=headers)

        self.assertDictEqual(
            {},
            headers,
        )

    def test_signal_modify_context_before_task_publish_celery_protocol_v2(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"
        user_id = "1234"
        expected_parent_task_uuid = "11111111-1111-1111-1111-111111111111"
        routing_key = "foo"
        properties: dict[str, Optional[str]] = {
            "correlation_id": "22222222-2222-2222-2222-222222222222"
        }

        received_properties: Any = None
        received_routing_key: Any = None

        @django_receiver(signals.modify_context_before_task_publish)  # type: ignore[misc,unused-ignore]
        def receiver_modify_context_before_task_publish(
            sender: Type[Any],
            signal: Any,
            context: Any,
            task_properties: Any,
            task_routing_key: str,
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
            nonlocal received_properties
            received_properties = task_properties
            nonlocal received_routing_key
            received_routing_key = task_routing_key

        headers: dict[str, Any] = {}
        structlog.contextvars.bind_contextvars(
            request_id=expected_uuid,
            user_id=user_id,
            task_id=expected_parent_task_uuid,
        )
        receiver = receivers.CeleryReceiver()
        receiver.receiver_before_task_publish(
            headers=headers,
            routing_key=routing_key,
            properties=properties,
        )

        self.assertDictEqual(
            {
                "__django_structlog__": {
                    "request_id": expected_uuid,
                    "parent_task_id": expected_parent_task_uuid,
                }
            },
            headers,
            "Only `request_id` and `parent_task_id` are preserved",
        )
        self.assertDictEqual(
            {"correlation_id": "22222222-2222-2222-2222-222222222222"},
            received_properties,
        )
        self.assertEqual("foo", received_routing_key)

    def test_receiver_after_task_publish(self) -> None:
        expected_task_id = "00000000-0000-0000-0000-000000000000"
        expected_task_name = "Foo"
        headers: dict[str, Any] = {"id": expected_task_id, "task": expected_task_name}
        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_after_task_publish(headers=headers)

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_enqueued", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertIn("child_task_id", record.msg)
        self.assertEqual(expected_task_id, record.msg["child_task_id"])
        self.assertIn("child_task_name", record.msg)
        self.assertEqual(expected_task_name, record.msg["child_task_name"])

    def test_receiver_after_task_publish_protocol_v1(self) -> None:
        expected_task_id = "00000000-0000-0000-0000-000000000000"
        expected_task_name = "Foo"
        body: dict[str, Any] = {"id": expected_task_id, "task": expected_task_name}

        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_after_task_publish(body=body)

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_enqueued", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertIn("child_task_id", record.msg)
        self.assertEqual(expected_task_id, record.msg["child_task_id"])
        self.assertIn("child_task_name", record.msg)
        self.assertEqual(expected_task_name, record.msg["child_task_name"])

    def test_receiver_task_pre_run(self) -> None:
        expected_request_uuid = "00000000-0000-0000-0000-000000000000"
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_user_id = "1234"
        task = Mock()
        task.request = Mock()
        task.request.__django_structlog__ = {
            "request_id": expected_request_uuid,
            "user_id": expected_user_id,
        }
        task.name = "task_name"
        structlog.contextvars.bind_contextvars(foo="bar")

        context = structlog.contextvars.get_merged_contextvars(self.logger)
        self.assertDictEqual({"foo": "bar"}, context)
        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_prerun(task_id, task)
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
        self.assertIn("task", record.msg)
        self.assertEqual("task_name", record.msg["task"])

    def test_signal_bind_extra_task_metadata(self) -> None:
        @django_receiver(signals.bind_extra_task_metadata)  # type: ignore[misc,unused-ignore]
        def receiver_bind_extra_request_metadata(
            sender: Type[Any], signal: Any, task: Any = None, logger: Any = None
        ) -> None:
            structlog.contextvars.bind_contextvars(
                correlation_id=task.request.correlation_id
            )

        expected_correlation_uuid = "00000000-0000-0000-0000-000000000000"
        task_id = "11111111-1111-1111-1111-111111111111"
        task = Mock()
        task.request = Mock()
        task.request.correlation_id = expected_correlation_uuid
        structlog.contextvars.bind_contextvars(foo="bar")

        context = structlog.contextvars.get_merged_contextvars(self.logger)
        self.assertDictEqual({"foo": "bar"}, context)
        receiver = receivers.CeleryReceiver()
        receiver.receiver_task_prerun(task_id, task)
        context = structlog.contextvars.get_merged_contextvars(self.logger)

        self.assertEqual(context["correlation_id"], expected_correlation_uuid)
        self.assertEqual(context["task_id"], task_id)

    def test_receiver_task_retry(self) -> None:
        expected_reason = "foo"

        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.WARNING
        ) as log_results:
            receiver.receiver_task_retry(reason=expected_reason)

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_retrying", record.msg["event"])
        self.assertEqual("WARNING", record.levelname)
        self.assertIn("reason", record.msg)
        self.assertEqual(expected_reason, record.msg["reason"])

    def test_receiver_task_success(self) -> None:
        expected_result = "foo"

        @django_receiver(signals.pre_task_succeeded)  # type: ignore[misc,unused-ignore]
        def receiver_pre_task_succeeded(
            sender: Type[Any],
            signal: Any,
            task: Any = None,
            logger: Any = None,
            result: Any = None,
        ) -> None:
            structlog.contextvars.bind_contextvars(result=result)

        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_success(result=expected_result)

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_succeeded", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertIn("result", record.msg)
        self.assertEqual(expected_result, record.msg["result"])

    def test_receiver_task_failure(self) -> None:
        expected_exception = "foo"
        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.ERROR
        ) as log_results:
            receiver.receiver_task_failure(exception=Exception("foo"))

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_failed", record.msg["event"])
        self.assertEqual("ERROR", record.levelname)
        self.assertIn("error", record.msg)
        self.assertIn("exception", record.msg)
        self.assertEqual(expected_exception, record.msg["error"])

    def test_receiver_task_failure_with_throws(self) -> None:
        expected_exception = "foo"

        mock_sender = Mock()
        mock_sender.throws = (Exception,)
        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_task_failure(
                exception=Exception("foo"), sender=mock_sender
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_failed", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertIn("error", record.msg)
        self.assertNotIn("exception", record.msg)
        self.assertEqual(expected_exception, record.msg["error"])

    def test_receiver_task_revoked(self) -> None:
        expected_request_uuid = "00000000-0000-0000-0000-000000000000"
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_user_id = "1234"
        expected_task_name = "task_name"
        request = Mock()
        request.__django_structlog__ = {
            "request_id": expected_request_uuid,
            "user_id": expected_user_id,
        }
        request.task = expected_task_name
        request.id = task_id

        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.WARNING
        ) as log_results:
            receiver.receiver_task_revoked(
                request=request, terminated=False, signum=None, expired=False
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_revoked", record.msg["event"])
        self.assertEqual("WARNING", record.levelname)
        self.assertIn("terminated", record.msg)
        self.assertFalse(record.msg["terminated"])
        self.assertIn("signum", record.msg)
        self.assertIsNone(record.msg["signum"])
        self.assertIn("signame", record.msg)
        self.assertIsNone(record.msg["signame"])
        self.assertIn("expired", record.msg)
        self.assertFalse(record.msg["expired"])
        self.assertIn("task_id", record.msg)
        self.assertEqual(task_id, record.msg["task_id"])
        self.assertIn("task", record.msg)
        self.assertEqual(expected_task_name, record.msg["task"])
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_request_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(expected_user_id, record.msg["user_id"])

    def test_receiver_task_revoked_terminated(self) -> None:
        expected_request_uuid = "00000000-0000-0000-0000-000000000000"
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_user_id = "1234"
        expected_task_name = "task_name"
        request = Mock()
        request.__django_structlog__ = {
            "request_id": expected_request_uuid,
            "user_id": expected_user_id,
        }
        request.task = expected_task_name
        request.id = task_id

        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.WARNING
        ) as log_results:
            receiver.receiver_task_revoked(
                request=request, terminated=True, signum=SIGTERM, expired=False
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_revoked", record.msg["event"])
        self.assertEqual("WARNING", record.levelname)
        self.assertIn("terminated", record.msg)
        self.assertTrue(record.msg["terminated"])
        self.assertIn("signum", record.msg)
        self.assertEqual(15, record.msg["signum"])
        self.assertIn("signame", record.msg)
        self.assertEqual("SIGTERM", record.msg["signame"])
        self.assertIn("expired", record.msg)
        self.assertFalse(record.msg["expired"])
        self.assertIn("task_id", record.msg)
        self.assertEqual(task_id, record.msg["task_id"])
        self.assertIn("task", record.msg)
        self.assertEqual(expected_task_name, record.msg["task"])
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_request_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(expected_user_id, record.msg["user_id"])

    def test_receiver_task_unknown(self) -> None:
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_task_name = "task_name"

        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.ERROR
        ) as log_results:
            receiver.receiver_task_unknown(id=task_id, name=expected_task_name)

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_not_found", record.msg["event"])
        self.assertEqual("ERROR", record.levelname)
        self.assertIn("task_id", record.msg)
        self.assertEqual(task_id, record.msg["task_id"])
        self.assertIn("task", record.msg)
        self.assertEqual(expected_task_name, record.msg["task"])

    def test_receiver_task_rejected(self) -> None:
        task_id = "11111111-1111-1111-1111-111111111111"
        message = Mock(name="message")
        message.properties = dict(correlation_id=task_id)

        receiver = receivers.CeleryReceiver()
        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.ERROR
        ) as log_results:
            receiver.receiver_task_rejected(message=message)

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_rejected", record.msg["event"])
        self.assertEqual("ERROR", record.levelname)
        self.assertIn("task_id", record.msg)
        self.assertEqual(task_id, record.msg["task_id"])

    def test_priority(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"
        user_id = "1234"
        expected_parent_task_uuid = "11111111-1111-1111-1111-111111111111"
        expected_routing_key = "foo"
        expected_priority = 6
        properties = {"priority": expected_priority}

        headers: dict[str, Any] = {}
        structlog.contextvars.bind_contextvars(
            request_id=expected_uuid,
            user_id=user_id,
            task_id=expected_parent_task_uuid,
        )
        receiver = receivers.CeleryReceiver()
        receiver.receiver_before_task_publish(
            headers=headers,
            routing_key=expected_routing_key,
            properties=properties,
        )

        self.assertDictEqual(
            {
                "__django_structlog__": {
                    "user_id": user_id,
                    "request_id": expected_uuid,
                    "parent_task_id": expected_parent_task_uuid,
                }
            },
            headers,
            "Only `request_id` and `parent_task_id` are preserved",
        )

        expected_task_id = "00000000-0000-0000-0000-000000000000"
        expected_task_name = "Foo"
        headers = {"id": expected_task_id, "task": expected_task_name}

        with self.assertLogs(
            logging.getLogger("django_structlog.celery.receivers"), logging.INFO
        ) as log_results:
            receiver.receiver_after_task_publish(
                headers=headers, routing_key=expected_routing_key
            )

        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("task_enqueued", record.msg["event"])
        self.assertEqual("INFO", record.levelname)
        self.assertIn("child_task_id", record.msg)
        self.assertEqual(expected_task_id, record.msg["child_task_id"])
        self.assertIn("child_task_name", record.msg)
        self.assertEqual(expected_task_name, record.msg["child_task_name"])

        self.assertIn("priority", record.msg)
        self.assertEqual(expected_priority, record.msg["priority"])

        self.assertIn("routing_key", record.msg)
        self.assertEqual(expected_routing_key, record.msg["routing_key"])


class TestConnectCeleryTaskSignals(TestCase):
    def test_call(self) -> None:
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

        from django_structlog.celery.receivers import CeleryReceiver

        receiver = CeleryReceiver()
        with patch(
            "celery.utils.dispatch.signal.Signal.connect", autospec=True
        ) as mock_connect:
            receiver.connect_worker_signals()

        mock_connect.assert_has_calls(
            [
                call(before_task_publish, receiver.receiver_before_task_publish),
                call(after_task_publish, receiver.receiver_after_task_publish),
                call(task_prerun, receiver.receiver_task_prerun),
                call(task_retry, receiver.receiver_task_retry),
                call(task_success, receiver.receiver_task_success),
                call(task_failure, receiver.receiver_task_failure),
                call(task_revoked, receiver.receiver_task_revoked),
                call(task_unknown, receiver.receiver_task_unknown),
                call(task_rejected, receiver.receiver_task_rejected),
            ]
        )


class TestConnectCelerySignals(TestCase):
    def test_call(self) -> None:
        from celery.signals import before_task_publish, after_task_publish
        from django_structlog.celery.receivers import CeleryReceiver

        receiver = CeleryReceiver()
        with patch(
            "celery.utils.dispatch.signal.Signal.connect", autospec=True
        ) as mock_connect:
            receiver.connect_signals()

        mock_connect.assert_has_calls(
            [
                call(before_task_publish, receiver.receiver_before_task_publish),
                call(after_task_publish, receiver.receiver_after_task_publish),
            ]
        )
