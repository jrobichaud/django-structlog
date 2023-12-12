from unittest.mock import patch, create_autospec

from django.test import TestCase

from django_structlog import apps, commands
from django_structlog.celery import receivers


class TestAppConfig(TestCase):
    def test_celery_enabled(self):
        app = apps.DjangoStructLogConfig(
            "django_structlog", __import__("django_structlog")
        )
        mock_receiver = create_autospec(spec=receivers.CeleryReceiver)
        with patch(
            "django_structlog.celery.receivers.CeleryReceiver",
            return_value=mock_receiver,
        ):
            with self.settings(DJANGO_STRUCTLOG_CELERY_ENABLED=True):
                app.ready()
        mock_receiver.connect_signals.assert_called_once()

        self.assertTrue(hasattr(app, "_celery_receiver"))
        self.assertIsNotNone(app._celery_receiver)

    def test_celery_disabled(self):
        app = apps.DjangoStructLogConfig(
            "django_structlog", __import__("django_structlog")
        )

        mock_receiver = create_autospec(spec=receivers.CeleryReceiver)
        with patch(
            "django_structlog.celery.receivers.CeleryReceiver",
            return_value=mock_receiver,
        ):
            with self.settings(DJANGO_STRUCTLOG_CELERY_ENABLED=False):
                app.ready()
        mock_receiver.connect_signals.assert_not_called()

        self.assertFalse(hasattr(app, "_celery_receiver"))

    def test_command_enabled(self):
        app = apps.DjangoStructLogConfig(
            "django_structlog", __import__("django_structlog")
        )
        mock_receiver = create_autospec(spec=commands.DjangoCommandReceiver)
        with patch(
            "django_structlog.commands.DjangoCommandReceiver",
            return_value=mock_receiver,
        ):
            with self.settings(DJANGO_STRUCTLOG_COMMAND_LOGGING_ENABLED=True):
                app.ready()
        mock_receiver.connect_signals.assert_called_once()

        self.assertTrue(hasattr(app, "_django_command_receiver"))
        self.assertIsNotNone(app._django_command_receiver)

    def test_command_disabled(self):
        app = apps.DjangoStructLogConfig(
            "django_structlog", __import__("django_structlog")
        )

        mock_receiver = create_autospec(spec=commands.DjangoCommandReceiver)
        with patch(
            "django_structlog.commands.DjangoCommandReceiver",
            return_value=mock_receiver,
        ):
            with self.settings(DJANGO_STRUCTLOG_COMMAND_LOGGING_ENABLED=False):
                app.ready()
        mock_receiver.connect_signals.assert_not_called()

        self.assertFalse(hasattr(app, "_django_command_receiver"))
