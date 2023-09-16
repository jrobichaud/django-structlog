import logging

from django.conf import settings


# noinspection PyPep8Naming
class AppSettings:
    PREFIX = "DJANGO_STRUCTLOG_"

    @property
    def CELERY_ENABLED(self):
        return getattr(settings, self.PREFIX + "CELERY_ENABLED", False)

    @property
    def STATUS_4XX_LOG_LEVEL(self):
        return getattr(settings, self.PREFIX + "STATUS_4XX_LOG_LEVEL", logging.WARNING)

    @property
    def COMMAND_LOGGING_ENABLED(self):
        return getattr(settings, self.PREFIX + "COMMAND_LOGGING_ENABLED", False)


app_settings = AppSettings()
