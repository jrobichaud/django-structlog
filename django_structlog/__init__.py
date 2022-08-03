""" ``django-structlog`` is a structured logging integration for ``Django`` project using ``structlog``.
"""


default_app_config = "django_structlog.apps.DjangoStructLogConfig"
name = "django_structlog"

VERSION = (3, 0, 1)

__version__ = ".".join(str(v) for v in VERSION)
