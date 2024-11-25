from django.test import TestCase

from django_structlog import app_settings


class TestAppSettings(TestCase):
    def test_celery_enabled(self) -> None:
        settings = app_settings.AppSettings()

        with self.settings(DJANGO_STRUCTLOG_CELERY_ENABLED=True):
            self.assertTrue(settings.CELERY_ENABLED)

    def test_celery_disabled(self) -> None:
        settings = app_settings.AppSettings()

        with self.settings(DJANGO_STRUCTLOG_CELERY_ENABLED=False):
            self.assertFalse(settings.CELERY_ENABLED)
