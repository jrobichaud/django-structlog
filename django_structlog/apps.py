from django.apps import AppConfig

from .app_settings import app_settings


class DjangoStructLogConfig(AppConfig):
    name = "django_structlog"

    def ready(self):
        if app_settings.CELERY_ENABLED:
            from .celery.receivers import connect_celery_signals

            connect_celery_signals()
