.. _configuration:

Configuration
=============

In your ``settings.py`` you can customize ``django-structlog``.

Example:

.. code-block:: python

    import logging
    DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL = logging.INFO


Settings
--------

+------------------------------------------+---------+-----------------+-------------------------------+
| Key                                      | Type    | Default         | Description                   |
+==========================================+=========+=================+===============================+
| DJANGO_STRUCTLOG_CELERY_ENABLED          | boolean | False           | See :ref:`celery_integration` |
+------------------------------------------+---------+-----------------+-------------------------------+
| DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL    | int     | logging.WARNING | Log level of 4XX status codes |
+------------------------------------------+---------+-----------------+-------------------------------+
| DJANGO_STRUCTLOG_COMMAND_LOGGING_ENABLED | boolean | False           | See :ref:`commands`           |
+------------------------------------------+---------+-----------------+-------------------------------+
