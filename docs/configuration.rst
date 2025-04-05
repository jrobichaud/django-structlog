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

+------------------------------------------+---------+-----------------+-------------------------------------------------------------------------------+
| Key                                      | Type    | Default         | Description                                                                   |
+==========================================+=========+=================+===============================================================================+
| DJANGO_STRUCTLOG_CELERY_ENABLED          | boolean | False           | See :ref:`celery_integration`                                                 |
+------------------------------------------+---------+-----------------+-------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_IP_LOGGING_ENABLED      | boolean | True            | automatically bind user ip using `django-ipware`                              |
+------------------------------------------+---------+-----------------+-------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL    | int     | logging.WARNING | Log level of 4XX status codes                                                 |
+------------------------------------------+---------+-----------------+-------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_COMMAND_LOGGING_ENABLED | boolean | False           | See :ref:`commands`                                                           |
+------------------------------------------+---------+-----------------+-------------------------------------------------------------------------------+
| DJANGO_STRUCTLOG_USER_ID_FIELD           | boolean | ``"pk"``        | Change field used to identify user in logs, ``None`` to disable user binding  |
+------------------------------------------+---------+-----------------+-------------------------------------------------------------------------------+
