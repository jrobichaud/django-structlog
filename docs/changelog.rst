Change Log
==========

1.2.1 (May 8, 2019)
-------------------

*Bugfixes:*
    - Fix missing license file to be included in distribution


1.2.0 (May 8, 2019)
-------------------

*Changes:*
    - In the event `task_enqueued`, `task_id` and `task_name` are renamed `child_task_id` and `child_task_name` respectively to avoid override of `task_id` in nested tasks.


1.1.6 (May 8, 2019)
-------------------

*New:*
    - Add `task_name` when a task is enqueued


1.1.5 (May 8, 2019)
-------------------

*New:*
    - Add support of tasks calling other tasks (introducing `parent_task_id`)

*Bugfixes:*
    - Fix missing packages


1.1.4 (April 22, 2019)
----------------------

*Improvements:*
    - Wheel distribution


1.1.3 (April 22, 2019)
----------------------

*Improvements:*
    - api documentation
    - code documentation

1.1.2 (April 19, 2019)
----------------------

*Changes:*
    - Rewrite the log texts as events

1.1.1 (April 18, 2019)
----------------------

*New:*
    - Add ``celery`` signal ``signals.bind_extra_task_metadata``


1.1 (April 16, 2019)
--------------------

*New:*
    - Add ``celery`` tasks support


1.0.4 to 1.0.7 (April 14, 2019)
-------------------------------

*New:*
    - Automated releases with tags on ``travis``

1.0.3 (April 14, 2019)
----------------------

*Bugfixes:*
    - Add ``bind_extra_request_metadata`` documentation

1.0.2 (April 13, 2019)
----------------------

*Bugfixes:*
    - Tweaked documentation.

1.0.0 (April 13, 2019)
----------------------

*New*:
    - Fist public release.