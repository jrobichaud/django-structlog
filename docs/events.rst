Events and Metadata
===================

Django's RequestMiddleware
--------------------------

Request Events
^^^^^^^^^^^^^^

+------------------+---------+------------------------------+
| Event            | Type    | Description                  |
+==================+=========+==============================+
| request_started  | INFO    | Django received a request    |
+------------------+---------+------------------------------+
| request_finished | INFO    | request completed normally   |
+------------------+---------+------------------------------+
| request_failed   | ERROR   | unhandled exception occurred |
+------------------+---------+------------------------------+

Request Bound Metadata
^^^^^^^^^^^^^^^^^^^^^^

These metadata are repeated on each log of the current request and will be also be repeated in all children Celery tasks.

+------------------+------------------------------------------------------------------------------------------------------------------------+
| Key              | Value                                                                                                                  |
+==================+========================================================================================================================+
| request_id       | UUID for the request or value of ``X-Request-ID`` HTTP header when provided                                            |
+------------------+------------------------------------------------------------------------------------------------------------------------+
| correlation_id   | value of ``X-Correlation-ID`` HTTP header when provided                                                                |
+------------------+------------------------------------------------------------------------------------------------------------------------+
| user_id          | user's id or None (requires `django.contrib.auth.middleware.AuthenticationMiddleware`_)                                |
+                  +                                                                                                                        +
|                  | `DRF <https://www.django-rest-framework.org/>`_: it will only be in ``request_finished`` and ``request_failed`` events |
+------------------+------------------------------------------------------------------------------------------------------------------------+
| ip               | request's ip                                                                                                           |
+------------------+------------------------------------------------------------------------------------------------------------------------+

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

CeleryMiddleware
----------------

Task Events
^^^^^^^^^^^

+--------------------+-------------+------------------------------------------------+
| Event              | Type        | Description                                    |
+====================+=============+================================================+
| task_enqueued      | INFO        | A task was enqueued by request or another task |
+--------------------+-------------+------------------------------------------------+
| task_retrying      | WARNING     | Worker retry task                              |
+--------------------+-------------+------------------------------------------------+
| task_succeeded     | INFO        | Task completed successfully                    |
+--------------------+-------------+------------------------------------------------+
| task_failed        | ERROR/INFO* | Task failed                                    |
+--------------------+-------------+------------------------------------------------+
| task_revoked       | WARNING     | Task was canceled                              |
+--------------------+-------------+------------------------------------------------+
| task_not_found     | ERROR       | Celery app did not discover the requested task |
+--------------------+-------------+------------------------------------------------+
| task_task_rejected | ERROR       | Task could not be enqueued                     |
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
| task_retrying    | reason           | reason for retry                       |
+------------------+------------------+----------------------------------------+
| task_failed      | error            | exception as string                    |
+------------------+------------------+----------------------------------------+
| task_failed      | exception*       | exception's traceback                  |
+------------------+------------------+----------------------------------------+
| task_revoked     | terminated       | Set to True if the task was terminated |
+------------------+------------------+----------------------------------------+
| task_revoked     | signum           | see Celery's documentation             |
+------------------+------------------+----------------------------------------+
| task_revoked     | expired          | see Celery's documentation             |
+------------------+------------------+----------------------------------------+

\* if task threw an expected exception, ``exception`` will be omitted. See `Celery's Task.throws <https://docs.celeryproject.org/en/latest/userguide/tasks.html#Task.throws>`_
