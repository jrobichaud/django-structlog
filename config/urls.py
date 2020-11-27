from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from django_structlog_demo_project.home import views, api_views


def uncaught_exception_view(request):
    raise Exception("Uncaught Exception")


urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    url(
        r"^success_task$", views.enqueue_successful_task, name="enqueue_successful_task"
    ),
    url(r"^failing_task$", views.enqueue_failing_task, name="enqueue_failing_task"),
    url(r"^nesting_task$", views.enqueue_nesting_task, name="enqueue_nesting_task"),
    url(r"^raise_exception", views.raise_exception, name="raise_exception"),
    url(r"^standard_logger", views.log_with_standard_logger, name="standard_logger"),
    url(r"^api_view$", api_views.home_api_view, name="api_view"),
    url(
        r"^about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    # User management
    url(
        r"^users/",
        include("django_structlog_demo_project.users.urls", namespace="users"),
    ),
    url(r"^accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(
            r"^400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        url(
            r"^403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        url(
            r"^404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        url(r"^500/", default_views.server_error),
        url(r"^uncaught_exception/", uncaught_exception_view),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
