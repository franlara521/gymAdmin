from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ClassType(models.Model):
    name = models.CharField("Nombre", max_length=100)
    description = models.TextField("Descripción", blank=True)
    default_duration_minutes = models.PositiveIntegerField("Duración por defecto (min)", default=60)
    color = models.CharField("Color (hex)", max_length=7, default="#0d6efd")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tipo de clase"
        verbose_name_plural = "Tipos de clase"
        ordering = ["name"]


class GymClass(models.Model):
    class_type = models.ForeignKey(
        ClassType, on_delete=models.PROTECT, related_name="instances",
        verbose_name="Tipo de clase"
    )
    instructor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="taught_classes", verbose_name="Instructor",
        limit_choices_to={"is_staff": True},
    )
    start_datetime = models.DateTimeField("Inicio")
    end_datetime = models.DateTimeField("Fin")
    capacity = models.PositiveIntegerField("Aforo máximo", default=10)
    location = models.CharField("Ubicación", max_length=200, blank=True)
    is_cancelled = models.BooleanField("Cancelada", default=False)
    notes = models.TextField("Notas", blank=True)

    @property
    def spots_available(self):
        return max(0, self.capacity - self.bookings.filter(status="confirmed").count())

    @property
    def is_full(self):
        return self.spots_available == 0

    @property
    def confirmed_count(self):
        return self.bookings.filter(status="confirmed").count()

    def __str__(self):
        return f"{self.class_type.name} — {self.start_datetime:%d/%m/%Y %H:%M}"

    class Meta:
        verbose_name = "Clase"
        verbose_name_plural = "Clases"
        ordering = ["start_datetime"]


class Booking(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmada"),
        ("cancelled", "Cancelada"),
        ("waitlisted", "Lista de espera"),
        ("attended", "Asistió"),
        ("no_show", "No se presentó"),
    ]

    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings", verbose_name="Cliente"
    )
    gym_class = models.ForeignKey(
        GymClass, on_delete=models.CASCADE, related_name="bookings", verbose_name="Clase"
    )
    status = models.CharField("Estado", max_length=15, choices=STATUS_CHOICES, default="confirmed")
    booked_at = models.DateTimeField("Reservado el", auto_now_add=True)
    cancelled_at = models.DateTimeField("Cancelado el", null=True, blank=True)

    def __str__(self):
        return f"{self.client.get_full_name() or self.client.username} → {self.gym_class}"

    class Meta:
        unique_together = ("client", "gym_class")
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-booked_at"]
