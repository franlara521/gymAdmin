from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.db.models import Q
from apps.accounts.mixins import SuperAdminRequiredMixin
from apps.accounts.models import ClientProfile, TrainerProfile
from apps.accounts.forms import (
    ClientCreateForm, ClientEditForm, ClientProfileForm,
    TrainerCreateForm, TrainerEditForm, TrainerProfileForm,
)


# ── Admin Home ─────────────────────────────────────────────────────────────────

class AdminHomeView(SuperAdminRequiredMixin, TemplateView):
    template_name = "accounts/admin/home.html"


# ── Client CRUD ────────────────────────────────────────────────────────────────

class ClientListView(SuperAdminRequiredMixin, ListView):
    template_name = "accounts/admin/client_list.html"
    context_object_name = "clients"
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.filter(
            is_staff=False, is_superuser=False
        ).select_related("client_profile").order_by("last_name", "first_name")
        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(username__icontains=query)
                | Q(email__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ClientDetailView(SuperAdminRequiredMixin, DetailView):
    model = User
    template_name = "accounts/admin/client_detail.html"
    context_object_name = "client_user"

    def get_queryset(self):
        return User.objects.filter(is_staff=False, is_superuser=False).select_related(
            "client_profile"
        )


class ClientCreateView(SuperAdminRequiredMixin, View):
    template_name = "accounts/admin/client_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ClientCreateForm()})

    def post(self, request):
        form = ClientCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Cliente {user.get_full_name()} creado correctamente.")
            return redirect("gym_admin:client_detail", pk=user.pk)
        return render(request, self.template_name, {"form": form})


class ClientEditView(SuperAdminRequiredMixin, View):
    template_name = "accounts/admin/client_form.html"

    def get_user(self, pk):
        return get_object_or_404(User, pk=pk, is_staff=False, is_superuser=False)

    def get(self, request, pk):
        client_user = self.get_user(pk)
        form = ClientEditForm(instance=client_user)
        profile_form = ClientProfileForm(instance=client_user.client_profile)
        return render(request, self.template_name, {
            "form": form,
            "profile_form": profile_form,
            "client_user": client_user,
        })

    def post(self, request, pk):
        client_user = self.get_user(pk)
        form = ClientEditForm(request.POST, instance=client_user)
        profile_form = ClientProfileForm(
            request.POST, request.FILES, instance=client_user.client_profile
        )
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("gym_admin:client_detail", pk=pk)
        return render(request, self.template_name, {
            "form": form,
            "profile_form": profile_form,
            "client_user": client_user,
        })


class ClientToggleActiveView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        client_user = get_object_or_404(User, pk=pk, is_staff=False, is_superuser=False)
        profile = client_user.client_profile
        profile.is_active_member = not profile.is_active_member
        profile.save()
        status = "activado" if profile.is_active_member else "desactivado"
        messages.success(request, f"Cliente {status} correctamente.")
        return redirect("gym_admin:client_detail", pk=pk)


# ── Trainer CRUD ───────────────────────────────────────────────────────────────

class TrainerListView(SuperAdminRequiredMixin, ListView):
    template_name = "accounts/admin/trainer_list.html"
    context_object_name = "trainers"
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.filter(
            is_staff=True, is_superuser=False
        ).select_related("trainer_profile").order_by("last_name", "first_name")
        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(username__icontains=query)
                | Q(email__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class TrainerDetailView(SuperAdminRequiredMixin, DetailView):
    model = User
    template_name = "accounts/admin/trainer_detail.html"
    context_object_name = "trainer_user"

    def get_queryset(self):
        return User.objects.filter(is_staff=True, is_superuser=False).select_related(
            "trainer_profile"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        trainer = self.object
        from apps.schedule.models import GymClass
        from apps.training.models import TrainingPlan
        from django.utils import timezone
        ctx["upcoming_classes"] = GymClass.objects.filter(
            instructor=trainer,
            start_datetime__gte=timezone.now(),
            is_cancelled=False,
        ).order_by("start_datetime")[:5]
        ctx["recent_plans"] = TrainingPlan.objects.filter(
            created_by=trainer
        ).select_related("assigned_to").order_by("-created_at")[:5]
        return ctx


class TrainerCreateView(SuperAdminRequiredMixin, View):
    template_name = "accounts/admin/trainer_form.html"

    def get(self, request):
        return render(request, self.template_name, {
            "form": TrainerCreateForm(),
            "profile_form": TrainerProfileForm(),
        })

    def post(self, request):
        form = TrainerCreateForm(request.POST)
        profile_form = TrainerProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()  # señal crea TrainerProfile automáticamente
            # Actualizar el perfil recién creado por la señal
            profile = user.trainer_profile
            for field in ["phone", "specialty", "bio", "avatar"]:
                value = profile_form.cleaned_data.get(field)
                if value:
                    setattr(profile, field, value)
            profile.save()
            messages.success(request, f"Entrenador {user.get_full_name()} creado correctamente.")
            return redirect("gym_admin:trainer_detail", pk=user.pk)
        return render(request, self.template_name, {"form": form, "profile_form": profile_form})


class TrainerEditView(SuperAdminRequiredMixin, View):
    template_name = "accounts/admin/trainer_form.html"

    def get_user(self, pk):
        return get_object_or_404(User, pk=pk, is_staff=True, is_superuser=False)

    def get(self, request, pk):
        trainer_user = self.get_user(pk)
        form = TrainerEditForm(instance=trainer_user)
        profile_form = TrainerProfileForm(instance=trainer_user.trainer_profile)
        return render(request, self.template_name, {
            "form": form,
            "profile_form": profile_form,
            "trainer_user": trainer_user,
        })

    def post(self, request, pk):
        trainer_user = self.get_user(pk)
        form = TrainerEditForm(request.POST, instance=trainer_user)
        profile_form = TrainerProfileForm(
            request.POST, request.FILES, instance=trainer_user.trainer_profile
        )
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, "Entrenador actualizado correctamente.")
            return redirect("gym_admin:trainer_detail", pk=pk)
        return render(request, self.template_name, {
            "form": form,
            "profile_form": profile_form,
            "trainer_user": trainer_user,
        })
