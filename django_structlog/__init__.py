""" ``django-structlog`` is a structured logging integration for ``Django`` project using ``structlog``.
"""


default_app_config = 'django_structlog.apps.DjangoStructLogConfig'
name = "django_structlog"

VERSION = (1, 1, 6)

__version__ = ".".join(str(v) for v in VERSION)
