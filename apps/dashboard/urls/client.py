from django.urls import path
from apps.dashboard.views import client as views

urlpatterns = [
    path("", views.ClientDashboardView.as_view(), name="dashboard"),
]
