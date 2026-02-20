from django.urls import path
from apps.accounts.views import client as views

urlpatterns = [
    path("", views.ClientHomeView.as_view(), name="home"),
    path("profile/", views.ClientProfileView.as_view(), name="profile"),
]
