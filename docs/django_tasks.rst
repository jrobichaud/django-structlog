.. _django_tasks_integration:

Django Tasks Integration
========================

We are referring to `Django's django.tasks <https://docs.djangoproject.com/en/dev/topics/tasks/>`_ and not `django-tasks backport <https://pypi.org/project/django-tasks/>`_.

This integration requires **Django 6.0+** and a `task backend <https://docs.djangoproject.com/en/dev/ref/tasks/#task-backends>`_ compatible with Django's task framework.

Getting Started with Django Tasks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to be able to support ``django.tasks`` you need to configure both your webapp and your workers.

How it works
------------

``django.tasks`` does not provide a way to attach custom metadata to a task. ``django-structlog`` stores the logging context in a dedicated Django cache instead:

1. When a task is enqueued (``task_enqueued`` signal), the current ``structlog`` context is saved in the ``django_structlog`` cache using the task's id as key.
2. When the task starts (``task_started`` signal), the context is cleared, ``task_id`` is bound and the saved context is retrieved from the cache and bound again.
3. When the task finishes (``task_finished`` signal), ``task_succeeded`` or ``task_failed`` is logged.

.. warning::
    The context is stored in the ``django_structlog`` cache. It should only contain data that can be serialized by your cache backend (``pickle`` for Django's built-in backends). You can use :ref:`django_tasks_modify_context_before_task_publish` to make sure this is the case.

Replace your requirements
-------------------------

First of all, make sure your ``django-structlog`` installation knows you use ``django.tasks`` in order to validate compatibility with your installed version. See `Installing “Extras” <https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras>`_ for more information.

Replace ``django-structlog`` with ``django-structlog[django-tasks]`` in your ``requirements.txt``.

.. code-block:: python

    django-structlog[django-tasks]==X.Y.Z

Enable Django Tasks integration in your web app
-----------------------------------------------

In your settings.py

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'django_structlog.middlewares.RequestMiddleware',
    ]

    DJANGO_STRUCTLOG_DJANGO_TASKS_ENABLED = True

Configure the ``django_structlog`` cache
----------------------------------------

The integration requires a cache named ``django_structlog``. Django will fail to start if it is missing while the integration is enabled.

.. code-block:: python

    CACHES = {
        "default": {
            # ...
        },
        "django_structlog": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379",
            # Must be longer than the delay between a task's enqueue and its start
            "TIMEOUT": 60 * 60 * 24,
        },
    }

.. warning::
    The cache must be **shared** between the processes enqueueing the tasks (ex: your web app) and the workers running them (ex: `Redis <https://docs.djangoproject.com/en/dev/topics/cache/#redis>`_, `Memcached <https://docs.djangoproject.com/en/dev/topics/cache/#memcached>`_ or `database caching <https://docs.djangoproject.com/en/dev/topics/cache/#database-caching>`_).

    ``LocMemCache`` is only suitable for tests or when the task runs in the same process (ex: ``django.tasks.backends.immediate.ImmediateBackend``).

.. note::
    Context entries are stored without an explicit timeout, therefore the cache's ``TIMEOUT`` applies (Django's default is 300 seconds). If a task starts after its entry expired, the task's logs will not contain the caller's context. Set a ``TIMEOUT`` greater than the longest delay you expect between a task being enqueued and being started (including tasks scheduled with ``run_after``).

    Entries are not deleted once the task has started, they are evicted when they expire.

Configure your workers
----------------------

Your workers must use the same settings as your web app: ``django_structlog`` in ``INSTALLED_APPS``, ``DJANGO_STRUCTLOG_DJANGO_TASKS_ENABLED = True`` and the same ``django_structlog`` cache. This way the receivers are connected when the worker initializes Django.

Make sure your worker also configures ``logging`` and ``structlog`` (see :doc:`getting_started`), otherwise the task events will not be rendered as expected.

.. _django_tasks_signals:

Signals
^^^^^^^

.. _django_tasks_modify_context_before_task_publish:

modify_context_before_task_publish
----------------------------------

You can connect to ``modify_context_before_task_publish`` signal in order to modify the metadata before it is stored in the cache.

By example you can strip down the ``context`` to keep only some of the keys:

.. code-block:: python

    from django.dispatch import receiver
    from django_structlog.tasks import signals

    @receiver(signals.modify_context_before_task_publish)
    def receiver_modify_context_before_task_publish(sender, signal, context, **kwargs):
        keys_to_keep = {"request_id", "parent_task_id"}
        new_dict = {key_to_keep: context[key_to_keep] for key_to_keep in keys_to_keep if key_to_keep in context}
        context.clear()
        context.update(new_dict)

See :attr:`django_structlog.tasks.signals.modify_context_before_task_publish`.

bind_extra_task_metadata
------------------------

You can optionally connect to ``bind_extra_task_metadata`` signal in order to bind more metadata to the logger or override existing bound metadata. This is called
when the task starts, after the context was restored and before ``task_started`` is logged.

.. code-block:: python

    from django.dispatch import receiver
    from django_structlog.tasks import signals
    import structlog

    @receiver(signals.bind_extra_task_metadata)
    def receiver_bind_extra_task_metadata(sender, signal, task_result=None, logger=None, **kwargs):
        structlog.contextvars.bind_contextvars(task_backend=task_result.backend)

See :attr:`django_structlog.tasks.signals.bind_extra_task_metadata`.

pre_task_succeeded
------------------

You can optionally connect to ``pre_task_succeeded`` signal in order to bind more metadata before ``task_succeeded`` is logged.

.. code-block:: python

    from django.dispatch import receiver
    from django_structlog.tasks import signals
    import structlog

    @receiver(signals.pre_task_succeeded)
    def receiver_pre_task_succeeded(sender, signal, logger=None, task_result=None, **kwargs):
        structlog.contextvars.bind_contextvars(result=str(task_result.return_value))

See :attr:`django_structlog.tasks.signals.pre_task_succeeded`.

Events and Metadata
^^^^^^^^^^^^^^^^^^^

See :ref:`django_tasks_events`.
