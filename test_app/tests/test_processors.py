from django.test import TestCase
import structlog

from django_structlog import processors


logger = structlog.getLogger(__name__)


class TestInjectContextDict(TestCase):
    def test(self):
        event_dict = {}
        with structlog.threadlocal.tmp_bind(logger):
            logger.bind(foo="bar")
            processors.inject_context_dict(None, None, event_dict)

        self.assertDictEqual({"foo": "bar"}, event_dict)
