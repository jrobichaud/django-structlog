.. _django_tasks_integration:

Django Tasks Integration
========================

We are referring to `Django's django.tasks <https://docs.djangoproject.com/en/dev/topics/tasks/>`_ and not `django-tasks backport <https://pypi.org/project/django-tasks/>`_.

You will require a backend compatible with Django's task system.

Getting Started with Django Tasks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Replace your requirements
-------------------------

First of all, make sure your ``django-structlog`` installation knows you use ``django.tasks`` in order to validate compatibility with your installed version. See `Installing “Extras” <https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras>`_ for more information.

Replace ``django-structlog`` with ``django-structlog[django-tasks]`` in your ``requirements.txt``.

.. code-block:: python

    django-structlog[django-tasks]==X.Y.Z

Enable celery Django Tasks Integration in your web app
------------------------------------------------------

.. code-block:: python

    DJANGO_TASKS_ENABLED = True

Signals
-------

See

:attr:`django_structlog.tasks.signals.bind_extra_task_metadata`
:attr:`django_structlog.tasks.signals.modify_context_before_task_publish`
:attr:`django_structlog.tasks.signals.pre_task_succeeded`
