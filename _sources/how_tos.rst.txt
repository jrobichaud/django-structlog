.. _how_tos:

How Tos
=======

These are code snippets on how to achieve some specific use cases.

.. warning::
    Be aware they are untested. Please `open an issue <https://github.com/jrobichaud/django-structlog/issues/new?labels=how%20to>`_ if there are bugs in these examples or if you want to share some great examples that should be there.


Bind ``request_id`` to response's header
----------------------------------------

You can add the ``request_id`` to a custom response header ``X-Request-ID`` in order to trace the request by the caller.

Origin: `#231 <https://github.com/jrobichaud/django-structlog/issues/231>`_

.. code-block:: python

    from django.dispatch import receiver
    from django_structlog import signals
    import structlog


    @receiver(signals.update_failure_response)
    @receiver(signals.bind_extra_request_finished_metadata)
    def add_request_id_to_error_response(response, logger, **kwargs):
        context = structlog.contextvars.get_merged_contextvars(logger)
        response['X-Request-ID'] = context["request_id"]

Bind ``rest_framework_simplejwt`` token's user id
-------------------------------------------------

Bind token's user_id from `rest_framework_simplejwt <https://django-rest-framework-simplejwt.readthedocs.io/en/latest/>`_ to the request.

It is a workaround for ``restframework``'s non-standard authentication system.
It prevents access of the user in middlewares, therefore ``django-structlog`` cannot bind the ``user_id`` by default.

.. code-block:: python

    import structlog
    from django.dispatch import receiver
    from django_structlog.signals import bind_extra_request_metadata
    from rest_framework_simplejwt.tokens import UntypedToken

    @receiver(bind_extra_request_metadata)
    def bind_token_user_id(request, logger, **kwargs):
        try:
            header = request.META.get("HTTP_AUTHORIZATION")
            if header:
                raw_token = header.split()[1]
                token = UntypedToken(raw_token)
                user_id = token["user_id"]
                structlog.contextvars.bind_contextvars(user_id=user_id)
        except Exception:
            pass

Bind AWS's ``X-Amzn-Trace-Id``
------------------------------

See `Request tracing for your Application Load Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-request-tracing.html>`_

Origin: `#324 <https://github.com/jrobichaud/django-structlog/issues/324>`_

.. code-block:: python

    from django.dispatch import receiver
    from django_structlog import signals
    from django_structlog.middlewares.request import get_request_header
    import structlog

    @receiver(signals.bind_extra_request_metadata)
    def bind_trace_id(request, logger, **kwargs):
        trace_id = get_request_header(
             request, "x-amzn-trace-id", "HTTP_X_AMZN_TRACE_ID"
        )
        if trace_id:
            structlog.contextvars.bind_contextvars(trace_id=trace_id)

Filter logs from being recorded
-------------------------------

You can add a custom filter to prevent some specific logs from being recorded, based on your criteria

See `Django logging documentation <https://docs.djangoproject.com/en/dev/topics/logging/#topic-logging-parts-filters>`_


Origin: `#412 <https://github.com/jrobichaud/django-structlog/issues/412>`_

.. code-block:: python

    # your_project/logging/filters.py

    import logging

    class ExcludeEventsFilter(logging.Filter):
        def __init__(self, excluded_event_type=None):
            super().__init__()
            self.excluded_event_type = excluded_event_type

        def filter(self, record):
            if not isinstance(record.msg, dict) or self.excluded_event_type is None:
                return True  # Include the log message if msg is not a dictionary or excluded_event_type is not provided

            if record.msg.get('event') in self.excluded_event_type:
                return False  # Exclude the log message
            return True  # Include the log message


    # in your settings.py

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'filters': ['exclude_request_started']
            },
        },
        'filters': {
            'exclude_request_started': {
                '()': 'your_project.logging.filters.ExcludeEventsFilter',
                'excluded_event_type': ['request_started']  # Example excluding request_started event
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
