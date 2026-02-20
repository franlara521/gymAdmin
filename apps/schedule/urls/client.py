from django.urls import path
from apps.schedule.views import client as views

urlpatterns = [
    path("", views.ScheduleView.as_view(), name="schedule"),
    path("week/", views.WeekGridPartialView.as_view(), name="week_grid"),
    path("book/<int:pk>/", views.BookClassView.as_view(), name="book"),
    path("cancel/<int:pk>/", views.CancelBookingView.as_view(), name="cancel"),
    path("history/", views.AttendanceHistoryView.as_view(), name="history"),
]
