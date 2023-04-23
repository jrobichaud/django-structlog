Change Log
==========


5.1.0 (April 22, 2023)
----------------------

*New:*
    - Add new signal :class:`django_structlog.signals.update_failure_response` allowing to modify the response in case of failure. See `#231 <https://github.com/jrobichaud/django-structlog/issues/231>`_. Special thanks to `@HMaker <https://github.com/HMaker>`_.

5.0.2 (April 16, 2023)
----------------------

See: :ref:`upgrade_5.0`

*Fixes:*
    - Fix regression in 5.0.0 and 5.0.1 where exceptions were not logged as ``error`` but as ``info``. See `#226 <https://github.com/jrobichaud/django-structlog/issues/226>`_. Special thanks to `@ntap-fge <https://github.com/ntap-fge>`_.

*Rollbacks from 5.0.0:*
    - Rollback removal of ``django_structlog.signals.bind_extra_request_failed_metadata``. Relates the above fix.


5.0.1 (March 24, 2023)
----------------------

See: :ref:`upgrade_5.0`

*Changes:*
   - minimum requirements change for ``asgiref`` to 3.6.0. See `#209 <https://github.com/jrobichaud/django-structlog/pull/209>`_. Special thanks to `@adinsoon <https://github.com/adinsoon>`_.


5.0.0 (March 23, 2023)
----------------------

See: :ref:`upgrade_5.0`

*Changes:*
   - ``RequestMiddleware`` and ``CeleryMiddleware`` now properly support async views

*Removed:*
    -  *(Rolled back in 5.0.2)* ``django_structlog.signals.bind_extra_request_failed_metadata``

*Deprecates:*
    - :class:`django_structlog.middlewares.request_middleware_router`
    - :class:`django_structlog.middlewares.requests.AsyncRequestMiddleware`
    - :class:`django_structlog.middlewares.requests.SyncRequestMiddleware`


4.1.1 (February 7, 2023)
------------------------

*New:*
    - Add :class:`django_structlog.middlewares.request_middleware_router` to choose automatically between Async or Sync middleware

*Rollbacks from 4.1.0:*
    - Rollback ``RequestMiddleware`` not being a class anymore, its an internal ``SyncRequestMiddleware``

*Others:*
    - Migrate project to ``pyproject.toml`` instead of ``setup.py``
    - Add `asgi` server to demo project see :ref:`development`.


4.1.0 (February 4, 2023)
------------------------

*New:*
    - Add `async view <https://docs.djangoproject.com/en/4.1/topics/async/#async-views>`_ support. See `#180 <https://github.com/jrobichaud/django-structlog/pull/180>`_. Special thanks to `@DamianMel <https://github.com/DamianMel>`_.

*Changes:*
    - ``RequestMiddleware`` is no longer a class but a function due to async view support. This should only affect projects using the middleware not as intended. If this cause you problems, please refer to this issue `#183 <https://github.com/jrobichaud/django-structlog/issues/183>`_, `the documentation <https://django-structlog.readthedocs.io>`_ or feel free to open a new issue. Special thanks to `@gvangool <https://github.com/gvangool>`_ for pointing that out.

*Others:*
    - Add colours in log in the demo project. See `63bdb4d <https://github.com/jrobichaud/django-structlog/commit/63bdb4d>`_ to update your projects. Special thanks to `@RoscoeTheDog <https://github.com/RoscoeTheDog>`_.
    - Upgrade or remove various development packages


4.0.1 (October 25, 2022)
------------------------

*New:*
    - Add support to ``python`` 3.11. See `#142 <https://github.com/jrobichaud/django-structlog/pull/142>`_. Special thanks to `@jairhenrique <https://github.com/jairhenrique>`_.


4.0.0 (October 22, 2022)
------------------------

See: :ref:`upgrade_4.0`

*Changes:*
    - ``django-structlog`` will now on follow LTS versions of Python, Django, and Celery. See `#110 <https://github.com/jrobichaud/django-structlog/pull/110>`_. Special thanks to `@jairhenrique <https://github.com/jairhenrique>`_ for his convincing arguments.

