import django.dispatch

bind_extra_request_metadata = django.dispatch.Signal(providing_args=["request", "logger"])
