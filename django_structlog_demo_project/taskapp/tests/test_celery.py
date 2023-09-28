import pytest

from .. import celery

pytestmark = pytest.mark.django_db


class TestSuccessfulTask:
    def test(self, caplog):
        celery.successful_task(foo="bar")
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg["event"] == "This is a successful task"


class TestFailingTask:
    def test(self):
        with pytest.raises(Exception) as e:
            celery.failing_task(foo="bar")
        assert str(e.value) == "This is a failed task"


class TestNestingTask:
    def test(self, caplog):
        celery.nesting_task()
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg["event"] == "This is a nesting task"


class TestNestedTask:
    def test(self, caplog):
        celery.nested_task()
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg["event"] == "This is a nested task"


class TestScheduledTask:
    def test(self, caplog):
        celery.scheduled_task()
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg["event"] == "This is a scheduled task"


class TestRejectedTask:
    def test(self):
        assert celery.rejected_task() is None


class TestCorruptRejectedTask:
    def test(self, caplog):
        task_id = "11111111-1111-1111-1111-111111111111"
        headers = dict(
            id=task_id,
            task="django_structlog_demo_project.taskapp.celery.rejected_task",
        )
        celery.corrupt_rejected_task(sender=None, headers=headers)
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg["event"] == "corrupting rejected_task"
        assert record.msg["task_id"] == task_id
        assert "task" not in headers

    def test_other_tasks_not_corrupted(self, caplog):
        task_id = "11111111-1111-1111-1111-111111111111"
        headers = dict(
            id=task_id,
            task="django_structlog_demo_project.taskapp.celery.successful_task",
        )
        celery.corrupt_rejected_task(sender=None, headers=headers)
        assert len(caplog.records) == 0
        assert (
            headers["task"]
            == "django_structlog_demo_project.taskapp.celery.successful_task"
        )
