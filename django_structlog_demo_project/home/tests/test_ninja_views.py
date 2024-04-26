import pytest
from ninja.testing import TestClient

from ..ninja_views import router

pytestmark = pytest.mark.django_db


class TestNinjaView:
    def test(self, caplog, request_factory):
        client = TestClient(router)
        response = client.get("/ninja")
        assert response.status_code == 200
        assert response.json() == {"result": "ok"}
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg["event"] == "This is a ninja structured log"
