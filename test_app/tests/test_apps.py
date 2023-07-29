from unittest.mock import patch

from django.test import TestCase

from django_structlog import apps


class TestAppConfig(TestCase):
    def test_celery_enabled(self):
        app = apps.DjangoStructLogConfig(
            "django_structlog", __import__("django_structlog")
        )
        with patch(
            "django_structlog.celery.receivers.connect_celery_signals"
        ) as mock_connect_celery_signals:
            with self.settings(DJANGO_STRUCTLOG_CELERY_ENABLED=True):
                app.ready()
        mock_connect_celery_signals.assert_called_once()

    def test_celery_disabled(self):
        app = apps.DjangoStructLogConfig(
            "django_structlog", __import__("django_structlog")
        )
        with patch(
            "django_structlog.celery.receivers.connect_celery_signals"
        ) as mock_connect_celery_signals:
            with self.settings(DJANGO_STRUCTLOG_CELERY_ENABLED=False):
                app.ready()
        mock_connect_celery_signals.assert_not_called()
