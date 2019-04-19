import django.dispatch


bind_extra_task_metadata = django.dispatch.Signal(providing_args=["task", "logger"])
