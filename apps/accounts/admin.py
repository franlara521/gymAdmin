from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ClientProfile


class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [ClientProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
