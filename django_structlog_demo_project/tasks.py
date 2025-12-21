import django

if django.VERSION >= (6, 0):
    import structlog
    from django.tasks import task

    @task
    def django_task():
        logger = structlog.getLogger(__name__)
        logger.info("This is a Django 6 native task using the built-in task framework")

        return "ok"
