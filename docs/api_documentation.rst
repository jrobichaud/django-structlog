API documentation
=================

django_structlog
^^^^^^^^^^^^^^^^

.. automodule:: django_structlog
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: django_structlog.middlewares
    :members: RequestMiddleware
    :undoc-members:
    :show-inheritance:

.. automodule:: django_structlog.signals
    :members: bind_extra_request_metadata, bind_extra_request_finished_metadata, bind_extra_request_failed_metadata

.. automodule:: django_structlog.processors
    :members: inject_context_dict
    :undoc-members:
    :show-inheritance:


django_structlog.celery
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: django_structlog.celery
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: django_structlog.celery.middlewares
    :members: CeleryMiddleware
    :undoc-members:
    :show-inheritance:

.. automodule:: django_structlog.celery.steps
    :members: DjangoStructLogInitStep
    :undoc-members:
    :show-inheritance:

.. automodule:: django_structlog.celery.signals
    :members: bind_extra_task_metadata, modify_context_before_task_publish, pre_task_succeeded
