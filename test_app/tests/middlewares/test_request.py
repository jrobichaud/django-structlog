import logging
import traceback
import uuid
from unittest import mock
from unittest.mock import patch, Mock

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.http import Http404, HttpResponseNotFound, HttpResponseForbidden
from django.test import TestCase, RequestFactory
import structlog

from django_structlog import middlewares
from django_structlog.middlewares.request import get_request_header
from django_structlog.signals import (
    bind_extra_request_metadata,
    bind_extra_request_finished_metadata,
    bind_extra_request_failed_metadata,
)


class TestRequestMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.logger = structlog.getLogger(__name__)
        self.log_results = None
        self.exception_traceback = None

    def tearDown(self):
        structlog.contextvars.clear_contextvars()

    def test_process_request_without_user(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        middleware = middlewares.RequestMiddleware(get_response)
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

    def test_process_request_with_null_user(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")
        request.user = None

        middleware = middlewares.RequestMiddleware(get_response)
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

    def test_process_request_anonymous(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        middleware = middlewares.RequestMiddleware(get_response)
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

    def test_process_request_user(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        mock_user = User.objects.create()
        request.user = mock_user

        middleware = middlewares.RequestMiddleware(get_response)
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

    def test_process_request_user_uuid(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        mock_user = mock.Mock()
        mock_user.pk = uuid.UUID(expected_uuid)
        request.user = mock_user

        middleware = middlewares.RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("user_id", record.msg)
        self.assertIsInstance(record.msg["user_id"], str)
        self.assertEqual(expected_uuid, record.msg["user_id"])

    def test_log_user_in_request_finished(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        mock_user = User.objects.create()

        request = self.factory.get("/foo")

        def get_response(_response):
            request.user = mock_user
            return mock_response

        middleware = middlewares.RequestMiddleware(get_response)
        with patch("uuid.UUID.__str__", return_value=expected_uuid), self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
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

    def test_log_user_in_request_finished_with_exception(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        mock_user = User.objects.create()

        request = self.factory.get("/foo")

        middleware = middlewares.RequestMiddleware(None)
        exception = Exception()

        def get_response(_response):
            request.user = mock_user
            try:
                raise exception
            except Exception as e:
                middleware.process_exception(request, e)
                self.exception_traceback = traceback.format_exc()
            return mock_response

        middleware.get_response = get_response

        with patch("uuid.UUID.__str__", return_value=expected_uuid), self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
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

    def test_signal_bind_extra_request_metadata(self):
        @receiver(bind_extra_request_metadata)
        def receiver_bind_extra_request_metadata(
            sender, signal, request=None, logger=None
        ):
            structlog.contextvars.bind_contextvars(
                user_email=getattr(request.user, "email", "")
            )

        mock_response = Mock()
        mock_response.status_code.return_value = 200

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = self.factory.get("/foo")

        mock_user = User.objects.create(email="foo@example.com")
        request.user = mock_user

        middleware = middlewares.RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertEqual(mock_user.email, record.msg["user_email"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])

    def test_signal_bind_extra_request_finished_metadata(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200

        @receiver(bind_extra_request_finished_metadata)
        def receiver_bind_extra_request_metadata(
            sender, signal, request=None, logger=None, response=None
        ):
            self.assertEqual(response, mock_response)
            structlog.contextvars.bind_contextvars(
                user_email=getattr(request.user, "email", "")
            )

        def get_response(_response):
            return mock_response

        request = self.factory.get("/foo")

        mock_user = User.objects.create(email="foo@example.com")
        request.user = mock_user

        middleware = middlewares.RequestMiddleware(get_response)

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record = log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_started", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_email", record.msg)
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])
        record = log_results.records[1]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_finished", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertIn("user_email", record.msg)
        self.assertEqual(mock_user.email, record.msg["user_email"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])

    def test_signal_bind_extra_request_failed_metadata(self):
        expected_exception = Exception()

        @receiver(bind_extra_request_failed_metadata)
        def receiver_bind_extra_request_metadata(
            sender, signal, request=None, logger=None, exception=None
        ):
            self.assertEqual(exception, expected_exception)
            structlog.contextvars.bind_contextvars(
                user_email=getattr(request.user, "email", "")
            )

        request = self.factory.get("/foo")

        mock_user = User.objects.create(email="foo@example.com")

        request.user = mock_user
        middleware = middlewares.RequestMiddleware(None)

        mock_response = Mock()

        def get_response(_response):
            middleware.process_exception(request, expected_exception)
            return mock_response

        middleware.get_response = get_response

        with self.assertLogs(
            "django_structlog.middlewares.request", logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
        record = log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_started", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_email", record.msg)
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])
        record = log_results.records[1]

        self.assertEqual("ERROR", record.levelname)
        self.assertIn("event", record.msg)
        self.assertEqual("request_failed", record.msg["event"])
        self.assertIn("request_id", record.msg)
        self.assertIn("user_email", record.msg)
        self.assertEqual(mock_user.email, record.msg["user_email"])
        self.assertIn("user_id", record.msg)
        self.assertEqual(mock_user.id, record.msg["user_id"])

    def test_process_request_error(self):
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        middleware = middlewares.RequestMiddleware(None)

        exception = Exception("This is an exception")

        def get_response(_response):
            """Simulate an exception"""
            try:
                raise exception
            except Exception as e:
                middleware.process_exception(request, e)
                self.exception_traceback = traceback.format_exc()

        middleware.get_response = get_response

        with patch("uuid.UUID.__str__", return_value=expected_uuid), self.assertLogs(
            logging.getLogger("django_structlog"), logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
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

    def test_process_request_403_are_processed_as_regular_requests(self):
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        middleware = middlewares.RequestMiddleware(None)

        exception = PermissionDenied()

        def get_response(_response):
            """Simulate an exception"""
            middleware.process_exception(request, exception)
            return HttpResponseForbidden()

        middleware.get_response = get_response

        with patch("uuid.UUID.__str__", return_value=expected_uuid), self.assertLogs(
            logging.getLogger("django_structlog"), logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
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
        self.assertEqual(record.msg["code"], 403)
        self.assertNotIn("exception", record.msg)
        self.assertIn("request", record.msg)

        with self.assertLogs(__name__, logging.INFO) as log_results:
            self.logger.info("hello")
        self.assertEqual(1, len(log_results.records))
        record = log_results.records[0]
        self.assertNotIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)

    def test_process_request_404_are_processed_as_regular_requests(self):
        expected_uuid = "00000000-0000-0000-0000-000000000000"

        request = self.factory.get("/foo")
        request.user = AnonymousUser()

        middleware = middlewares.RequestMiddleware(None)

        exception = Http404()

        def get_response(_response):
            """Simulate an exception"""
            middleware.process_exception(request, exception)
            return HttpResponseNotFound()

        middleware.get_response = get_response

        with patch("uuid.UUID.__str__", return_value=expected_uuid), self.assertLogs(
            logging.getLogger("django_structlog"), logging.INFO
        ) as log_results:
            middleware(request)

        self.assertEqual(2, len(log_results.records))
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

    def test_should_log_request_id_from_request_x_request_id_header(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        x_request_id = "my-fake-request-id"

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = RequestFactory(HTTP_X_REQUEST_ID=x_request_id).get("/foo")

        middleware = middlewares.RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertEqual(x_request_id, record.msg["request_id"])

    def test_should_log_correlation_id_from_request_x_correlation_id_header(self):
        mock_response = Mock()
        mock_response.status_code.return_value = 200
        x_correlation_id = "my-fake-correlation-id"

        def get_response(_response):
            with self.assertLogs(__name__, logging.INFO) as log_results:
                self.logger.info("hello")
            self.log_results = log_results
            return mock_response

        request = RequestFactory(HTTP_X_CORRELATION_ID=x_correlation_id).get("/foo")

        middleware = middlewares.RequestMiddleware(get_response)
        middleware(request)

        self.assertEqual(1, len(self.log_results.records))
        record = self.log_results.records[0]

        self.assertEqual("INFO", record.levelname)
        self.assertIn("request_id", record.msg)
        self.assertNotIn("user_id", record.msg)
        self.assertEqual(x_correlation_id, record.msg["correlation_id"])


class TestGetRequestHeader(TestCase):
    def test_django_22_or_higher(self):
        mock_request = mock.MagicMock(spec=["headers"])
        get_request_header(mock_request, "x-foo-bar", "HTTP_X_FOO_BAR")
        mock_request.headers.get.assert_called_once_with("x-foo-bar")

    def test_django_prior_to_22(self):
        mock_request = mock.MagicMock(spec=["META"])
        get_request_header(mock_request, "x-foo-bar", "HTTP_X_FOO_BAR")
        mock_request.META.get.assert_called_once_with("HTTP_X_FOO_BAR")
