from django.test import TestCase
import structlog

from django_structlog import processors


logger = structlog.getLogger(__name__)


class TestInjectContextDict(TestCase):
    def tearDown(self):
        structlog.contextvars.clear_contextvars()

    def test(self):
        event_dict = {}
        structlog.contextvars.bind_contextvars(foo="bar")
        processors.inject_context_dict(None, None, event_dict)

        self.assertDictEqual({"foo": "bar"}, event_dict)
