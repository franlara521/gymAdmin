from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),

    # Raíz: redirige según tipo de usuario
    path("", include("apps.accounts.urls.root")),

    # Portal cliente
    path("portal/client/", include(("apps.accounts.urls.client", "client"))),
    path("portal/client/schedule/", include(("apps.schedule.urls.client", "client_schedule"))),
    path("portal/client/training/", include(("apps.training.urls.client", "client_training"))),
    path("portal/client/messages/", include(("apps.messaging.urls.client", "client_messaging"))),
    path("portal/client/dashboard/", include(("apps.dashboard.urls.client", "client_dashboard"))),

    # Portal entrenador
    path("portal/trainer/", include(("apps.accounts.urls.trainer", "trainer"))),
    path("portal/trainer/schedule/", include(("apps.schedule.urls.trainer", "trainer_schedule"))),
    path("portal/trainer/training/", include(("apps.training.urls.trainer", "trainer_training"))),
    path("portal/trainer/messages/", include(("apps.messaging.urls.trainer", "trainer_messaging"))),
    path("portal/trainer/dashboard/", include(("apps.dashboard.urls.trainer", "trainer_dashboard"))),

    # Portal superadmin gimnasio
    path("portal/admin/", include(("apps.accounts.urls.admin", "gym_admin"))),
    path("portal/admin/schedule/", include(("apps.schedule.urls.admin", "admin_schedule"))),
    path("portal/admin/training/", include(("apps.training.urls.admin", "admin_training"))),
    path("portal/admin/messages/", include(("apps.messaging.urls.admin", "admin_messaging"))),
    path("portal/admin/dashboard/", include(("apps.dashboard.urls.admin", "admin_dashboard"))),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
