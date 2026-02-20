from django.urls import path
from apps.messaging.views import trainer as views

urlpatterns = [
    path("", views.TrainerInboxView.as_view(), name="inbox"),
    path("<int:thread_pk>/", views.TrainerThreadDetailView.as_view(), name="thread_detail"),
    path("<int:thread_pk>/reply/", views.TrainerReplyView.as_view(), name="reply"),
]
