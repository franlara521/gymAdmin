from django.urls import path
from apps.training.views import trainer as views

urlpatterns = [
    path("", views.TrainerPlanListView.as_view(), name="plan_list"),
    path("create/", views.TrainerPlanCreateView.as_view(), name="plan_create"),
    path("<int:pk>/", views.TrainerPlanDetailView.as_view(), name="plan_detail"),
    path("<int:pk>/edit/", views.TrainerPlanEditView.as_view(), name="plan_edit"),
]
