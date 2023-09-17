import structlog
from django.core.management import BaseCommand
from django_extensions.management.utils import signalcommand

logger = structlog.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("baz", type=str)

    @signalcommand
    def handle(self, baz, *args, **options):
        logger.info("my nested log", baz=baz)
        return 0
