import logging

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

    def test_request_cancelled_log_level_default(self) -> None:
        settings = app_settings.AppSettings()
        self.assertEqual(settings.REQUEST_CANCELLED_LOG_LEVEL, logging.WARNING)

    def test_request_cancelled_log_level_custom(self) -> None:
        settings = app_settings.AppSettings()

        with self.settings(DJANGO_STRUCTLOG_REQUEST_CANCELLED_LOG_LEVEL=logging.DEBUG):
            self.assertEqual(settings.REQUEST_CANCELLED_LOG_LEVEL, logging.DEBUG)

    def test_status_5xx_log_level_default(self) -> None:
        settings = app_settings.AppSettings()
        self.assertEqual(settings.STATUS_5XX_LOG_LEVEL, logging.ERROR)

    def test_status_5xx_log_level_custom(self) -> None:
        settings = app_settings.AppSettings()

        with self.settings(DJANGO_STRUCTLOG_STATUS_5XX_LOG_LEVEL=logging.CRITICAL):
            self.assertEqual(settings.STATUS_5XX_LOG_LEVEL, logging.CRITICAL)
