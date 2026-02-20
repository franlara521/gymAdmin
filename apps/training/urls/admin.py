from django.urls import path
from apps.training.views import admin as views

urlpatterns = [
    path("", views.PlanListView.as_view(), name="plan_list"),
    path("create/", views.PlanCreateView.as_view(), name="plan_create"),
    path("<int:pk>/", views.PlanDetailView.as_view(), name="plan_detail"),
    path("<int:pk>/edit/", views.PlanEditView.as_view(), name="plan_edit"),
    path("<int:pk>/delete/", views.PlanDeleteView.as_view(), name="plan_delete"),
]
