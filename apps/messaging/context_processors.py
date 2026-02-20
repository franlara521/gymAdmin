def unread_count(request):
    """Inyecta el contador de mensajes no leídos en todos los templates."""
    if not request.user.is_authenticated:
        return {"unread_count": 0, "unread_admin_count": 0}

    if request.user.is_staff:
        from apps.messaging.models import Thread
        count = Thread.objects.filter(
            messages__sender__is_staff=False,
            messages__is_read_by_admin=False,
        ).distinct().count()
        return {"unread_count": 0, "unread_admin_count": count}
    else:
        try:
            count = request.user.message_thread.unread_by_client_count
        except Exception:
            count = 0
        return {"unread_count": count, "unread_admin_count": 0}
