Celery Integration
==================

Getting Started with Celery
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to be able to support celery you need to configure both your webapp and your workers

Add CeleryMiddleWare in your web app
------------------------------------

In your settings.py

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'django_structlog.middlewares.RequestMiddleware',
        'django_structlog.middlewares.CeleryMiddleware',
    ]


Initialize Celery Worker with DjangoStructLogInitStep
-----------------------------------------------------

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
-------------------------

In the same file as before

.. code-block:: python

    @setup_logging.connect
    def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # pragma: no cover
        logging.config.dictConfig(
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

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.filter_by_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


.. _celery_signals:

Signals
^^^^^^^
modify_context_before_task_publish
----------------------------------

You can connect to ``modify_context_before_task_publish`` signal in order to modify the metadata before it is stored in the task's message.

By example you can strip down the ``context`` to keep only some of the keys:

.. code-block:: python

    @receiver(signals.modify_context_before_task_publish)
    def receiver_modify_context_before_task_publish(sender, signal, context):
        keys_to_keep = {"request_id", "parent_task_id"}
        new_dict = {key_to_keep: context[key_to_keep] for key_to_keep in keys_to_keep if key_to_keep in context}
        context.clear()
        context.update(new_dict)


bind_extra_task_metadata
------------------------

You can optionally connect to ``bind_extra_task_metadata`` signal in order to bind more metadata to the logger or override existing bound metadata. This is called
in celery's ``receiver_task_pre_run``.

.. code-block:: python

    from django_structlog.celery import signals
    import structlog

    @receiver(signals.bind_extra_task_metadata)
    def receiver_bind_extra_request_metadata(sender, signal, task=None, logger=None):
        structlog.contextvars.bind_contextvars(correlation_id=task.request.correlation_id)

