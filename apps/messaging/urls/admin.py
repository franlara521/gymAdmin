from django.urls import path
from apps.messaging.views import admin as views

urlpatterns = [
    path("", views.AdminInboxView.as_view(), name="inbox"),
    path("<int:thread_pk>/", views.ThreadDetailView.as_view(), name="thread_detail"),
    path("<int:thread_pk>/reply/", views.ReplyView.as_view(), name="reply"),
]
