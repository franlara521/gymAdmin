from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from apps.accounts.mixins import TrainerRequiredMixin
from apps.accounts.models import TrainerProfile
from apps.accounts.forms import TrainerProfileForm


class TrainerHomeView(TrainerRequiredMixin, TemplateView):
    template_name = "accounts/trainer/home.html"


class TrainerProfileView(TrainerRequiredMixin, UpdateView):
    model = TrainerProfile
    form_class = TrainerProfileForm
    template_name = "accounts/trainer/profile.html"
    success_url = reverse_lazy("trainer:profile")

    def get_object(self, queryset=None):
        return self.request.user.trainer_profile

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente.")
        return super().form_valid(form)
