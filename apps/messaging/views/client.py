from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from apps.accounts.mixins import ClientRequiredMixin
from apps.messaging.models import Thread, Message


def get_or_create_thread(user):
    thread, _ = Thread.objects.get_or_create(client=user)
    return thread


class ClientInboxView(ClientRequiredMixin, TemplateView):
    template_name = "messaging/client/inbox.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        thread = get_or_create_thread(self.request.user)
        # Marcar mensajes del admin como leídos
        thread.messages.filter(is_read_by_client=False).exclude(
            sender=self.request.user
        ).update(is_read_by_client=True)
        ctx["thread"] = thread
        ctx["messages_list"] = thread.messages.all()
        return ctx


class MessageListPartialView(ClientRequiredMixin, TemplateView):
    """HTMX: refresca solo la lista de mensajes."""
    template_name = "messaging/client/partials/message_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        thread = get_or_create_thread(self.request.user)
        thread.messages.filter(is_read_by_client=False).exclude(
            sender=self.request.user
        ).update(is_read_by_client=True)
        ctx["thread"] = thread
        ctx["messages_list"] = thread.messages.all()
        return ctx


class SendMessageView(ClientRequiredMixin, View):
    def post(self, request):
        body = request.POST.get("body", "").strip()
        if not body:
            return HttpResponse(status=204)

        thread = get_or_create_thread(request.user)
        Message.objects.create(
            thread=thread,
            sender=request.user,
            body=body,
            is_read_by_admin=False,
            is_read_by_client=True,
        )
        thread.save()  # actualiza updated_at

        messages_list = thread.messages.all()
        html = render_to_string(
            "messaging/client/partials/message_list.html",
            {"thread": thread, "messages_list": messages_list},
            request=request,
        )
        return HttpResponse(html)
