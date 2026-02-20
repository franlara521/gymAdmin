import json
from datetime import timedelta
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models.functions import TruncWeek
from apps.accounts.mixins import StaffRequiredMixin
from apps.accounts.models import ClientProfile
from apps.schedule.models import Booking, GymClass
from apps.messaging.models import Thread


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/admin/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        twelve_weeks_ago = now - timedelta(weeks=12)

        # Asistencia total por semana (últimas 12 semanas)
        attendance_qs = (
            Booking.objects
            .filter(booked_at__gte=twelve_weeks_ago, status__in=["confirmed", "attended"])
            .annotate(week=TruncWeek("booked_at"))
            .values("week")
            .annotate(count=Count("id"))
            .order_by("week")
        )
        ctx["attendance_chart_data"] = json.dumps({
            "labels": [item["week"].strftime("%d %b") for item in attendance_qs],
            "datasets": [{
                "label": "Reservas",
                "data": [item["count"] for item in attendance_qs],
                "borderColor": "#0d6efd",
                "backgroundColor": "rgba(13,110,253,0.1)",
                "tension": 0.3,
                "fill": True,
            }],
        })

        # Clases más populares (top 5 por reservas en últimas 12 semanas)
        popular_qs = (
            GymClass.objects
            .filter(start_datetime__gte=twelve_weeks_ago)
            .values("class_type__name")
            .annotate(count=Count("bookings"))
            .order_by("-count")[:5]
        )
        colors = ["#0d6efd", "#6610f2", "#6f42c1", "#d63384", "#dc3545"]
        ctx["popular_chart_data"] = json.dumps({
            "labels": [item["class_type__name"] for item in popular_qs],
            "datasets": [{
                "data": [item["count"] for item in popular_qs],
                "backgroundColor": colors[:len(list(popular_qs))],
            }],
        })

        # Stats resumen
        today = now.date()
        week_start = today - timedelta(days=today.weekday())
        ctx["total_active_clients"] = ClientProfile.objects.filter(is_active_member=True).count()
        ctx["total_clients"] = ClientProfile.objects.count()
        ctx["classes_this_week"] = GymClass.objects.filter(
            start_datetime__date__gte=week_start,
            start_datetime__date__lt=week_start + timedelta(days=7),
            is_cancelled=False,
        ).count()
        ctx["pending_messages"] = Thread.objects.filter(
            messages__sender__is_staff=False,
            messages__is_read_by_admin=False,
        ).distinct().count()
        ctx["bookings_this_week"] = Booking.objects.filter(
            booked_at__date__gte=week_start,
            status__in=["confirmed", "attended"],
        ).count()

        # Últimas 5 reservas
        ctx["recent_bookings"] = (
            Booking.objects
            .filter(status="confirmed")
            .select_related("client", "gym_class__class_type")
            .order_by("-booked_at")[:8]
        )

        return ctx
