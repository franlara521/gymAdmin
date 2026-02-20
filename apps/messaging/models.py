from django.db import models
from django.contrib.auth.models import User


class Thread(models.Model):
    """Un hilo de conversación por cliente."""
    client = models.OneToOneField(User, on_delete=models.CASCADE, related_name="message_thread")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def unread_by_admin_count(self):
        return self.messages.filter(sender=self.client, is_read_by_admin=False).count()

    @property
    def unread_by_client_count(self):
        return self.messages.filter(is_read_by_client=False).exclude(sender=self.client).count()

    @property
    def last_message(self):
        return self.messages.order_by("-sent_at").first()

    def __str__(self):
        return f"Conversación: {self.client.get_full_name() or self.client.username}"

    class Meta:
        verbose_name = "Hilo"
        verbose_name_plural = "Hilos"
        ordering = ["-updated_at"]


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField("Mensaje")
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read_by_admin = models.BooleanField(default=False)
    is_read_by_client = models.BooleanField(default=True)

    def __str__(self):
        return f"De {self.sender.username} — {self.sent_at:%d/%m %H:%M}"

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ["sent_at"]
