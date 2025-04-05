import logging

from django.conf import settings


# noinspection PyPep8Naming
class AppSettings:
    PREFIX = "DJANGO_STRUCTLOG_"

    @property
    def CELERY_ENABLED(self) -> bool:
        return getattr(settings, self.PREFIX + "CELERY_ENABLED", False)

    @property
    def IP_LOGGING_ENABLED(self) -> bool:
        return getattr(settings, self.PREFIX + "IP_LOGGING_ENABLED", True)

    @property
    def STATUS_4XX_LOG_LEVEL(self) -> int:
        return getattr(settings, self.PREFIX + "STATUS_4XX_LOG_LEVEL", logging.WARNING)

    @property
    def COMMAND_LOGGING_ENABLED(self) -> bool:
        return getattr(settings, self.PREFIX + "COMMAND_LOGGING_ENABLED", False)

    @property
    def USER_ID_FIELD(self) -> str:
        return getattr(settings, self.PREFIX + "USER_ID_FIELD", "pk")


app_settings = AppSettings()
