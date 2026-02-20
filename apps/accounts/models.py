from django.db import models
from django.contrib.auth.models import User


class TrainerProfile(models.Model):
    SPECIALTY_CHOICES = [
        ("crossfit", "CrossFit"),
        ("hiit", "HIIT"),
        ("yoga", "Yoga"),
        ("fuerza", "Fuerza"),
        ("cardio", "Cardio"),
        ("otro", "Otro"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="trainer_profile",
        limit_choices_to={"is_staff": True, "is_superuser": False},
    )
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    specialty = models.CharField(
        "Especialidad", max_length=20, choices=SPECIALTY_CHOICES, default="otro"
    )
    bio = models.TextField("Biografía", blank=True)
    avatar = models.ImageField("Foto", upload_to="trainers/", null=True, blank=True)
    joined_at = models.DateField("Incorporación", auto_now_add=True)

    def __str__(self):
        return f"Entrenador: {self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "Perfil de entrenador"
        verbose_name_plural = "Perfiles de entrenadores"
        ordering = ["user__last_name", "user__first_name"]


class ClientProfile(models.Model):
    GOAL_CHOICES = [
        ("weight_loss", "Pérdida de peso"),
        ("muscle_gain", "Ganancia muscular"),
        ("endurance", "Resistencia"),
        ("general", "Fitness general"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    date_of_birth = models.DateField("Fecha de nacimiento", null=True, blank=True)
    join_date = models.DateField("Fecha de alta", auto_now_add=True)
    goal = models.CharField("Objetivo", max_length=20, choices=GOAL_CHOICES, default="general")
    notes = models.TextField("Notas internas", blank=True)
    is_active_member = models.BooleanField("Miembro activo", default=True)
    avatar = models.ImageField("Foto", upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "Perfil de cliente"
        verbose_name_plural = "Perfiles de clientes"
        ordering = ["user__last_name", "user__first_name"]
