.. _configuration:

Configuration
=============

In your ``settings.py`` you can customize ``django-structlog``.

Example:

.. code-block:: python

    import logging
    DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL = logging.INFO


.. _settings:

Settings
--------

+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| Key                                              | Type    | Default         | Description                                                                  |
+==================================================+=========+=================+==============================================================================+
| DJANGO_STRUCTLOG_CELERY_ENABLED                  | boolean | False           | See :ref:`celery_integration`                                                |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_CELERY_DEFAULT_LOG_LEVEL        | int     | logging.INFO    | The default log level for celery task events                                 |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_CELERY_TASK_START_LOG_LEVEL     | int     | logging.INFO    | Log level for task_enqueued and task_started events                          |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_CELERY_TASK_SUCCESS_LOG_LEVEL   | int     | logging.INFO    | Log level for task_succeeded events                                          |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_CELERY_TASK_NOTICE_LOG_LEVEL    | int     | logging.WARNING | Log level for task_retrying and task_revoked events                          |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_CELERY_TASK_FAILURE_LOG_LEVEL   | int     | logging.INFO    | Log level for task_failed                                                    |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_CELERY_TASK_ERROR_LOG_LEVEL     | int     | logging.ERROR   | Log level for true errors using Celery                                       |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_IP_LOGGING_ENABLED              | boolean | True            | automatically bind user ip using `django-ipware`                             |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_DEFAULT_LOG_LEVEL               | int     | logging.INFO    | The default log level for non-error statuses                                 |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_START_LOG_LEVEL                 | int     | logging.INFO    | The level at which request starts are logged                                 |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_STATUS_2XX_LOG_LEVEL            | int     | logging.INFO    | The level of 2XX status codes                                                |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL            | int     | logging.WARNING | Log level of 4XX status codes                                                |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_STATUS_5XX_LOG_LEVEL            | int     | logging.ERROR   | Log level of 5XX status codes                                                |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_REQUEST_CANCELLED_LOG_LEVEL     | int     | logging.WARNING | Log level of request_cancelled messages                                      |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_COMMAND_LOGGING_ENABLED         | boolean | False           | See :ref:`commands`                                                          |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_USER_ID_FIELD                   | string  | ``"pk"``        | Change field used to identify user in logs, ``None`` to disable user binding |
+--------------------------------------------------+---------+-----------------+------------------------------------------------------------------------------+
