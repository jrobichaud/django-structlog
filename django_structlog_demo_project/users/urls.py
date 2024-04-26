from django.urls import re_path

from django_structlog_demo_project.users.views import (
    user_list_view,
    user_redirect_view,
    user_update_view,
    user_detail_view,
)

app_name = "users"
urlpatterns = [
    re_path(r"^$", view=user_list_view, name="list"),
    re_path(r"~redirect/", view=user_redirect_view, name="redirect"),
    re_path(r"~update/", view=user_update_view, name="update"),
    re_path(r"^(?P<username>(\w|\.)+)/", view=user_detail_view, name="detail"),
]
