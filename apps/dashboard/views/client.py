import json
from datetime import timedelta
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models.functions import TruncWeek
from apps.accounts.mixins import ClientRequiredMixin
from apps.schedule.models import Booking, GymClass


class ClientDashboardView(ClientRequiredMixin, TemplateView):
    template_name = "dashboard/client/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        twelve_weeks_ago = now - timedelta(weeks=12)

        # Asistencia personal por semana
        attendance_qs = (
            Booking.objects
            .filter(
                client=user,
                booked_at__gte=twelve_weeks_ago,
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
                "label": "Clases reservadas",
                "data": [item["count"] for item in attendance_qs],
                "borderColor": "#0d6efd",
                "backgroundColor": "rgba(13,110,253,0.1)",
                "tension": 0.3,
                "fill": True,
            }],
        })

        # Próximas clases
        ctx["upcoming_bookings"] = (
            Booking.objects
            .filter(
                client=user,
                status="confirmed",
                gym_class__start_datetime__gte=now,
                gym_class__is_cancelled=False,
            )
            .select_related("gym_class__class_type", "gym_class__instructor")
            .order_by("gym_class__start_datetime")[:5]
        )

        # Stats resumen
        ctx["total_confirmed"] = Booking.objects.filter(
            client=user, status__in=["confirmed", "attended"]
        ).count()
        ctx["total_attended"] = Booking.objects.filter(client=user, status="attended").count()
        ctx["active_plans"] = user.assigned_plans.filter(is_active=True).count()

        return ctx
