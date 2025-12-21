import pytest

from .. import views

pytestmark = pytest.mark.django_db
pytest_plugins = ("pytest_asyncio",)


class TestEnqueueSuccessfulTask:
    def test(self):
        response = views.enqueue_successful_task(None)
        assert response.status_code == 201


class TestEnqueueFailingTask:
    def test(self):
        response = views.enqueue_failing_task(None)
        assert response.status_code == 201


class TestEnqueueNestingTask:
    def test(self):
        response = views.enqueue_nesting_task(None)
        assert response.status_code == 201


class TestRaiseException:
    def test(self):
        with pytest.raises(Exception) as e:
            views.raise_exception(None)
        assert str(e.value) == "This is a view raising an exception."


class TestLogWithStandardLogger:
    def test(self):
        response = views.log_with_standard_logger(None)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAsyncView:
    async def test(self, mocker):
        mocker.patch("asyncio.sleep")
        response = await views.async_view(None)
        assert response.status_code == 200


class TestRevokeTask:
    def test(self):
        response = views.revoke_task(None)
        assert response.status_code == 201


class TestEnqueueUnknownTask:
    def test(self):
        response = views.enqueue_unknown_task(None)
        assert response.status_code == 201


class TestEnqueueRejectedTask:
    def test(self):
        response = views.enqueue_rejected_task(None)
        assert response.status_code == 201


@pytest.mark.asyncio
class TestAsyncStreamingViewView:
    async def test(self, mocker):
        response = await views.async_streaming_view(None)
        assert response.status_code == 200

        mocker.patch("asyncio.sleep")
        assert b"0" == await anext(response.streaming_content)
        assert b"1" == await anext(response.streaming_content)
        assert b"2" == await anext(response.streaming_content)
        assert b"3" == await anext(response.streaming_content)
        assert b"4" == await anext(response.streaming_content)

        with pytest.raises(StopAsyncIteration):
            await anext(response.streaming_content)


class TestSyncStreamingViewView:
    def test(self, mocker):
        response = views.sync_streaming_view(None)
        assert response.status_code == 200

        mocker.patch("time.sleep")
        assert b"0" == next(response.streaming_content)
        assert b"1" == next(response.streaming_content)
        assert b"2" == next(response.streaming_content)
        assert b"3" == next(response.streaming_content)
        assert b"4" == next(response.streaming_content)
        with pytest.raises(StopIteration):
            next(response.streaming_content)


class TestEnqueueDjangoTask:
    def test_django6(self, caplog, mocker):
        import django

        if django.VERSION < (6, 0):
            pytest.skip("Django 6+ required")

        mock_task = mocker.patch("django_structlog_demo_project.tasks.django_task")

        response = views.enqueue_django_task(None)
        assert response.status_code == 201

        mock_task.enqueue.assert_called_once()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Enqueuing Django 6 native task" in record.msg["event"]

    def test_django_less_than_6(self):
        import django

        if django.VERSION >= (6, 0):
            pytest.skip("Django < 6 required")

        response = views.enqueue_django_task(None)
        assert response.status_code == 200
