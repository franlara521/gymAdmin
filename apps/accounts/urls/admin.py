from django.urls import path
from apps.accounts.views import admin as views

urlpatterns = [
    path("", views.AdminHomeView.as_view(), name="home"),
    # Clientes
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("clients/<int:pk>/edit/", views.ClientEditView.as_view(), name="client_edit"),
    path("clients/<int:pk>/toggle-active/", views.ClientToggleActiveView.as_view(), name="client_toggle_active"),
    # Entrenadores
    path("trainers/", views.TrainerListView.as_view(), name="trainer_list"),
    path("trainers/create/", views.TrainerCreateView.as_view(), name="trainer_create"),
    path("trainers/<int:pk>/", views.TrainerDetailView.as_view(), name="trainer_detail"),
    path("trainers/<int:pk>/edit/", views.TrainerEditView.as_view(), name="trainer_edit"),
]
