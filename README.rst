
django-structlog
================
|build-status| |pypi| |docs| |coverage| |python| |license|

.. |build-status| image:: https://secure.travis-ci.org/jrobichaud/django-structlog.svg?branch=master
   :target: https://travis-ci.org/jrobichaud/django-structlog
   :alt: Build Status


.. |pypi| image:: https://img.shields.io/pypi/v/django-structlog.svg
   :target: https://django-structlog.readthedocs.io/en/latest/changelog.html
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
    :target: https://pypi.org/project/django-structlog/
    :alt: License

django-structlog is a structured logging integration for Django project using `structlog <https://www.structlog.org/>`_

Logging will then produce additional cohesive metadata on each logs that makes it easier to track incident.

Standard logging:
~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> import logging
   >>> logger = logging.get_logger(__name__)
   >>> logger.info("An error occured")

.. code-block:: bash

   An error occured

Well... ok

With django-structlog and flag_line:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> import structlog 
   >>> logger = structlog.get_logger(__name__)
   >>> logger.info("An error occured", bar="Buz")

.. code-block:: bash

   timestamp='2019-04-13T19:39:31.089925Z' level='info' event='An error occured' logger='my_awesome_project.my_awesome_module' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0'

Then you can search with commands like:

.. code-block:: bash

   $ cat logs/flat_line.log | grep request_id='3a8f801c-072b-4805-8f38-e1337f363ed4'

With django-structlog and json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> import structlog 
   >>> logger = structlog.get_logger(__name__)
   >>> logger.info("An error occured", bar="Buz")

.. code-block:: json

   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "event": "An error occured", "timestamp": "2019-04-13T19:39:31.089925Z", "logger": "my_awesome_project.my_awesome_module", "level": "info", "bar": "buz"}

Then you can search with commands like:

.. code-block:: bash

   $ cat logs/json.log | jq '.[] | select(.request_id="3a8f801c-072b-4805-8f38-e1337f363ed4")' -s

Getting Started
---------------

These steps will show how to integrate the middleware to your awesome application.

Installing
^^^^^^^^^^

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
           "django_structlog_demo_project": {
               "handlers": ["console", "flat_line_file", "json_file"],
               "level": "INFO",
           },
       }
   }

   structlog.configure(
       processors=[
           structlog.stdlib.filter_by_level,
           structlog.processors.TimeStamper(fmt="iso"),
           structlog.stdlib.add_logger_name,
           structlog.stdlib.add_log_level,
           structlog.stdlib.PositionalArgumentsFormatter(),
           structlog.processors.StackInfoRenderer(),
           structlog.processors.format_exc_info,
           structlog.processors.UnicodeDecoder(),
           structlog.processors.ExceptionPrettyPrinter(),
           structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
       ],
       context_class=structlog.threadlocal.wrap_dict(dict),
       logger_factory=structlog.stdlib.LoggerFactory(),
       wrapper_class=structlog.stdlib.BoundLogger,
       cache_logger_on_first_use=True,
   )

Start logging with ``structlog`` instead of ``logging``.

.. code-block:: python

   import structlog
   logger = structlog.get_logger(__name__)

Extending Request Log Metadata
------------------------------

By default only a ``request_id`` and the ``user_id`` are bound from the request but pertinent log metadata may vary from a project to another.

If you need to add more metadata from the request you can implement a convenient signal receiver to bind them.

.. code-block:: python

   from django.dispatch import receiver

   from django_structlog.signals import bind_extra_request_metadata


   @receiver(bind_extra_request_metadata)
   def bind_user_email(request, logger, **kwargs):
       logger.bind(user_email=getattr(request.user, 'email', ''))

Example outputs
---------------

