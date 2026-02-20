from django.urls import path
from apps.dashboard.views import admin as views

urlpatterns = [
    path("", views.AdminDashboardView.as_view(), name="dashboard"),
]
