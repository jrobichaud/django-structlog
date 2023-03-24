.. inclusion-marker-introduction-begin

django-structlog
================

| |pypi| |wheels| |build-status| |docs| |coverage| |open_issues| |pull_requests|
| |django| |python| |license| |black|
| |watchers| |stars| |forks|

.. |build-status| image:: https://github.com/jrobichaud/django-structlog/actions/workflows/main.yml/badge.svg?branch=master
   :target: https://github.com/jrobichaud/django-structlog/actions
   :alt: Build Status

.. |pypi| image:: https://img.shields.io/pypi/v/django-structlog.svg
   :target: https://pypi.org/project/django-structlog/
   :alt: PyPI version

.. |docs| image:: https://readthedocs.org/projects/django-structlog/badge/?version=latest
   :target: https://django-structlog.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. |coverage| image:: https://img.shields.io/codecov/c/github/jrobichaud/django-structlog.svg
   :target: https://codecov.io/gh/jrobichaud/django-structlog
   :alt: codecov

.. |python| image:: https://img.shields.io/pypi/pyversions/django-structlog.svg
    :target: https://pypi.org/project/django-structlog/
    :alt: Supported Python versions

.. |license| image:: https://img.shields.io/pypi/l/django-structlog.svg
    :target: https://github.com/jrobichaud/django-structlog/blob/master/LICENSE.rst
    :alt: License

.. |open_issues| image:: https://img.shields.io/github/issues/jrobichaud/django-structlog.svg
    :target: https://github.com/jrobichaud/django-structlog/issues
    :alt: GitHub issues

.. |django| image:: https://img.shields.io/pypi/djversions/django-structlog.svg
    :target: https://pypi.org/project/django-structlog/
    :alt: PyPI - Django Version

.. |pull_requests| image:: https://img.shields.io/github/issues-pr/jrobichaud/django-structlog.svg
    :target: https://github.com/jrobichaud/django-structlog/pulls
    :alt: GitHub pull requests

.. |forks| image:: https://img.shields.io/github/forks/jrobichaud/django-structlog.svg?style=social
    :target: https://github.com/jrobichaud/django-structlog/
    :alt: GitHub forks

.. |stars| image:: https://img.shields.io/github/stars/jrobichaud/django-structlog.svg?style=social
    :target: https://github.com/jrobichaud/django-structlog/
    :alt: GitHub stars

.. |watchers| image:: https://img.shields.io/github/watchers/jrobichaud/django-structlog.svg?style=social
    :target: https://github.com/jrobichaud/django-structlog/
    :alt: GitHub watchers

.. |wheels| image:: https://img.shields.io/pypi/wheel/django-structlog.svg
    :target: https://pypi.org/project/django-structlog/
    :alt: PyPI - Wheel

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black
    :alt: Black


django-structlog is a structured logging integration for `Django <https://www.djangoproject.com/>`_ project using `structlog <https://www.structlog.org/>`_

Logging will then produce additional cohesive metadata on each logs that makes it easier to track events or incidents.


Additional Popular Integrations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Django REST framework <https://www.django-rest-framework.org/>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Django REST framework`` is supported by default. But when using it with ``rest_framework.authentication.TokenAuthentication`` (or other DRF authentications)  ``user_id`` will be only be in ``request_finished`` and ``request_failed`` instead of each logs.

See `#37  <https://github.com/jrobichaud/django-structlog/issues/37>`_ for details.

`Celery <http://www.celeryproject.org/>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Celery's task logging requires additional configurations, see `documentation <https://django-structlog.readthedocs.io/en/latest/celery.html>`_ for details.


Logging comparison
^^^^^^^^^^^^^^^^^^

Standard logging:
~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> import logging
   >>> logger = logging.get_logger(__name__)
   >>> logger.info("An error occurred")

.. code-block:: bash

   An error occurred

Well... ok

With django-structlog and flat_line:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> import structlog
   >>> logger = structlog.get_logger(__name__)
   >>> logger.info("an_error_occurred", bar="Buz")

.. code-block:: bash

   timestamp='2019-04-13T19:39:31.089925Z' level='info' event='an_error_occurred' logger='my_awesome_project.my_awesome_module' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' bar='Buz'

Then you can search with commands like:

.. code-block:: bash

   $ cat logs/flat_line.log | grep request_id='3a8f801c-072b-4805-8f38-e1337f363ed4'

With django-structlog and json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> import structlog
   >>> logger = structlog.get_logger(__name__)
   >>> logger.info("an_error_occurred", bar="Buz")

