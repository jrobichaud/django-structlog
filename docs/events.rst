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

+------------------+------------------------------------------------------------------------------------------+
| Key              | Value                                                                                    |
+==================+==========================================================================================+
| request_id       | UUID of the request                                                                      |
+------------------+------------------------------------------------------------------------------------------+
| user_id          | user's id or None (requires ``django.contrib.auth.middleware.AuthenticationMiddleware``) |
+------------------+------------------------------------------------------------------------------------------+
| ip               | request's ip                                                                             |
+------------------+------------------------------------------------------------------------------------------+

To bind more metadata from request see :ref:`django_signals`


Request Events Metadata
^^^^^^^^^^^^^^^^^^^^^^^

These metadata appear once along with their associated event

+------------------+------------------+------------------------+
| Event            | Key              | Value                  |
+==================+==================+========================+
| request_started  | request          | request as string      |
+------------------+------------------+------------------------+
| request_started  | user_agent       | request's user agent   |
+------------------+------------------+------------------------+
| request_finished | code             | request's status code  |
+------------------+------------------+------------------------+
| request_failed   | exception        | exception as string    |
+------------------+------------------+------------------------+


CeleryMiddleware
----------------

Task Events
^^^^^^^^^^^

+--------------------+---------+------------------------------------------------+
| Event              | Type    | Description                                    |
+====================+=========+================================================+
| task_enqueued      | INFO    | A task was enqueued by request or another task |
+--------------------+---------+------------------------------------------------+
| task_retrying      | WARNING | Worker retry task                              |
+--------------------+---------+------------------------------------------------+
| task_succeed       | INFO    | Task completed successfully                    |
+--------------------+---------+------------------------------------------------+
| task_failed        | ERROR   | Task failed                                    |
+--------------------+---------+------------------------------------------------+
| task_revoked       | WARNING | Task was canceled                              |
+--------------------+---------+------------------------------------------------+
| task_not_found     | ERROR   | Celery app did not discover the requested task |
+--------------------+---------+------------------------------------------------+
| task_task_rejected | ERROR   | Task could not be enqueued                     |
+--------------------+---------+------------------------------------------------+

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

To bind more metadata from task see :ref:`celery_signals`


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
| task_succeed     | result           | result of the task                     |
+------------------+------------------+----------------------------------------+
| task_failed      | error            | exception as string                    |
+------------------+------------------+----------------------------------------+
| task_revoked     | terminated       | Set to True if the task was terminated |
+------------------+------------------+----------------------------------------+
| task_revoked     | signum           | see Celery's documentation             |
+------------------+------------------+----------------------------------------+
| task_revoked     | expired          | see Celery's documentation             |
+------------------+------------------+----------------------------------------+


