Events and Metadata
===================

Django's RequestMiddleware
--------------------------

.. _request_events:

Request Events
^^^^^^^^^^^^^^

+-------------------+--------------------+-----------------------------------------------------+
| Event             | Type               | Description                                         |
+===================+====================+=====================================================+
| request_started   | INFO               | Django received a request                           |
+-------------------+--------------------+-----------------------------------------------------+
| request_finished  | INFO/WARNING/ERROR | request completed with status (2XX or 3XX)/4XX/5XX  |
+-------------------+--------------------+-----------------------------------------------------+
| request_cancelled | WARNING            | request cancelled during an async request with asgi |
+-------------------+--------------------+-----------------------------------------------------+
| request_failed    | ERROR              | unhandled exception occurred                        |
+-------------------+--------------------+-----------------------------------------------------+

.. _streaming_response_events:

StreamingHttpResponse Events
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specific to `StreamingHttpResponse <https://docs.djangoproject.com/en/dev/ref/request-response/#streaminghttpresponse-objects>`_

+---------------------+--------------------+-------------------------------------+
| Event               | Type               | Description                         |
+=====================+====================+=====================================+
| streaming_started   | INFO               | Streaming of response started       |
+---------------------+--------------------+-------------------------------------+
| streaming_finished  | INFO               | Streaming of response finished      |
+---------------------+--------------------+-------------------------------------+
| streaming_cancelled | WARNING            | Streaming of response was cancelled |
+---------------------+--------------------+-------------------------------------+
| streaming_failed    | ERROR              | Streaming of response failed        |
+---------------------+--------------------+-------------------------------------+


Request Bound Metadata
^^^^^^^^^^^^^^^^^^^^^^

These metadata are repeated on each log of the current request and will be also be repeated in all children Celery tasks.

+------------------+---------------------------------------------------------------------------------------------------------------------------------+
| Key              | Value                                                                                                                           |
+==================+=================================================================================================================================+
| request_id       | UUID for the request or value of ``X-Request-ID`` HTTP header when provided                                                     |
+------------------+---------------------------------------------------------------------------------------------------------------------------------+
| correlation_id   | value of ``X-Correlation-ID`` HTTP header when provided                                                                         |
+------------------+---------------------------------------------------------------------------------------------------------------------------------+
| user_id          | user's id or None (requires `django.contrib.auth.middleware.AuthenticationMiddleware`_)                                         |
|                  |                                                                                                                                 |
|                  | `DRF <https://www.django-rest-framework.org/>`_: it will only be in ``request_finished`` and ``request_failed`` events          |
|                  |                                                                                                                                 |
|                  | If you need to override the bound ``user_id``, it has to be done in all three signals:                                          |
|                  |  - :attr:`django_structlog.signals.bind_extra_request_metadata`                                                                 |
|                  |  - :attr:`django_structlog.signals.bind_extra_request_finished_metadata`                                                        |
|                  |  - :attr:`django_structlog.signals.bind_extra_request_failed_metadata`                                                          |
+------------------+---------------------------------------------------------------------------------------------------------------------------------+
| ip               | request's ip                                                                                                                    |
+------------------+---------------------------------------------------------------------------------------------------------------------------------+

To bind more metadata or override existing metadata from request see :ref:`django_signals`

.. _`django.contrib.auth.middleware.AuthenticationMiddleware`: https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.contrib.auth.middleware


Request Events Metadata
^^^^^^^^^^^^^^^^^^^^^^^

These metadata appear once along with their associated event

+------------------+------------------+--------------------------------------------------------------+
| Event            | Key              | Value                                                        |
+==================+==================+==============================================================+
| request_started  | request          | request as string                                            |
+------------------+------------------+--------------------------------------------------------------+
| request_started  | user_agent       | request's user agent                                         |
+------------------+------------------+--------------------------------------------------------------+
| request_finished | code             | request's status code                                        |
+------------------+------------------+--------------------------------------------------------------+
| request_failed   | exception        | exception traceback (requires format_exc_info_)              |
+------------------+------------------+--------------------------------------------------------------+

.. _format_exc_info: https://www.structlog.org/en/stable/api.html#structlog.processors.format_exc_info

Celery
------

