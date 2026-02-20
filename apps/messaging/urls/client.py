from django.urls import path
from apps.messaging.views import client as views

urlpatterns = [
    path("", views.ClientInboxView.as_view(), name="inbox"),
    path("send/", views.SendMessageView.as_view(), name="send"),
    path("messages/", views.MessageListPartialView.as_view(), name="message_list"),
]
