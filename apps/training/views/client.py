from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from apps.accounts.mixins import ClientRequiredMixin
from apps.training.models import TrainingPlan


class PlanListView(ClientRequiredMixin, ListView):
    template_name = "training/client/plan_list.html"
    context_object_name = "plans"

    def get_queryset(self):
        return TrainingPlan.objects.filter(
            assigned_to=self.request.user, is_active=True
        ).order_by("-created_at")


class PlanDetailView(ClientRequiredMixin, DetailView):
    template_name = "training/client/plan_detail.html"
    context_object_name = "plan"

    def get_queryset(self):
        return TrainingPlan.objects.filter(
            assigned_to=self.request.user
        ).prefetch_related("sections")
