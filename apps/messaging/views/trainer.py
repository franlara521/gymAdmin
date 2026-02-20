from django.views.generic import ListView, TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages as django_messages
from apps.accounts.mixins import TrainerRequiredMixin
from apps.messaging.models import Thread, Message
from apps.schedule.models import GymClass


class TrainerInboxView(TrainerRequiredMixin, ListView):
    """Hilos de mensajes: clientes que tienen reservas en clases del entrenador."""
    template_name = "messaging/trainer/inbox.html"
    context_object_name = "threads"

    def get_queryset(self):
        # Obtener IDs de clientes con bookings en clases del entrenador
        client_ids = GymClass.objects.filter(
            instructor=self.request.user
        ).values_list("bookings__client_id", flat=True).distinct()
        return (
            Thread.objects
            .filter(client_id__in=client_ids)
            .select_related("client")
            .order_by("-updated_at")
        )


class TrainerThreadDetailView(TrainerRequiredMixin, TemplateView):
    template_name = "messaging/trainer/thread_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        thread = get_object_or_404(Thread, pk=self.kwargs["thread_pk"])
        # Marcar mensajes del cliente como leídos por el admin
        thread.messages.filter(sender=thread.client, is_read_by_admin=False).update(
            is_read_by_admin=True
        )
        ctx["thread"] = thread
        ctx["messages_list"] = thread.messages.all()
        return ctx


class TrainerReplyView(TrainerRequiredMixin, View):
    def post(self, request, thread_pk):
        thread = get_object_or_404(Thread, pk=thread_pk)
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                body=body,
                is_read_by_admin=True,
                is_read_by_client=False,
            )
            thread.save()
            django_messages.success(request, "Respuesta enviada.")
        return redirect("trainer_messaging:thread_detail", thread_pk=thread_pk)