.. code-block:: json

   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "event": "an_error_occurred", "timestamp": "2019-04-13T19:39:31.089925Z", "logger": "my_awesome_project.my_awesome_module", "level": "info", "bar": "Buz"}

Then you can search with commands like:

.. code-block:: bash

   $ cat logs/json.log | jq '.[] | select(.request_id="3a8f801c-072b-4805-8f38-e1337f363ed4")' -s

.. inclusion-marker-introduction-end

.. inclusion-marker-getting-started-begin

Getting Started
===============

These steps will show how to integrate the middleware to your awesome application.

Installation
^^^^^^^^^^^^

Install the library

.. code-block:: bash

   pip install django-structlog

Add middleware

.. code-block:: python

   MIDDLEWARE = [
       # ...
       'django_structlog.middlewares.RequestMiddleware',
   ]

Add appropriate structlog configuration to your ``settings.py``

.. code-block:: python

   import structlog

   LOGGING = {
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
           # Make sure to replace the following logger's name for yours
           "django_structlog_demo_project": {
               "handlers": ["console", "flat_line_file", "json_file"],
               "level": "INFO",
           },
       }
   }

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
       cache_logger_on_first_use=True,
   )

Start logging with ``structlog`` instead of ``logging``.

.. code-block:: python

   import structlog
   logger = structlog.get_logger(__name__)

.. _django_signals:

Extending Request Log Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default only a ``request_id`` and the ``user_id`` are bound from the request but pertinent log metadata may vary from a project to another.

If you need to add more metadata from the request you can implement a convenient signal receiver to bind them. You can also override existing bound metadata the same way.

.. code-block:: python

   from django.dispatch import receiver

   from django_structlog.signals import bind_extra_request_metadata
   import structlog


   @receiver(bind_extra_request_metadata)
   def bind_user_email(request, logger, **kwargs):
       structlog.contextvars.bind_contextvars(user_email=getattr(request.user, 'email', ''))


Standard Loggers
^^^^^^^^^^^^^^^^

It is also possible to log using standard python logger.

In your formatters, add the ``foreign_pre_chain`` section, and then add ``structlog.contextvars.merge_contextvars``:

.. code-block:: python

   LOGGING = {
       "version": 1,
       "disable_existing_loggers": False,
       "formatters": {
           "json_formatter": {
               "()": structlog.stdlib.ProcessorFormatter,
               "processor": structlog.processors.JSONRenderer(),
               # Add this section:
               "foreign_pre_chain": [
                   structlog.contextvars.merge_contextvars, # <---- add this
                   # customize the rest as you need
                   structlog.processors.TimeStamper(fmt="iso"),
                   structlog.stdlib.add_logger_name,
                   structlog.stdlib.add_log_level,
                   structlog.stdlib.PositionalArgumentsFormatter(),
               ],
           },
       },
       ...
    }


.. inclusion-marker-getting-started-end


.. inclusion-marker-example-outputs-begin

Example outputs
===============

Flat lines file (\ ``logs/flat_lines.log``\ )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   timestamp='2019-04-13T19:39:29.321453Z' level='info' event='request_started' logger='django_structlog.middlewares.request' request_id='c53dff1d-3fc5-4257-a78a-9a567c937561' user_id=1 ip='0.0.0.0' request=GET / user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
   timestamp='2019-04-13T19:39:29.345207Z' level='info' event='request_finished' logger='django_structlog.middlewares.request' request_id='c53dff1d-3fc5-4257-a78a-9a567c937561' user_id=1 ip='0.0.0.0' code=200
   timestamp='2019-04-13T19:39:31.086155Z' level='info' event='request_started' logger='django_structlog.middlewares.request' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' request=POST /success_task user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
   timestamp='2019-04-13T19:39:31.089925Z' level='info' event='Enqueuing successful task' logger='django_structlog_demo_project.home.views' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0'
   timestamp='2019-04-13T19:39:31.147590Z' level='info' event='task_enqueued' logger='django_structlog.middlewares.celery' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' child_task_id='6b11fd80-3cdf-4de5-acc2-3fd4633aa654'
   timestamp='2019-04-13T19:39:31.153081Z' level='info' event='This is a successful task' logger='django_structlog_demo_project.taskapp.celery' task_id='6b11fd80-3cdf-4de5-acc2-3fd4633aa654' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0'
   timestamp='2019-04-13T19:39:31.160043Z' level='info' event='request_finished' logger='django_structlog.middlewares.request' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' code=201
   timestamp='2019-04-13T19:39:31.162372Z' level='info' event='task_succeed' logger='django_structlog.middlewares.celery' task_id='6b11fd80-3cdf-4de5-acc2-3fd4633aa654' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' result='None'

