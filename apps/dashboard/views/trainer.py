import json
from datetime import timedelta
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.db.models.functions import TruncWeek
from apps.accounts.mixins import TrainerRequiredMixin
from apps.schedule.models import GymClass, Booking
from apps.training.models import TrainingPlan


class TrainerDashboardView(TrainerRequiredMixin, TemplateView):
    template_name = "dashboard/trainer/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        eight_weeks_ago = now - timedelta(weeks=8)
        week_start = today - timedelta(days=today.weekday())

        trainer = self.request.user

        # Mis clases esta semana
        ctx["classes_this_week"] = GymClass.objects.filter(
            instructor=trainer,
            start_datetime__date__gte=week_start,
            start_datetime__date__lt=week_start + timedelta(days=7),
            is_cancelled=False,
        ).count()

        # Total de clientes únicos (con reservas en mis clases)
        ctx["total_clients"] = (
            Booking.objects
            .filter(gym_class__instructor=trainer, status__in=["confirmed", "attended"])
            .values("client")
            .distinct()
            .count()
        )

        # Tasa de asistencia
        total_confirmed = Booking.objects.filter(
            gym_class__instructor=trainer,
            status__in=["confirmed", "attended", "no_show"],
            gym_class__start_datetime__lt=now,
        ).count()
        total_attended = Booking.objects.filter(
            gym_class__instructor=trainer,
            status="attended",
        ).count()
        ctx["attendance_rate"] = (
            round(total_attended / total_confirmed * 100) if total_confirmed else 0
        )

        # Planes activos creados por mí
        ctx["active_plans"] = TrainingPlan.objects.filter(
            created_by=trainer, is_active=True
        ).count()

        # Asistencia por semana en mis clases (últimas 8 semanas)
        attendance_qs = (
            Booking.objects
            .filter(
                gym_class__instructor=trainer,
                booked_at__gte=eight_weeks_ago,
                status__in=["confirmed", "attended"],
            )
            .annotate(week=TruncWeek("booked_at"))
            .values("week")
            .annotate(count=Count("id"))
            .order_by("week")
        )
        ctx["attendance_chart_data"] = json.dumps({
            "labels": [item["week"].strftime("%d %b") for item in attendance_qs],
            "datasets": [{
                "label": "Reservas en mis clases",
                "data": [item["count"] for item in attendance_qs],
                "borderColor": "#fd7e14",
                "backgroundColor": "rgba(253,126,20,0.1)",
                "tension": 0.3,
                "fill": True,
            }],
        })

        # Próximas clases
        ctx["upcoming_classes"] = GymClass.objects.filter(
            instructor=trainer,
            start_datetime__gte=now,
            is_cancelled=False,
        ).select_related("class_type").prefetch_related("bookings").order_by("start_datetime")[:8]

        return ctx
