from django.urls import path
from apps.schedule.views import trainer as views

urlpatterns = [
    path("", views.TrainerScheduleView.as_view(), name="schedule"),
    path("week/", views.TrainerWeekGridView.as_view(), name="week_grid"),
    path("class/<int:pk>/", views.TrainerClassDetailView.as_view(), name="class_detail"),
    path("class/<int:pk>/attend/<int:booking_pk>/", views.TrainerMarkAttendanceView.as_view(), name="mark_attendance"),
]