*New:*
    - You can now install ``django-structlog`` with ``celery`` extra. Specifying ``django-structlog[celery]==4.0.0`` in ``requirements.txt`` will make sure your ``celery``'s version is compatible.

*Others:*
    - Upgrade or remove various development packages
    - Upgrade local development environment from python 3.7 to 3.10 and from django 3.2 to django 4.1
    - Added a `gh-pages <https://jrobichaud.github.io/django-structlog/>`_


3.0.1 (August 2, 2022)
----------------------

*Fixes:*
    - ``AttributeError`` with custom User without ``pk``. See `#80 <https://github.com/jrobichaud/django-structlog/issues/80>`_. Special thanks to `@mlegner <https://github.com/mlegner>`_.

*Others:*
    - Add ``dependabot`` to manage dependencies. See `#83 <https://github.com/jrobichaud/django-structlog/pull/83>`_. Special thanks to `@jairhenrique <https://github.com/jairhenrique>`_.
    - Upgrade various development packages


3.0.0 (August 1, 2022)
----------------------

See: :ref:`upgrade_3.0`

*Changes:*
    - ``django-structlog`` now uses ``structlog.contextvars`` instead of ``structlog.threadlocal``. See the upgrade guide for more information (:ref:`upgrade_3.0`) and `#78 <https://github.com/jrobichaud/django-structlog/pull/78>`_. Special thanks to `@AndrewGuenther <https://github.com/AndrewGuenther>`_  and `@shimizukawa <https://github.com/shimizukawa>`_.
        - removed ``django_structlog.processors.inject_context_dict``
        - minimum requirements change to ``python`` 3.7+
        - minimum requirements change to ``structlog`` 21.5

*New:*
    - Add python 3.10, celery 5.2 and django 4.0 to the test matrix.

*Others:*
    - Remove ``wrapper_class`` from the configuration


2.2.0 (November 18, 2021)
-------------------------

*Changes:*
    - Requests were logged as ``<WSGIRequest: GET '/'>`` (as an object) and now they are logged like this ``GET /`` (as a string). See `#72 <https://github.com/jrobichaud/django-structlog/issues/72>`_. Special thanks to `@humitos <https://github.com/humitos>`_.


2.1.3 (September 28, 2021)
--------------------------

*Fixes:*
    - Implement `Celery Task.throws <https://docs.celeryproject.org/en/latest/userguide/tasks.html#Task.throws>`_' behaviour of logging expected exception as ``INFO`` with no tracebacks. See `#62 <https://github.com/jrobichaud/django-structlog/issues/62>`_ and `#70 <https://github.com/jrobichaud/django-structlog/pull/70>`_. Special thanks to `@meunomemauricio <https://github.com/meunomemauricio>`_.


2.1.2 (August 31, 2021)
-----------------------

*Fixes:*
    - ``django.core.exceptions.PermissionDenied`` is no longer logged as 500 but 403. See `#68 <https://github.com/jrobichaud/django-structlog/pull/68>`_. Special thanks to `@rabbit-aaron <https://github.com/rabbit-aaron>`_.


2.1.1 (June 22, 2021)
-------------------------

*Others:*
    - Add ``django`` 3.2 and ``python`` 3.9 to the test matrix and ``pypi`` metadata. See `#65 <https://github.com/jrobichaud/django-structlog/pull/65>`_. Special thanks to `@kashewnuts <https://github.com/kashewnuts>`_.


2.1.0 (November 26, 2020)
-------------------------

*New:*
    - :class:`django_structlog.processors.inject_context_dict` for standard python loggers. See `#24 <https://github.com/jrobichaud/django-structlog/issues/24>`_. Special thanks to `@debfx <https://github.com/debfx>`_.


2.0.0 (November 25, 2020)
-------------------------

