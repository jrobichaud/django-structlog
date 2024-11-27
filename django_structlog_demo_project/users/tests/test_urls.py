import pytest
from django.conf import settings
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test_detail(user: settings.AUTH_USER_MODEL):
    route = f"/users/{user.username}/"
    assert reverse("users:detail", kwargs={"username": user.username}) == route
    assert resolve(route).view_name == "users:detail"


def test_detail_username_with_dot():
    route = "/users/foo.bar/"
    assert reverse("users:detail", kwargs={"username": "foo.bar"}) == route
    assert resolve(route).view_name == "users:detail"


def test_list():
    assert reverse("users:list") == "/users/"
    assert resolve("/users/").view_name == "users:list"


def test_update():
    assert reverse("users:update") == "/users/~update/"
    assert resolve("/users/~update/").view_name == "users:update"


def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"
