import django
import pytest

if django.VERSION >= (6, 0):
    from .. import tasks

    pytestmark = pytest.mark.django_db

    class TestDjangoTask:
        def test(self, caplog):
            task_result = tasks.django_task.enqueue()
            assert task_result == "ok"

            assert len(caplog.records) == 1
            record = caplog.records[0]
            assert (
                record.msg["event"]
                == "This is a Django 6 native task using the built-in task framework"
            )