*Upgrade:*
    - There are necessary configuration changes needed. See :ref:`upgrade_2.0` for the details.

*Changes:*
    - No longer add ``error`` and ``error_traceback``. See `#55 <https://github.com/jrobichaud/django-structlog/issues/55>`_ and :ref:`upgrade_2.0`. Special thanks to `@debfx <https://github.com/debfx>`_.

*Fixes:*
    - Fix crash when request's user is ``None`` for `django-oauth-toolkit <https://github.com/jazzband/django-oauth-toolkit>`_. See `#56 <https://github.com/jrobichaud/django-structlog/issues/56>`_. Special thanks to `@nicholasamorim <https://github.com/nicholasamorim>`_.


1.6.3 (November 11, 2020)
-------------------------

*Improvements:*
    - Call stack of exception in log is now an appropriate string. See `#54 <https://github.com/jrobichaud/django-structlog/pull/54>`_. Special thanks to `@debfx <https://github.com/debfx>`_.


1.6.2 (October 4, 2020)
-----------------------

*Fixes:*
    - Fix UUID as User pk causing issues. See `#52 <https://github.com/jrobichaud/django-structlog/pull/52>`_ `#45 <https://github.com/jrobichaud/django-structlog/pull/45>`_ and `#51 <https://github.com/jrobichaud/django-structlog/issues/51>`_. Special thanks to `@fadedDexofan <https://github.com/fadedDexofan>`_.


1.6.1 (August 13, 2020)
-----------------------

*Fixes:*
    - Removed ``providing_args`` from signals to fix django 4.0 deprecation warnings introduced by django 3.1. See `#44 <https://github.com/jrobichaud/django-structlog/pull/44>`_. Special thanks to `@ticosax <https://github.com/ticosax>`_.
    - Fix ``sender`` of ``signals.pre_task_succeeded``
    - Documented signal parameters in doc strings and ``API documentation`` to replace ``providing_args``

*Others:*
    - Add ``django`` 3.0 and 3.1 to the test matrix and ``pypi`` supported frameworks metadata
    - Fix reference of the previous ci in the documentation


1.6.0 (June 17, 2020)
---------------------

*Changes:*
    - ``task_succeed`` is now ``task_succeeded``. Special thanks to `@PawelMorawian <https://github.com/PawelMorawian>`_.
    - Remove ``result`` from ``task_succeeded`` log (may be added back, see below). Special thanks to `@PawelMorawian <https://github.com/PawelMorawian>`_ as well.
    - Add ``django_structlog.celery.signals.pre_task_succeeded``. To be able to bind ``result`` if someone really needs it.


1.5.5 (June 16, 2020)
---------------------

*New:*
    - Add ``bind_extra_request_finished_metadata`` and ``bind_extra_request_failed_metadata``. See `#39 <https://github.com/jrobichaud/django-structlog/pull/39>`_. Special thanks to `@prik2693 <https://github.com/prik2693>`_.


1.5.4 (June 15, 2020)
---------------------

*Improvements:*
    - Remove redundant ``DJANGO_STRUCTLOG_LOG_USER_IN_REQUEST_FINISHED`` setting and just always make sure ``user_id`` is in ``request_finished`` and ``request_failed`` instead. See `#37 <https://github.com/jrobichaud/django-structlog/pull/37>`_.


1.5.3 (June 15, 2020)
---------------------

*New:*
    - Add ``DJANGO_STRUCTLOG_LOG_USER_IN_REQUEST_FINISHED`` setting to support `Django REST framework <https://www.django-rest-framework.org/>`_. See `#37 <https://github.com/jrobichaud/django-structlog/pull/37>`_. Special thanks to `@immortaleeb <https://github.com/immortaleeb>`_.


1.5.2 (April 2, 2020)
---------------------

*New:*
    - Add ``modify_context_before_task_publish`` signal.


1.5.1 (March 18, 2020)
----------------------

