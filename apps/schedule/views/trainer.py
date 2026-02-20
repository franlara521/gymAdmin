from datetime import timedelta
from django.utils import timezone
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from apps.accounts.mixins import TrainerRequiredMixin
from apps.schedule.models import GymClass, Booking


def _get_trainer_week_context(request, offset=0):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    week_end = week_start + timedelta(days=7)
    classes = (
        GymClass.objects
        .filter(
            instructor=request.user,
            start_datetime__date__gte=week_start,
            start_datetime__date__lt=week_end,
            is_cancelled=False,
        )
        .select_related("class_type")
        .order_by("start_datetime")
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
        "today": today,
    }


class TrainerScheduleView(TrainerRequiredMixin, TemplateView):
    template_name = "schedule/trainer/schedule.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        offset = int(self.request.GET.get("week", 0))
        ctx.update(_get_trainer_week_context(self.request, offset))
        return ctx


class TrainerWeekGridView(TrainerRequiredMixin, TemplateView):
    """HTMX: grid semanal filtrado por entrenador."""
    template_name = "schedule/trainer/partials/week_grid.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        offset = int(self.request.GET.get("week", 0))
        ctx.update(_get_trainer_week_context(self.request, offset))
        return ctx


class TrainerClassDetailView(TrainerRequiredMixin, TemplateView):
    template_name = "schedule/trainer/class_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        gym_class = get_object_or_404(GymClass, pk=self.kwargs["pk"], instructor=self.request.user)
        ctx["gym_class"] = gym_class
        ctx["bookings"] = gym_class.bookings.filter(
            status__in=["confirmed", "attended", "no_show"]
        ).select_related("client")
        return ctx


class TrainerMarkAttendanceView(TrainerRequiredMixin, View):
    def post(self, request, pk, booking_pk):
        gym_class = get_object_or_404(GymClass, pk=pk, instructor=request.user)
        booking = get_object_or_404(Booking, pk=booking_pk, gym_class=gym_class)
        new_status = request.POST.get("status", "attended")
        if new_status in ["attended", "no_show", "confirmed"]:
            booking.status = new_status
            booking.save()
        return redirect("trainer_schedule:class_detail", pk=pk)
