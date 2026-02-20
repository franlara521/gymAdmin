from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from apps.accounts.mixins import ClientRequiredMixin
from apps.accounts.models import ClientProfile
from apps.accounts.forms import ClientProfileForm


class ClientHomeView(ClientRequiredMixin, TemplateView):
    template_name = "accounts/client/home.html"


class ClientProfileView(ClientRequiredMixin, UpdateView):
    model = ClientProfile
    form_class = ClientProfileForm
    template_name = "accounts/client/profile.html"
    success_url = reverse_lazy("client:profile")

    def get_object(self, queryset=None):
        return self.request.user.client_profile

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente.")
        return super().form_valid(form)
