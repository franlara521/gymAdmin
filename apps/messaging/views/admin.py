from django.views.generic import ListView, TemplateView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages as django_messages
from apps.accounts.mixins import StaffRequiredMixin
from apps.messaging.models import Thread, Message


class AdminInboxView(StaffRequiredMixin, ListView):
    model = Thread
    template_name = "messaging/admin/inbox.html"
    context_object_name = "threads"

    def get_queryset(self):
        return Thread.objects.select_related("client").order_by("-updated_at")


class ThreadDetailView(StaffRequiredMixin, TemplateView):
    template_name = "messaging/admin/thread_detail.html"

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


class ReplyView(StaffRequiredMixin, View):
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
        return redirect("admin_messaging:thread_detail", thread_pk=thread_pk)
