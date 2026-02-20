from datetime import timedelta
from django.utils import timezone
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from apps.accounts.mixins import ClientRequiredMixin
from apps.schedule.models import GymClass, Booking


def _get_week_context(request, offset=0):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    week_end = week_start + timedelta(days=7)
    classes = (
        GymClass.objects
        .filter(start_datetime__date__gte=week_start, start_datetime__date__lt=week_end, is_cancelled=False)
        .select_related("class_type", "instructor")
        .order_by("start_datetime")
    )
    user_booked = set(
        request.user.bookings.filter(status="confirmed").values_list("gym_class_id", flat=True)
    )
    days = [week_start + timedelta(days=i) for i in range(7)]
    days_classes = {d: [] for d in days}
    for cls in classes:
        day = cls.start_datetime.date()
        if day in days_classes:
            days_classes[day].append(cls)

    return {
        "week_start": week_start,
        "week_end": week_end - timedelta(days=1),
        "offset": offset,
        "days_classes": [(d, days_classes[d]) for d in days],
        "user_booked": user_booked,
        "today": today,
    }


class ScheduleView(ClientRequiredMixin, TemplateView):
    template_name = "schedule/client/schedule.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        offset = int(self.request.GET.get("week", 0))
        ctx.update(_get_week_context(self.request, offset))
        return ctx


class WeekGridPartialView(ClientRequiredMixin, TemplateView):
    """Devuelve solo el grid de la semana para HTMX."""
    template_name = "schedule/client/partials/week_grid.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        offset = int(self.request.GET.get("week", 0))
        ctx.update(_get_week_context(self.request, offset))
        return ctx


class BookClassView(ClientRequiredMixin, View):
    def post(self, request, pk):
        gym_class = get_object_or_404(GymClass, pk=pk, is_cancelled=False)
        error = None

        if gym_class.is_full:
            error = "La clase está completa"
        else:
            booking, created = Booking.objects.get_or_create(
                client=request.user,
                gym_class=gym_class,
                defaults={"status": "confirmed"},
            )
            if not created:
                if booking.status == "cancelled":
                    booking.status = "confirmed"
                    booking.cancelled_at = None
                    booking.save()

        html = render_to_string(
            "schedule/client/partials/class_card.html",
            {"cls": gym_class, "booked": not error, "error": error, "user_booked": {gym_class.pk}},
            request=request,
        )
        return HttpResponse(html)


class CancelBookingView(ClientRequiredMixin, View):
    def post(self, request, pk):
        from django.utils import timezone as tz
        gym_class = get_object_or_404(GymClass, pk=pk)
        booking = get_object_or_404(Booking, client=request.user, gym_class=gym_class)
        booking.status = "cancelled"
        booking.cancelled_at = tz.now()
        booking.save()

        html = render_to_string(
            "schedule/client/partials/class_card.html",
            {"cls": gym_class, "booked": False, "user_booked": set()},
            request=request,
        )
        return HttpResponse(html)


class AttendanceHistoryView(ClientRequiredMixin, TemplateView):
    template_name = "schedule/client/history.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["bookings"] = (
            Booking.objects
            .filter(client=self.request.user)
            .exclude(status="cancelled")
            .select_related("gym_class__class_type", "gym_class__instructor")
            .order_by("-gym_class__start_datetime")
        )
        return ctx
