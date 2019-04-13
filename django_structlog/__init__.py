from django.utils.version import get_version

default_app_config = 'django_structlog.apps.DjangoStructLogConfig'
name = "django_structlog"

VERSION = (1, 0, 1, 'final', 0)

__version__ = get_version(VERSION)
