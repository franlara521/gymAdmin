from django.contrib import admin
from .models import ClassType, GymClass, Booking


@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "default_duration_minutes", "color"]


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ["booked_at"]


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ["class_type", "start_datetime", "instructor", "capacity", "is_cancelled"]
    list_filter = ["is_cancelled", "class_type"]
    inlines = [BookingInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["client", "gym_class", "status", "booked_at"]
    list_filter = ["status"]
