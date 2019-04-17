Celery Integration
==================

In order to be able to support celery you need to configure both your webapp and your workers

Add CeleryMiddleWare in your web app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In your settings.py

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'django_structlog.middlewares.RequestMiddleware',
        'django_structlog.middlewares.CeleryMiddleware',
    ]


Initialize Celery Worker with DjangoStructLogInitStep
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In your celery AppConfig's module.

.. code-block:: python

    import logging

    import structlog
    from celery import Celery
    from celery.signals import setup_logging
    from django_structlog.celery.steps import DjangoStructLogInitStep

    app = Celery("your_celery_project")

    # A step to initialize django-structlog
    app.steps['worker'].add(DjangoStructLogInitStep)


Configure celery's logger
^^^^^^^^^^^^^^^^^^^^^^^^^

In the same file as before

.. code-block:: python

    @setup_logging.connect
    def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # pragma: no cover
        logging.basicConfig(
            {
               "version": 1,
               "disable_existing_loggers": False,
               "formatters": {
                   "json_formatter": {
                       "()": structlog.stdlib.ProcessorFormatter,
                       "processor": structlog.processors.JSONRenderer(),
                   },
                   "plain_console": {
                       "()": structlog.stdlib.ProcessorFormatter,
                       "processor": structlog.dev.ConsoleRenderer(),
                   },
                   "key_value": {
                       "()": structlog.stdlib.ProcessorFormatter,
                       "processor": structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event', 'logger']),
                   },
               },
               "handlers": {
                   "console": {
                       "class": "logging.StreamHandler",
                       "formatter": "plain_console",
                   },
                   "json_file": {
                       "class": "logging.handlers.WatchedFileHandler",
                       "filename": "logs/json.log",
                       "formatter": "json_formatter",
                   },
                   "flat_line_file": {
                       "class": "logging.handlers.WatchedFileHandler",
                       "filename": "logs/flat_line.log",
                       "formatter": "key_value",
                   },
               },
               "loggers": {
                   "django_structlog": {
                       "handlers": ["console", "flat_line_file", "json_file"],
                       "level": "INFO",
                   },
                   "django_structlog_demo_project": {
                       "handlers": ["console", "flat_line_file", "json_file"],
                       "level": "INFO",
                   },
               }
           }
        )

        # Same as in the example
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.ExceptionPrettyPrinter(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=structlog.threadlocal.wrap_dict(dict),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
