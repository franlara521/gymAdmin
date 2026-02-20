from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from apps.accounts.mixins import StaffRequiredMixin
from apps.schedule.models import GymClass, Booking, ClassType
from apps.schedule.forms import GymClassForm, ClassTypeForm


class ClassListView(StaffRequiredMixin, ListView):
    model = GymClass
    template_name = "schedule/admin/class_list.html"
    context_object_name = "classes"
    paginate_by = 20

    def get_queryset(self):
        return (
            GymClass.objects
            .select_related("class_type", "instructor")
            .prefetch_related("bookings")
            .order_by("start_datetime")
        )


class ClassCreateView(StaffRequiredMixin, CreateView):
    model = GymClass
    form_class = GymClassForm
    template_name = "schedule/admin/class_form.html"
    success_url = reverse_lazy("admin_schedule:class_list")

    def form_valid(self, form):
        messages.success(self.request, "Clase creada correctamente.")
        return super().form_valid(form)


class ClassUpdateView(StaffRequiredMixin, UpdateView):
    model = GymClass
    form_class = GymClassForm
    template_name = "schedule/admin/class_form.html"
    success_url = reverse_lazy("admin_schedule:class_list")

    def form_valid(self, form):
        messages.success(self.request, "Clase actualizada correctamente.")
        return super().form_valid(form)


class ClassDeleteView(StaffRequiredMixin, DeleteView):
    model = GymClass
    template_name = "schedule/admin/class_confirm_delete.html"
    success_url = reverse_lazy("admin_schedule:class_list")

    def form_valid(self, form):
        messages.success(self.request, "Clase eliminada.")
        return super().form_valid(form)


class ClassAttendeeListView(StaffRequiredMixin, TemplateView):
    template_name = "schedule/admin/class_attendees.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        gym_class = get_object_or_404(GymClass, pk=self.kwargs["pk"])
        ctx["gym_class"] = gym_class
        ctx["bookings"] = gym_class.bookings.filter(status__in=["confirmed", "attended", "no_show"]).select_related("client")
        return ctx


class MarkAttendedView(StaffRequiredMixin, View):
    def post(self, request, pk, booking_pk):
        booking = get_object_or_404(Booking, pk=booking_pk, gym_class__pk=pk)
        new_status = request.POST.get("status", "attended")
        if new_status in ["attended", "no_show", "confirmed"]:
            booking.status = new_status
            booking.save()
        return redirect("admin_schedule:class_attendees", pk=pk)


class ClassTypeListView(StaffRequiredMixin, ListView):
    model = ClassType
    template_name = "schedule/admin/class_type_list.html"
    context_object_name = "class_types"


class ClassTypeCreateView(StaffRequiredMixin, CreateView):
    model = ClassType
    form_class = ClassTypeForm
    template_name = "schedule/admin/class_type_form.html"
    success_url = reverse_lazy("admin_schedule:class_types")

    def form_valid(self, form):
        messages.success(self.request, "Tipo de clase creado.")
        return super().form_valid(form)


class ClassTypeUpdateView(StaffRequiredMixin, UpdateView):
    model = ClassType
    form_class = ClassTypeForm
    template_name = "schedule/admin/class_type_form.html"
    success_url = reverse_lazy("admin_schedule:class_types")

    def form_valid(self, form):
        messages.success(self.request, "Tipo de clase actualizado.")
        return super().form_valid(form)