*Improvements:*
    - Allow to override celery task metadata from binding. See `#32 <https://github.com/jrobichaud/django-structlog/issues/32>`_ and `#33 <https://github.com/jrobichaud/django-structlog/pull/33>`_. Special thanks to `@chiragjn <https://github.com/chiragjn>`_


1.5.0 (March 6, 2020)
---------------------

*Improvements:*
    - Add support for celery 3. See `#26 <https://github.com/jrobichaud/django-structlog/issues/26>`_ and `#31 <https://github.com/jrobichaud/django-structlog/pull/31>`_. Special thanks to `@chiragjn <https://github.com/chiragjn>`_ and `@prik2693 <https://github.com/prik2693>`_


1.4.1 (February 8, 2020)
------------------------

*New:*
    - Bind ``X-Correlation-ID`` HTTP header's value as ``correlation_id`` when provided in request.


1.4.0 (February 7, 2020)
------------------------

*New:*
    - Use ``X-Request-ID`` HTTP header's value as ``request_id`` when provided in request. See `#22 <https://github.com/jrobichaud/django-structlog/issues/22>`_. Special thanks to `@jairhenrique <https://github.com/jairhenrique>`_


1.3.5 (December 23, 2019)
-------------------------

*New:*
    - Add python 3.8, celery 4.4 and django 3.0 to the test matrix.

*Improvements:*
    - Extract ``test_app`` from ``django_structlog_demo_app`` in order to test ``django_structlog`` all by itself
    - Improve CI execution speed by merging stages
    - Upgrade a few development depencencies


1.3.4 (November 27, 2019)
-------------------------

*Bugfix:*
    - Exception logging not working properly with ``DEBUG = False``. See `#19 <https://github.com/jrobichaud/django-structlog/issues/19>`_. Special thanks to `@danpalmer <https://github.com/danpalmer>`_


1.3.3 (October 6, 2019)
-----------------------

*Bugfix:*
    - Fix support of different primary key for ``User`` model. See `#13 <https://github.com/jrobichaud/django-structlog/issues/13>`_. Special thanks to `@dhararon <https://github.com/dhararon>`_


1.3.2 (September 21, 2019)
--------------------------

*Improvements:*
    - Add support of projects without ``AuthenticationMiddleware``. See `#9 <https://github.com/jrobichaud/django-structlog/pull/9>`_. Special thanks to `@dhararon <https://github.com/dhararon>`_


1.3.1 (September 4, 2019)
-------------------------

*Bugfixes:*
    - Remove extraneous ``rest-framework`` dependency introduced by `#7 <https://github.com/jrobichaud/django-structlog/pull/7>`_. See `#8 <https://github.com/jrobichaud/django-structlog/pull/8>`_ . Special thanks to `@ghickman <https://github.com/ghickman>`_


1.3.0 (September 3, 2019)
-------------------------

*Improvements:*
    - Improve django uncaught exception formatting. See `#7 <https://github.com/jrobichaud/django-structlog/pull/7>`_. Special thanks to `@paulstuartparker <https://github.com/paulstuartparker>`_


1.2.3 (May 18, 2019)
--------------------

*Bugfixes:*
    - Fix ``structlog`` dependency not being installed

*Improvements:*
    - Use `black <https://github.com/python/black>`_ code formatter


1.2.2 (May 13, 2019)
--------------------

*Improvements:*
    - Use appropriate packaging


1.2.1 (May 8, 2019)
-------------------

*Bugfixes:*
    - Fix missing license file to be included in distribution


1.2.0 (May 8, 2019)
-------------------

*Changes:*
    - In the event ``task_enqueued``, ``task_id`` and ``task_name`` are renamed ``child_task_id`` and ``child_task_name`` respectively to avoid override of ``task_id`` in nested tasks.


1.1.6 (May 8, 2019)
-------------------

*New:*
    - Add ``task_name`` when a task is enqueued


1.1.5 (May 8, 2019)
-------------------

*New:*
    - Add support of tasks calling other tasks (introducing ``parent_task_id``)

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
