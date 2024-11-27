from unittest.mock import patch

from django.test import TestCase

from django_structlog.celery import steps


class TestDjangoStructLogInitStep(TestCase):
    def test_call(self) -> None:
        with patch(
            "django_structlog.celery.receivers.CeleryReceiver.connect_worker_signals",
            autospec=True,
        ) as mock_connect:
            step = steps.DjangoStructLogInitStep(None)

        mock_connect.assert_called_once()

        self.assertIsNotNone(step.receiver)
