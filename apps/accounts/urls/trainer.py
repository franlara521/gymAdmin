from django.urls import path
from apps.accounts.views import trainer as views

urlpatterns = [
    path("", views.TrainerHomeView.as_view(), name="home"),
    path("profile/", views.TrainerProfileView.as_view(), name="profile"),
]
