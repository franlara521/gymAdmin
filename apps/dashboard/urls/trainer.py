from django.urls import path
from apps.dashboard.views import trainer as views

urlpatterns = [
    path("", views.TrainerDashboardView.as_view(), name="dashboard"),
]
