import pytest

from .. import api_views

pytestmark = pytest.mark.django_db


class TestApiView:
    def test(self, caplog, request_factory):
        response = api_views.home_api_view(request_factory.get("/"))
        assert response.status_code == 200
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg["event"] == "This is a rest-framework structured log"
