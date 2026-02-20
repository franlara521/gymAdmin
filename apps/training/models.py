from django.db import models
from django.contrib.auth.models import User


class TrainingPlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ("training", "Plan de entrenamiento"),
        ("diet", "Plan de dieta"),
        ("combined", "Plan combinado"),
    ]

    title = models.CharField("Título", max_length=200)
    plan_type = models.CharField("Tipo", max_length=10, choices=PLAN_TYPE_CHOICES)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_plans",
        verbose_name="Creado por", limit_choices_to={"is_staff": True},
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_plans",
        verbose_name="Asignado a",
    )
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)
    is_active = models.BooleanField("Activo", default=True)
    notes = models.TextField("Notas del admin", blank=True)

    def __str__(self):
        return f"{self.title} → {self.assigned_to.get_full_name() or self.assigned_to.username}"

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["-created_at"]


class PlanSection(models.Model):
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField("Título de sección", max_length=200)
    order = models.PositiveIntegerField("Orden", default=0)
    content = models.TextField("Contenido")

    def __str__(self):
        return f"{self.plan.title} / {self.title}"

    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
        ordering = ["order"]
