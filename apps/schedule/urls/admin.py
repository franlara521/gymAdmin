from django.urls import path
from apps.schedule.views import admin as views

urlpatterns = [
    path("", views.ClassListView.as_view(), name="class_list"),
    path("create/", views.ClassCreateView.as_view(), name="class_create"),
    path("<int:pk>/edit/", views.ClassUpdateView.as_view(), name="class_edit"),
    path("<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),
    path("<int:pk>/attendees/", views.ClassAttendeeListView.as_view(), name="class_attendees"),
    path("<int:pk>/mark-attended/<int:booking_pk>/", views.MarkAttendedView.as_view(), name="mark_attended"),
    path("types/", views.ClassTypeListView.as_view(), name="class_types"),
    path("types/create/", views.ClassTypeCreateView.as_view(), name="class_type_create"),
    path("types/<int:pk>/edit/", views.ClassTypeUpdateView.as_view(), name="class_type_edit"),
]
