import asyncio
import logging
import traceback
import uuid
from typing import Any, AsyncGenerator, Awaitable, Generator, Type, cast
from unittest import mock
from unittest.mock import AsyncMock, Mock, patch

import structlog
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.signals import got_request_exception
from django.dispatch import receiver
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
    StreamingHttpResponse,
)
from django.test import RequestFactory, TestCase, override_settings

from django_structlog.middlewares.request import (
    RequestMiddleware,
    async_streaming_content_wrapper,
    get_request_header,
    sync_streaming_content_wrapper,
)
from django_structlog.signals import (
    bind_extra_request_failed_metadata,
    bind_extra_request_finished_metadata,
    bind_extra_request_metadata,
)


class TestRequestMiddleware(TestCase):
    log_results: Any

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.logger = structlog.getLogger(__name__)
        self.log_results = None
        Site.objects.update_or_create(
            id=1,
            defaults={"domain": "testserver", "name": "django_structlog_demo_project"},
        )

    def tearDown(self) -> None:
        structlog.contextvars.clear_contextvars()

    def test_process_request_without_user(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        middleware = RequestMiddleware(get_response)
        with patch("uuid.UUID.__str__", return_value=expected_uuid):
            middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)

    def test_process_request_with_null_user(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")
        setattr(request, "user", None)

        middleware = RequestMiddleware(get_response)
        with patch("uuid.UUID.__str__", return_value=expected_uuid):
            middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)

    def test_process_request_anonymous(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        middleware = RequestMiddleware(get_response)
        with patch("uuid.UUID.__str__", return_value=expected_uuid):
            middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])
        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)

    def test_process_request_user(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        mock_user: Any = User.objects.create()
        request.user = mock_user

        middleware = RequestMiddleware(get_response)
        with patch("uuid.UUID.__str__", return_value=expected_uuid):
            middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsInstance(record.msg["user_id"], int)
        self.assertEqual(mock_user.id, record.msg["user_id"])
        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)

    def test_process_request_user_uuid(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        mock_user: Any = mock.Mock()
        mock_user.pk = uuid.UUID(expected_uuid)
        request.user = mock_user

        middleware = RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("user_id", record.msg)
        self.assertIsInstance(record.msg["user_id"], str)
        self.assertEqual(expected_uuid, record.msg["user_id"])

    def test_process_request_user_without_id(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        class SimpleUser:
            pass

        request.user = cast(Any, SimpleUser())
        middleware = RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

    def test_log_user_in_request_finished(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        mock_user: Any = User.objects.create()

        request = self.factory.get("/foo")

        def get_response(_request: HttpRequest) -> HttpResponse:
            request.user = mock_user
            return mock_response

        middleware = RequestMiddleware(get_response)
        with (
            patch("uuid.UUID.__str__", return_value=expected_uuid),
            self.assertLogs(
                "django_structlog.middlewares.request", logging.INFO
            ) as log_results,
        ):
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertEqual("request_started", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertNotIn("user_id", record.msg)

        record = log_results.records[1]

        self.assertEqual("INFO", record.levelname)
        self.assertEqual("request_finished", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])

    def test_log_user_in_request_finished_with_exception(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        mock_user: Any = User.objects.create()

        request = self.factory.get("/foo")

        def get_response(_request: HttpRequest) -> HttpResponse:
            request.user = mock_user
            try:
                raise exception
            except Exception:
                got_request_exception.send(object, request=request)
                self.exception_traceback = traceback.format_exc()
            return mock_response

        middleware = RequestMiddleware(get_response)
        exception = Exception()

        middleware.get_response = get_response

        with (
            patch("uuid.UUID.__str__", return_value=expected_uuid),
            self.assertLogs(
                "django_structlog.middlewares.request", logging.INFO
            ) as log_results,
        ):
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertEqual("request_started", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertNotIn("user_id", record.msg)

        record = log_results.records[1]

        self.assertEqual("ERROR", record.levelname)
        self.assertEqual("request_failed", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("exception", record.msg)
        self.assertEqual(self.exception_traceback.strip(), record.msg["exception"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])

    def test_signal_bind_extra_request_metadata(self) -> None:
        @receiver(bind_extra_request_metadata)
        def receiver_bind_extra_request_metadata(
            sender: Type[Any],
            signal: Any,
            request: Any = None,
            logger: Any = None,
            log_kwargs: Any = None,
            **kwargs: Any,
        ) -> None:
            current_site = get_current_site(request)
            log_kwargs["request_started_log"] = "foo"
            structlog.contextvars.bind_contextvars(domain=current_site.domain)

        mock_response = Mock()
        mock_response.status_code = 200

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        mock_user: Any = User.objects.create(email="foo@example.com")
        request.user = mock_user

        middleware = RequestMiddleware(get_response)

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as django_structlog_results:
            middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual("testserver", record.msg["domain"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])

        self.assertEqual(2, len(django_structlog_results.records))
        record = django_structlog_results.records[0]
        self.assertEqual("request_started", record.msg["event"])
        self.assertEqual("foo", record.msg["request_started_log"])

        record = django_structlog_results.records[1]
        self.assertEqual("request_finished", record.msg["event"])
        self.assertNotIn("request_started_log", record.msg)

    def test_signal_bind_extra_request_finished_metadata(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200

        @receiver(bind_extra_request_finished_metadata)
        def receiver_bind_extra_request_finished_metadata(
            sender: Type[Any],
            signal: Any,
            request: Any = None,
            logger: Any = None,
            response: Any = None,
            log_kwargs: Any = None,
        ) -> None:
            self.assertEqual(response, mock_response)
            current_site = get_current_site(request)
            log_kwargs["request_finished_log"] = "foo"
            structlog.contextvars.bind_contextvars(domain=current_site.domain)

        def get_response(_request: HttpRequest) -> HttpResponse:
            return mock_response

        request = self.factory.get("/foo")

        mock_user: Any = User.objects.create(email="foo@example.com")
        request.user = mock_user

        middleware = RequestMiddleware(get_response)

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_started", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertNotIn("domain", record.msg)
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])
        record = log_results.records[1]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_finished", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertIn("domain", record.msg)
        self.assertEqual("testserver", record.msg["domain"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])
        self.assertIn("request_finished_log", record.msg)
        self.assertEqual("foo", record.msg["request_finished_log"])

    def test_signal_bind_extra_request_failed_metadata(self) -> None:
        expected_exception = Exception()

        @receiver(bind_extra_request_failed_metadata)
        def receiver_bind_extra_request_failed_metadata(
            sender: Type[Any],
            signal: Any,
            request: Any = None,
            response: Any = None,
            logger: Any = None,
            exception: Any = None,
            log_kwargs: Any = None,
        ) -> None:
            self.assertEqual(exception, expected_exception)
            current_site = get_current_site(request)
            log_kwargs["request_failed_log"] = "foo"
            structlog.contextvars.bind_contextvars(domain=current_site.domain)

        request = self.factory.get("/foo")

        mock_user: Any = User.objects.create(email="foo@example.com")

        request.user = mock_user

        def get_response(_request: HttpRequest) -> HttpResponse:
            try:
                raise expected_exception
            except Exception:
                got_request_exception.send(object, request=request)
            return mock_response

        middleware = RequestMiddleware(get_response)

        mock_response = Mock()

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))

        record: Any
        record = log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_started", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertNotIn("domain", record.msg)
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])
        record = log_results.records[1]

        self.assertEqual("ERROR", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_failed", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertIn("domain", record.msg)
        self.assertEqual("testserver", record.msg["domain"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])
        self.assertIn("request_failed_log", record.msg)
        self.assertEqual("foo", record.msg["request_failed_log"])

    def test_process_request_error(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        def get_response(_request: HttpRequest) -> Any:
            """Simulate an exception"""
            try:
                raise exception
            except Exception:
                got_request_exception.send(object, request=request)
                self.exception_traceback = traceback.format_exc()

        middleware = RequestMiddleware(get_response)

        exception = Exception("This is an exception")

        with (
            patch("uuid.UUID.__str__", return_value=expected_uuid),
            self.assertLogs(
                logging.getLogger("django_structlog"), logging.INFO
            ) as log_results,
        ):
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        record = log_results.records[1]
        self.assertEqual("ERROR", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        self.assertIn("code", record.msg)
        self.assertEqual(record.msg["code"], 500)
        self.assertIn("exception", record.msg)
        self.assertEqual(self.exception_traceback.strip(), record.msg["exception"])
        self.assertIn("request", record.msg)

        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertFalse(hasattr(request, "_raised_exception"))

    def test_process_request_403_are_processed_as_regular_requests(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        def get_response(_request: HttpRequest) -> HttpResponse:
            try:
                raise exception
            except Exception:
                got_request_exception.send(object, request=request)
            return HttpResponseForbidden()

        middleware = RequestMiddleware(get_response)

        exception = PermissionDenied()

        with (
            patch("uuid.UUID.__str__", return_value=expected_uuid),
            self.assertLogs(
                logging.getLogger("django_structlog"), logging.INFO
            ) as log_results,
        ):
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        record = log_results.records[1]
        self.assertEqual("WARNING", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        self.assertIn("code", record.msg)
        self.assertEqual(record.msg["code"], 403)
        self.assertNotIn("exception", record.msg)
        self.assertIn("request", record.msg)

        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertFalse(hasattr(request, "_raised_exception"))

    def test_process_request_404_are_processed_as_regular_requests(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        def get_response(_request: HttpRequest) -> HttpResponse:
            try:
                raise exception
            except Exception:
                got_request_exception.send(object, request=request)
            return HttpResponseNotFound()

        middleware = RequestMiddleware(get_response)

        exception = Http404()

        with (
            patch("uuid.UUID.__str__", return_value=expected_uuid),
            self.assertLogs(
                logging.getLogger("django_structlog"), logging.INFO
            ) as log_results,
        ):
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        record = log_results.records[1]
        self.assertEqual("WARNING", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        self.assertIn("code", record.msg)
        self.assertEqual(record.msg["code"], 404)
        self.assertNotIn("exception", record.msg)
        self.assertIn("request", record.msg)

        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertFalse(hasattr(request, "_raised_exception"))

    @override_settings(DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL=logging.INFO)
    def test_process_request_4XX_can_be_personalized(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        def get_response(_request: HttpRequest) -> HttpResponse:
            try:
                raise exception
            except Exception:
                got_request_exception.send(object, request=request)
            return HttpResponseNotFound()

        middleware = RequestMiddleware(get_response)

        exception = Http404()

        with (
            patch("uuid.UUID.__str__", return_value=expected_uuid),
            self.assertLogs(
                logging.getLogger("django_structlog"), logging.INFO
            ) as log_results,
        ):
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        record = log_results.records[1]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        self.assertIn("code", record.msg)
        self.assertEqual(record.msg["code"], 404)
        self.assertNotIn("exception", record.msg)
        self.assertIn("request", record.msg)

        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertFalse(hasattr(request, "_raised_exception"))

    def test_process_request_500_are_processed_as_errors(self) -> None:
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        def get_response(_request: HttpRequest) -> HttpResponse:
            return HttpResponseServerError()

        middleware = RequestMiddleware(get_response)

        with (
            patch("uuid.UUID.__str__", return_value=expected_uuid),
            self.assertLogs(
                logging.getLogger("django_structlog"), logging.INFO
            ) as log_results,
        ):
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        record = log_results.records[1]
        self.assertEqual("ERROR", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(expected_uuid, record.msg["request_id"])
        self.assertIn("user_id", record.msg)
        self.assertIsNone(record.msg["user_id"])

        self.assertIn("code", record.msg)
        self.assertEqual(record.msg["code"], 500)
        self.assertNotIn("exception", record.msg)
        self.assertIn("request", record.msg)

        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertFalse(hasattr(request, "_raised_exception"))

    def test_should_log_request_id_from_request_x_request_id_header(self) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        x_request_id = "my-fake-request-id"

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = RequestFactory(HTTP_X_REQUEST_ID=x_request_id).get("/foo")

        middleware = RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record: Any
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertEqual(x_request_id, record.msg["request_id"])

    def test_should_log_correlation_id_from_request_x_correlation_id_header(
        self,
    ) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        x_correlation_id = "my-fake-correlation-id"

        def get_response(_request: HttpRequest) -> HttpResponse:
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = RequestFactory(HTTP_X_CORRELATION_ID=x_correlation_id).get("/foo")

        middleware = RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record: Any
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertEqual(x_correlation_id, record.msg["correlation_id"])

    def test_sync_streaming_response(self) -> None:
        def streaming_content() -> Generator[Any, None, None]:  # pragma: no cover
            yield

        mock_response = mock.create_autospec(StreamingHttpResponse)
        mock_response.streaming_content = streaming_content()
        mock_response.is_async = False
        mock_response.status_code = 200

        def get_response(_request: HttpRequest) -> Any:
            return mock_response

        request = RequestFactory().get("/foo")

        middleware = RequestMiddleware(get_response)

        mock_wrapper = AsyncMock()
        with patch(
            "django_structlog.middlewares.request.sync_streaming_content_wrapper",
            return_value=mock_wrapper,
        ) as mock_sync_streaming_response_wrapper:
            response: Any = middleware(request)

        mock_sync_streaming_response_wrapper.assert_called_once()
        self.assertEqual(response.streaming_content, mock_wrapper)

    def test_async_streaming_response(self) -> None:
        async def streaming_content() -> AsyncGenerator[Any, None]:  # pragma: no cover
            yield

        mock_response = mock.create_autospec(StreamingHttpResponse)
        mock_response.streaming_content = streaming_content()
        mock_response.is_async = True
        mock_response.status_code = 200

        def get_response(_request: HttpRequest) -> Any:
            return mock_response

        request = RequestFactory().get("/foo")

        middleware = RequestMiddleware(get_response)

        mock_wrapper = AsyncMock()
        with patch(
            "django_structlog.middlewares.request.async_streaming_content_wrapper",
            return_value=mock_wrapper,
        ) as mock_sync_streaming_response_wrapper:
            response: Any = middleware(request)

        mock_sync_streaming_response_wrapper.assert_called_once()
        self.assertEqual(response.streaming_content, mock_wrapper)

    async def test_async_cancel(self) -> None:
        async def async_get_response(request: HttpRequest) -> Any:
            raise asyncio.CancelledError

        middleware = RequestMiddleware(async_get_response)

        mock_request = Mock()
        with (
            patch(
                "django_structlog.middlewares.RequestMiddleware.prepare"
            ) as mock_prepare,
            patch(
                "django_structlog.middlewares.RequestMiddleware.handle_response"
            ) as mock_handle_response,
            self.assertLogs(
                "django_structlog.middlewares.request", logging.WARNING
            ) as log_results,
        ):
            with self.assertRaises(asyncio.CancelledError):
                await cast(Awaitable[HttpResponse], middleware(mock_request))
        mock_prepare.assert_called_once_with(mock_request)
        mock_handle_response.assert_not_called()
        self.assertEqual(1, len(log_results.records))
        record: Any = log_results.records[0]
        self.assertEqual("request_cancelled", record.msg["event"])


class TestRequestMiddlewareRouter(TestCase):
    async def test_async(self) -> None:
        mock_response = Mock()

        async def async_get_response(request: HttpRequest) -> Any:
            return mock_response

        middleware = RequestMiddleware(async_get_response)

        mock_request = Mock()
        with (
            patch(
                "django_structlog.middlewares.RequestMiddleware.prepare"
            ) as mock_prepare,
            patch(
                "django_structlog.middlewares.RequestMiddleware.handle_response"
            ) as mock_handle_response,
        ):
            response = await cast(Awaitable[HttpResponse], middleware(mock_request))
        self.assertEqual(response, mock_response)
        mock_prepare.assert_called_once_with(mock_request)
        mock_handle_response.assert_called_once_with(mock_request, mock_response)

    def test_sync(self) -> None:
        mock_response = Mock()

        def get_response(request: HttpRequest) -> HttpResponse:
            return mock_response

        middleware = RequestMiddleware(get_response)

        mock_request = Mock()
        with (
            patch(
                "django_structlog.middlewares.RequestMiddleware.prepare"
            ) as mock_prepare,
            patch(
                "django_structlog.middlewares.RequestMiddleware.handle_response"
            ) as mock_handle_response,
        ):
            response = middleware(mock_request)
        self.assertEqual(response, mock_response)
        mock_prepare.assert_called_once_with(mock_request)
        mock_handle_response.assert_called_once_with(mock_request, mock_response)


class TestGetRequestHeader(TestCase):
    def test_django_22_or_higher(self) -> None:
        mock_request = mock.MagicMock(spec=["headers"])
        get_request_header(mock_request, "x-foo-bar", "HTTP_X_FOO_BAR")
        mock_request.headers.get.assert_called_once_with("x-foo-bar")

    def test_django_prior_to_22(self) -> None:
        mock_request = mock.MagicMock(spec=["META"])
        get_request_header(mock_request, "x-foo-bar", "HTTP_X_FOO_BAR")
        mock_request.META.get.assert_called_once_with("HTTP_X_FOO_BAR")


class TestSyncStreamingContentWrapper(TestCase):
    def setUp(self) -> None:
        self.logger = structlog.getLogger(__name__)

    def test_success(self) -> None:
        result = Mock()

        def streaming_content() -> Generator[Any, None, None]:
            self.logger.info("streaming_content")
            yield result

        wrapped_streaming_content = sync_streaming_content_wrapper(
            streaming_content(), {"foo": "bar"}
        )
        with (
            self.assertLogs(__name__, logging.INFO) as streaming_content_log_results,
            self.assertLogs(
                "django_structlog.middlewares.request", logging.INFO
            ) as log_results,
        ):
            self.assertEqual(result, next(wrapped_streaming_content))

        self.assertEqual(1, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertEqual("streaming_started", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            self.assertRaises(StopIteration, next, wrapped_streaming_content)

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = streaming_content_log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertEqual("streaming_finished", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

    def test_failure(self) -> None:
        result = Mock()

        class CustomException(Exception):
            pass

        exception = CustomException()

        def streaming_content() -> Generator[Any, None, None]:
            self.logger.info("streaming_content")
            yield result
            raise exception

        wrapped_streaming_content = sync_streaming_content_wrapper(
            streaming_content(), {"foo": "bar"}
        )
        with (
            self.assertLogs(__name__, logging.INFO) as streaming_content_log_results,
            self.assertLogs(
                "django_structlog.middlewares.request", logging.INFO
            ) as log_results,
        ):
            self.assertEqual(result, next(wrapped_streaming_content))

        self.assertEqual(1, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertEqual("streaming_started", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            self.assertRaises(CustomException, next, wrapped_streaming_content)

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = streaming_content_log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = log_results.records[0]
        self.assertEqual("ERROR", record.levelname)
        self.assertEqual("streaming_failed", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])


class TestASyncStreamingContentWrapper(TestCase):
    def setUp(self) -> None:
        self.logger = structlog.getLogger(__name__)

    async def test_success(self) -> None:
        result = Mock()

        async def streaming_content() -> AsyncGenerator[Any, None]:
            self.logger.info("streaming_content")
            yield result

        wrapped_streaming_content = async_streaming_content_wrapper(
            streaming_content(), {"foo": "bar"}
        )
        with (
            self.assertLogs(__name__, logging.INFO) as streaming_content_log_results,
            self.assertLogs(
                "django_structlog.middlewares.request", logging.INFO
            ) as log_results,
        ):
            self.assertEqual(result, await wrapped_streaming_content.__anext__())

        self.assertEqual(1, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertEqual("streaming_started", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            with self.assertRaises(StopAsyncIteration):
                await wrapped_streaming_content.__anext__()

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = streaming_content_log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertEqual("streaming_finished", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

    async def test_failure(self) -> None:
        result = Mock()

        class CustomException(Exception):
            pass

        exception = CustomException()

        async def streaming_content() -> AsyncGenerator[Any, None]:
            self.logger.info("streaming_content")
            yield result
            raise exception

        wrapped_streaming_content = async_streaming_content_wrapper(
            streaming_content(), {"foo": "bar"}
        )
        with (
            self.assertLogs(__name__, logging.INFO) as streaming_content_log_results,
            self.assertLogs(
                "django_structlog.middlewares.request", logging.INFO
            ) as log_results,
        ):
            self.assertEqual(result, await wrapped_streaming_content.__anext__())

        self.assertEqual(1, len(log_results.records))
        record: Any
        record = log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertEqual("streaming_started", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            with self.assertRaises(CustomException):
                await wrapped_streaming_content.__anext__()

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = streaming_content_log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = log_results.records[0]
        self.assertEqual("ERROR", record.levelname)
        self.assertEqual("streaming_failed", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

    async def test_cancel(self) -> None:
        result = Mock()

        exception = asyncio.CancelledError()

        async def streaming_content() -> AsyncGenerator[Any, None]:
            self.logger.info("streaming_content")
            yield result
            raise exception

        wrapped_streaming_content = async_streaming_content_wrapper(
            streaming_content(), {"foo": "bar"}
        )
        with self.assertLogs(__name__, logging.INFO) as streaming_content_log_results:
            self.assertEqual(result, await wrapped_streaming_content.__anext__())
        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            with self.assertRaises(asyncio.CancelledError):
                await wrapped_streaming_content.__anext__()

        self.assertEqual(1, len(streaming_content_log_results.records))
        record: Any
        record = streaming_content_log_results.records[0]
        self.assertEqual("INFO", record.levelname)
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])

        self.assertEqual(1, len(streaming_content_log_results.records))
        record = log_results.records[0]
        self.assertEqual("WARNING", record.levelname)
        self.assertEqual("streaming_cancelled", record.msg["event"])
        self.assertIn("foo", record.msg)
        self.assertEqual("bar", record.msg["foo"])
