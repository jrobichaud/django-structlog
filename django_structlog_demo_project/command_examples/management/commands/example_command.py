import structlog
from django.core import management
from django.core.management import BaseCommand
from django_extensions.management.utils import signalcommand

logger = structlog.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("foo", type=str)

    @signalcommand
    def handle(self, foo, *args, **options):
        logger.info("my log", foo=foo)
        management.call_command("example_nested_command", "buz", verbosity=0)
        logger.info("my log 2")