Json file (\ ``logs/json.log``\ )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {"request_id": "c53dff1d-3fc5-4257-a78a-9a567c937561", "user_id": 1, "ip": "0.0.0.0", "request": "GET /", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36", "event": "request_started", "timestamp": "2019-04-13T19:39:29.321453Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"request_id": "c53dff1d-3fc5-4257-a78a-9a567c937561", "user_id": 1, "ip": "0.0.0.0", "code": 200, "event": "request_finished", "timestamp": "2019-04-13T19:39:29.345207Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "request": "POST /success_task", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36", "event": "request_started", "timestamp": "2019-04-13T19:39:31.086155Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "event": "Enqueuing successful task", "timestamp": "2019-04-13T19:39:31.089925Z", "logger": "django_structlog_demo_project.home.views", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "child_task_id": "6b11fd80-3cdf-4de5-acc2-3fd4633aa654", "event": "task_enqueued", "timestamp": "2019-04-13T19:39:31.147590Z", "logger": "django_structlog.middlewares.celery", "level": "info"}
   {"task_id": "6b11fd80-3cdf-4de5-acc2-3fd4633aa654", "request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "event": "This is a successful task", "timestamp": "2019-04-13T19:39:31.153081Z", "logger": "django_structlog_demo_project.taskapp.celery", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "code": 201, "event": "request_finished", "timestamp": "2019-04-13T19:39:31.160043Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"task_id": "6b11fd80-3cdf-4de5-acc2-3fd4633aa654", "request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "result": "None", "event": "task_succeed", "timestamp": "2019-04-13T19:39:31.162372Z", "logger": "django_structlog.middlewares.celery", "level": "info"}

.. inclusion-marker-example-outputs-end

.. inclusion-marker-upgrade-guide-begin

Upgrade Guide
=============

.. _upgrade_5.0:

Upgrading to 5.0+
^^^^^^^^^^^^^^^^^

Minimum requirements
~~~~~~~~~~~~~~~~~~~~
- requires asgiref 3.6+

Changes you may need to do
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Make sure you use ``django_structlog.middlewares.RequestMiddleware``
-----------------------------------------------------------------------

If you used any of the experimental async or sync middlewares, you do not need to anymore.
Make sure you use ``django_structlog.middlewares.RequestMiddleware`` instead of any of the other request middlewares commented below:

.. code-block:: python

    MIDDLEWARE += [
        # "django_structlog.middlewares.request_middleware_router", # <- remove
        # "django_structlog.middlewares.requests.SyncRequestMiddleware", # <- remove
        # "django_structlog.middlewares.requests.AsyncRequestMiddleware", # <- remove
        "django_structlog.middlewares.RequestMiddleware", # <- make sure you use this one
        "django_structlog.middlewares.CeleryMiddleware",
    ]

They will be removed in another major version.

2. ``django_structlog.signals.bind_extra_request_failed_metadata`` was removed
------------------------------------------------------------------------------

The signal ``bind_extra_request_failed_metadata`` was removed since it was never called.

Remove your custom signal.


.. _upgrade_4.0:

Upgrading to 4.0+
^^^^^^^^^^^^^^^^^

``django-structlog`` drops support of django below 3.2.

Minimum requirements
~~~~~~~~~~~~~~~~~~~~
- requires django 3.2+
- requires python 3.7+
- requires structlog 21.4.0+
- (optionally) requires celery 5.1+


Changes if you use ``celery``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can now install ``django-structlog`` explicitly with ``celery`` extra in order to validate the compatibility with your version of ``celery``.


.. code-block:: bash

    django-structlog[celery]==4.0.0

See `Installing “Extras” <https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras>`_ for more information about this ``pip`` feature.

.. _upgrade_3.0:

Upgrading to 3.0+
^^^^^^^^^^^^^^^^^

``django-structlog`` now use  `structlog.contextvars.bind_contextvars <https://www.structlog.org/en/stable/contextvars.html>`_ instead of ``threadlocal``.

Minimum requirements
~~~~~~~~~~~~~~~~~~~~
- requires python 3.7+
- requires structlog 21.4.0+


Changes you need to do
~~~~~~~~~~~~~~~~~~~~~~

1. Update structlog settings
----------------------------

- add ``structlog.contextvars.merge_contextvars`` as first ``processors``
- remove ``context_class=structlog.threadlocal.wrap_dict(dict),``
- (if you use standard loggers) add ``structlog.contextvars.merge_contextvars`` in `foreign_pre_chain`
- (if you use standard loggers) remove ``django_structlog.processors.inject_context_dict,``


.. code-block:: python

   structlog.configure(
       processors=[
           structlog.contextvars.merge_contextvars, # <---- add this
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
       # context_class=structlog.threadlocal.wrap_dict(dict), # <---- remove this
       logger_factory=structlog.stdlib.LoggerFactory(),
       cache_logger_on_first_use=True,
   )

   # If you use standard logging
   LOGGING = {
       "version": 1,
       "disable_existing_loggers": False,
       "formatters": {
           "json_formatter": {
               "()": structlog.stdlib.ProcessorFormatter,
               "processor": structlog.processors.JSONRenderer(),
               "foreign_pre_chain": [
                   structlog.contextvars.merge_contextvars, # <---- add this
                   # django_structlog.processors.inject_context_dict, # <---- remove this
                   structlog.processors.TimeStamper(fmt="iso"),
                   structlog.stdlib.add_logger_name,
                   structlog.stdlib.add_log_level,
                   structlog.stdlib.PositionalArgumentsFormatter(),
               ],
           },
       },
       ...
    }


2. Replace all ``logger.bind`` with ``structlog.contextvars.bind_contextvars``
------------------------------------------------------------------------------

.. code-block:: python

   @receiver(bind_extra_request_metadata)
   def bind_user_email(request, logger, **kwargs):
      # logger.bind(user_email=getattr(request.user, 'email', ''))
      structlog.contextvars.bind_contextvars(user_email=getattr(request.user, 'email', ''))

.. _upgrade_2.0:

Upgrading to 2.0+
^^^^^^^^^^^^^^^^^

``django-structlog`` was originally developed using the debug configuration `ExceptionPrettyPrinter <https://www.structlog.org/en/stable/api.html#structlog.processors.ExceptionPrettyPrinter>`_ which led to incorrect handling of exception.

- remove ``structlog.processors.ExceptionPrettyPrinter(),`` of your processors.
- make sure you have ``structlog.processors.format_exc_info,`` in your processors if you want appropriate exception logging.

.. inclusion-marker-upgrade-guide-end

.. inclusion-marker-running-tests-begin

Running the tests
=================

Note: For the moment redis is needed to run the tests. The easiest way is to start docker demo's redis.

.. code-block:: bash

   docker compose up -d redis
   pip install -r requirements.txt
   env CELERY_BROKER_URL=redis://0.0.0.0:6379 DJANGO_SETTINGS_MODULE=config.settings.test pytest test_app
   env CELERY_BROKER_URL=redis://0.0.0.0:6379 DJANGO_SETTINGS_MODULE=config.settings.test_demo_app pytest django_structlog_demo_project
   docker compose stop redis

.. inclusion-marker-running-tests-end


.. inclusion-marker-demo-begin

Demo app
========

.. code-block:: bash

   docker compose up --build

Open ``http://127.0.0.1:8000/`` in your browser.

Navigate while looking into the log files and shell's output.

.. inclusion-marker-demo-end


.. inclusion-marker-authors-begin

Authors
=======


* **Jules Robichaud-Gagnon** - *Initial work* - `jrobichaud <https://github.com/jrobichaud>`_

See also the list of `contributors <https://github.com/jrobichaud/django-structlog/contributors>`_ who participated in this project.

.. inclusion-marker-authors-end


.. inclusion-marker-acknowledgements-begin

Acknowledgments
===============

* Big thanks to `@ferd <https://github.com/ferd>`_ for his `bad opinions <https://ferd.ca/erlang-otp-21-s-new-logger.html>`_ that inspired the author enough to spend time on this library.
* `This issue <https://github.com/hynek/structlog/issues/175>`_ helped the author to figure out how to integrate ``structlog`` in Django.
* `This stack overflow question <https://stackoverflow.com/questions/43855507/configuring-and-using-structlog-with-django>`_ was also helpful.

.. inclusion-marker-acknowledgements-end

License
=======

This project is licensed under the MIT License - see the `LICENSE <https://github.com/jrobichaud/django-structlog/blob/master/LICENSE.rst>`_ file for details
