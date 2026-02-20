from django.views.generic import ListView, DetailView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from apps.accounts.mixins import StaffRequiredMixin
from apps.training.models import TrainingPlan
from apps.training.forms import TrainingPlanForm, PlanSectionFormSet


class PlanListView(StaffRequiredMixin, ListView):
    model = TrainingPlan
    template_name = "training/admin/plan_list.html"
    context_object_name = "plans"
    paginate_by = 20

    def get_queryset(self):
        return TrainingPlan.objects.select_related("assigned_to", "created_by").order_by("-created_at")


class PlanDetailView(StaffRequiredMixin, DetailView):
    model = TrainingPlan
    template_name = "training/admin/plan_detail.html"
    context_object_name = "plan"

    def get_queryset(self):
        return TrainingPlan.objects.prefetch_related("sections").select_related("assigned_to", "created_by")


class PlanCreateView(StaffRequiredMixin, View):
    template_name = "training/admin/plan_form.html"

    def get(self, request):
        form = TrainingPlanForm(initial={"assigned_to": request.GET.get("client")})
        formset = PlanSectionFormSet()
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request):
        form = TrainingPlanForm(request.POST)
        formset = PlanSectionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()
            formset.instance = plan
            formset.save()
            messages.success(request, f"Plan '{plan.title}' creado correctamente.")
            return redirect("admin_training:plan_detail", pk=plan.pk)
        return render(request, self.template_name, {"form": form, "formset": formset})


class PlanEditView(StaffRequiredMixin, View):
    template_name = "training/admin/plan_form.html"

    def get_object(self, pk):
        return get_object_or_404(TrainingPlan, pk=pk)

    def get(self, request, pk):
        plan = self.get_object(pk)
        form = TrainingPlanForm(instance=plan)
        formset = PlanSectionFormSet(instance=plan)
        return render(request, self.template_name, {"form": form, "formset": formset, "plan": plan})

    def post(self, request, pk):
        plan = self.get_object(pk)
        form = TrainingPlanForm(request.POST, instance=plan)
        formset = PlanSectionFormSet(request.POST, instance=plan)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Plan actualizado correctamente.")
            return redirect("admin_training:plan_detail", pk=plan.pk)
        return render(request, self.template_name, {"form": form, "formset": formset, "plan": plan})


class PlanDeleteView(StaffRequiredMixin, DeleteView):
    model = TrainingPlan
    template_name = "training/admin/plan_confirm_delete.html"
    success_url = reverse_lazy("admin_training:plan_list")

    def form_valid(self, form):
        messages.success(self.request, "Plan eliminado.")
        return super().form_valid(form)
