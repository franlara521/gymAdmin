from django.urls import path
from apps.training.views import client as views

urlpatterns = [
    path("", views.PlanListView.as_view(), name="plan_list"),
    path("<int:pk>/", views.PlanDetailView.as_view(), name="plan_detail"),
]