Task Events
^^^^^^^^^^^

+--------------------+-------------+------------------------------------------------+
| Event              | Type        | Description                                    |
+====================+=============+================================================+
| task_enqueued      | INFO        | A task was enqueued by request or another task |
+--------------------+-------------+------------------------------------------------+
| task_retrying      | WARNING     | Worker retry task                              |
+--------------------+-------------+------------------------------------------------+
| task_started       | INFO        | task just started executing                    |
+--------------------+-------------+------------------------------------------------+
| task_succeeded     | INFO        | Task completed successfully                    |
+--------------------+-------------+------------------------------------------------+
| task_failed        | ERROR/INFO* | Task failed                                    |
+--------------------+-------------+------------------------------------------------+
| task_revoked       | WARNING     | Task was canceled                              |
+--------------------+-------------+------------------------------------------------+
| task_not_found     | ERROR       | Celery app did not discover the requested task |
+--------------------+-------------+------------------------------------------------+
| task_rejected      | ERROR       | Task could not be enqueued                     |
+--------------------+-------------+------------------------------------------------+

\* if task threw an expected exception, it will logged as ``INFO``. See `Celery's Task.throws <https://docs.celeryproject.org/en/latest/userguide/tasks.html#Task.throws>`_

Task Bound Metadata
^^^^^^^^^^^^^^^^^^^

These metadata are repeated on each log of the current task and will be also be repeated in all children Celery tasks.
Take note that all the caller's logger bound metadata are also bound to the task's logger.

+------------------+------------------------------------+
| Key              | Value                              |
+==================+====================================+
| task_id          | UUID of the current task           |
+------------------+------------------------------------+
| parent_task_id   | UUID of the parent's task (if any) |
+------------------+------------------------------------+

To bind more metadata or override existing metadata from task see :ref:`celery_signals`


Task Event Metadata
^^^^^^^^^^^^^^^^^^^

These metadata appear once along with their associated event

+------------------+------------------+----------------------------------------+
| Event            | Key              | Value                                  |
+==================+==================+========================================+
| task_enqueued    | child_task_id    | id of the task being enqueued          |
+------------------+------------------+----------------------------------------+
| task_enqueued    | child_task_name  | name of the task being enqueued        |
+------------------+------------------+----------------------------------------+
| task_enqueued    | routing_key      | task's routing key                     |
+------------------+------------------+----------------------------------------+
| task_enqueued    | priority         | priority of task (if any)              |
+------------------+------------------+----------------------------------------+
| task_retrying    | reason           | reason for retry                       |
+------------------+------------------+----------------------------------------+
| task_started     | task             | name of the task                       |
+------------------+------------------+----------------------------------------+
| task_succeeded   | duration_ms      | duration of the task in milliseconds   |
+------------------+------------------+----------------------------------------+
| task_failed      | error            | exception as string                    |
+------------------+------------------+----------------------------------------+
| task_failed      | exception*       | exception's traceback                  |
+------------------+------------------+----------------------------------------+
| task_failed      | duration_ms      | duration of the task in milliseconds   |
+------------------+------------------+----------------------------------------+
| task_revoked     | terminated       | Set to True if the task was terminated |
+------------------+------------------+----------------------------------------+
| task_revoked     | signum           | python termination signal's number     |
+------------------+------------------+----------------------------------------+
| task_revoked     | signame          | python termination signal's name       |
+------------------+------------------+----------------------------------------+
| task_revoked     | expired          | see Celery's documentation             |
+------------------+------------------+----------------------------------------+
| task_revoked     | task_id          | id of the task being revoked           |
+------------------+------------------+----------------------------------------+
| task_revoked     | task             | name of the task being revoked         |
+------------------+------------------+----------------------------------------+
| task_not_found   | task_id          | id of the task not found               |
+------------------+------------------+----------------------------------------+
| task_not_found   | task             | name of the task not found             |
+------------------+------------------+----------------------------------------+
| task_rejected    | task_id          | id of the task being rejected          |
+------------------+------------------+----------------------------------------+

\* if task threw an expected exception, ``exception`` will be omitted. See `Celery's Task.throws <https://docs.celeryproject.org/en/latest/userguide/tasks.html#Task.throws>`_
