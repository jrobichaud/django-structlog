.. _commands:

Commands
========

Prerequisites
^^^^^^^^^^^^^

Install ``django-structlog`` with command support (it will install `django-extensions <https://django-extensions.readthedocs.io/en/latest/>`_).

.. code-block:: bash

   pip install django-structlog[commands]

Alternatively install `django-extensions <https://django-extensions.readthedocs.io/en/latest/>`_ directly:

.. code-block:: bash

   pip install django-extensions

Configuration
^^^^^^^^^^^^^

Enable ``django-structlog``'s command logging:

.. code-block:: python

   DJANGO_STRUCTLOG_COMMAND_LOGGING_ENABLED = True

Add ``django-extensions``'s `@signalcommand <https://django-extensions.readthedocs.io/en/latest/command_signals.html#using-pre-post-signals-on-your-own-commands>`_ to your commands

.. code-block:: python

    import structlog
    from django.core.management import BaseCommand
    from django_extensions.management.utils import signalcommand # <- add this

    logger = structlog.getLogger(__name__)


    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser.add_argument("foo", type=str)

        @signalcommand # <- add this
        def handle(self, foo, *args, **options):
            logger.info("my log", foo=foo)
            return 0

Results
^^^^^^^

Log will add ``command_name`` and ``command_id`` to the logs:

.. code-block:: bash

    $ python manage.py example_command bar
    2023-09-13T21:10:50.084368Z [info     ] command_started                [django_structlog.commands] command_name=django_structlog_demo_project.users.example_command command_id=be723d34-59f5-468e-9258-24232aa4cedd
    2023-09-13T21:10:50.085325Z [info     ] my log                         [django_structlog_demo_project.users.management.commands.example_command] command_id=be723d34-59f5-468e-9258-24232aa4cedd foo=bar
    2023-09-13T21:10:50.085877Z [info     ] command_finished               [django_structlog.commands] command_id=be723d34-59f5-468e-9258-24232aa4cedd


It also supports nested commands which will keep track of parent commands through ``parent_id``:

.. code-block:: bash

    $ python manage.py example_command bar
    2023-09-15T00:10:10.466616Z [info     ] command_started                [django_structlog.commands] command_id=f2a8c9a8-5aa3-4e22-b11c-f387449a34ed command_name=django_structlog_demo_project.users.example_command
    2023-09-15T00:10:10.467250Z [info     ] my log                         [django_structlog_demo_project.users.management.commands.example_command] command_id=f2a8c9a8-5aa3-4e22-b11c-f387449a34ed foo=bar
    2023-09-15T00:10:10.468176Z [info     ] command_started                [django_structlog.commands] baz=2 command_id=57524ccb-a8eb-4d30-a989-4e83ffdca9c0 command_name=django_structlog_demo_project.users.example_nested_command parent_command_id=f2a8c9a8-5aa3-4e22-b11c-f387449a34ed
    2023-09-15T00:10:10.468871Z [info     ] my nested log                  [django_structlog_demo_project.users.management.commands.example_nested_command] command_id=57524ccb-a8eb-4d30-a989-4e83ffdca9c0 parent_command_id=f2a8c9a8-5aa3-4e22-b11c-f387449a34ed
    2023-09-15T00:10:10.469418Z [info     ] command_finished               [django_structlog.commands] command_id=57524ccb-a8eb-4d30-a989-4e83ffdca9c0 parent_command_id=f2a8c9a8-5aa3-4e22-b11c-f387449a34ed
    2023-09-15T00:10:10.469964Z [info     ] my log 2                       [django_structlog_demo_project.users.management.commands.example_command] command_id=f2a8c9a8-5aa3-4e22-b11c-f387449a34ed
    2023-09-15T00:10:10.470585Z [info     ] command_finished               [django_structlog.commands] command_id=f2a8c9a8-5aa3-4e22-b11c-f387449a34ed