Flat lines file (\ ``logs/flat_lines.log``\ )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   timestamp='2019-04-13T19:39:29.321453Z' level='info' event='Request started' logger='django_structlog.middlewares.request' request_id='c53dff1d-3fc5-4257-a78a-9a567c937561' user_id=1 ip='0.0.0.0' request=<WSGIRequest: GET '/'> user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
   timestamp='2019-04-13T19:39:29.345207Z' level='info' event='Request finished' logger='django_structlog.middlewares.request' request_id='c53dff1d-3fc5-4257-a78a-9a567c937561' user_id=1 ip='0.0.0.0' code=200
   timestamp='2019-04-13T19:39:31.086155Z' level='info' event='Request started' logger='django_structlog.middlewares.request' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' request=<WSGIRequest: POST '/success_task'> user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
   timestamp='2019-04-13T19:39:31.089925Z' level='info' event='Enqueuing successful task' logger='django_structlog_demo_project.home.views' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0'
   timestamp='2019-04-13T19:39:31.147590Z' level='info' event='Task enqueued' logger='django_structlog.middlewares.celery' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' task_id='6b11fd80-3cdf-4de5-acc2-3fd4633aa654'
   timestamp='2019-04-13T19:39:31.153081Z' level='info' event='This is a successful task' logger='django_structlog_demo_project.taskapp.celery' task_id='6b11fd80-3cdf-4de5-acc2-3fd4633aa654' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0'
   timestamp='2019-04-13T19:39:31.160043Z' level='info' event='Request finished' logger='django_structlog.middlewares.request' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' code=201
   timestamp='2019-04-13T19:39:31.162372Z' level='info' event='Task success' logger='django_structlog.middlewares.celery' task_id='6b11fd80-3cdf-4de5-acc2-3fd4633aa654' request_id='3a8f801c-072b-4805-8f38-e1337f363ed4' user_id=1 ip='0.0.0.0' result='None'

Json file (\ ``logs/json.log``\ )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {"request_id": "c53dff1d-3fc5-4257-a78a-9a567c937561", "user_id": 1, "ip": "0.0.0.0", "request": "<WSGIRequest: GET '/'>", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36", "event": "Request started", "timestamp": "2019-04-13T19:39:29.321453Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"request_id": "c53dff1d-3fc5-4257-a78a-9a567c937561", "user_id": 1, "ip": "0.0.0.0", "code": 200, "event": "Request finished", "timestamp": "2019-04-13T19:39:29.345207Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "request": "<WSGIRequest: POST '/success_task'>", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36", "event": "Request started", "timestamp": "2019-04-13T19:39:31.086155Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "event": "Enqueuing successful task", "timestamp": "2019-04-13T19:39:31.089925Z", "logger": "django_structlog_demo_project.home.views", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "task_id": "6b11fd80-3cdf-4de5-acc2-3fd4633aa654", "event": "Task enqueued", "timestamp": "2019-04-13T19:39:31.147590Z", "logger": "django_structlog.middlewares.celery", "level": "info"}
   {"task_id": "6b11fd80-3cdf-4de5-acc2-3fd4633aa654", "request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "event": "This is a successful task", "timestamp": "2019-04-13T19:39:31.153081Z", "logger": "django_structlog_demo_project.taskapp.celery", "level": "info"}
   {"request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "code": 201, "event": "Request finished", "timestamp": "2019-04-13T19:39:31.160043Z", "logger": "django_structlog.middlewares.request", "level": "info"}
   {"task_id": "6b11fd80-3cdf-4de5-acc2-3fd4633aa654", "request_id": "3a8f801c-072b-4805-8f38-e1337f363ed4", "user_id": 1, "ip": "0.0.0.0", "result": "None", "event": "Task success", "timestamp": "2019-04-13T19:39:31.162372Z", "logger": "django_structlog.middlewares.celery", "level": "info"}

Running the tests
-----------------

Note: For the moment redis is needed to run the tests. The easiest way start docker's demo. 

.. code-block:: bash

   docker-compose up --build

In another shell

.. code-block:: bash

   pip install -r requirement/base.txt
   pytest

Demo app
--------

.. code-block:: bash

   docker-compose up --build

Open ``http://0.0.0.0:8000/`` in your browser.

Navigate while looking into the log files and shell's output. 

Versioning
----------

We use `SemVer <http://semver.org/>`_ for versioning. For the versions available, see the `tags on this repository <https://github.com/jrobichaud/django-structlog/tags>`_. 

Authors
-------


* **Jules Robichaud-Gagnon** - *Initial work* - `jrobichaud <https://github.com/jrobichaud>`_

See also the list of `contributors <https://github.com/jrobichaud/django-structlog/contributors>`_ who participated in this project.

License
-------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/jrobichaud/django-structlog/blob/master/LICENSE.rst>`_ file for details

Acknowledgments
---------------


* Big thanks to `@ferd <https://github.com/ferd>`_ for his `bad opinions <https://ferd.ca/erlang-otp-21-s-new-logger.html>`_ that inspired the author enough to spend time on this library. 
* `This issue <https://github.com/hynek/structlog/issues/175>`_ helped the author to figure out how to integrate ``structlog`` in Django.
