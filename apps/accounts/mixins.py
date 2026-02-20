from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class SuperAdminRequiredMixin(LoginRequiredMixin):
    """Solo superusuarios. Redirige trainers y clientes a su portal."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            if request.user.is_staff:
                return redirect("trainer_dashboard:dashboard")
            return redirect("client_dashboard:dashboard")
        return super().dispatch(request, *args, **kwargs)


class TrainerRequiredMixin(LoginRequiredMixin):
    """Solo entrenadores (is_staff=True, is_superuser=False)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            return redirect("admin_dashboard:dashboard")
        if not request.user.is_staff:
            return redirect("client_dashboard:dashboard")
        return super().dispatch(request, *args, **kwargs)


class ClientRequiredMixin(LoginRequiredMixin):
    """Solo clientes (is_staff=False, is_superuser=False)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            return redirect("admin_dashboard:dashboard")
        if request.user.is_staff:
            return redirect("trainer_dashboard:dashboard")
        return super().dispatch(request, *args, **kwargs)


# Alias para compatibilidad con vistas admin existentes
StaffRequiredMixin = SuperAdminRequiredMixin
