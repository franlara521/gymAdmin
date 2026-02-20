from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def portal_redirect(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard:dashboard")
    if request.user.is_staff:
        return redirect("trainer_dashboard:dashboard")
    return redirect("client_dashboard:dashboard")


urlpatterns = [
    path("", portal_redirect, name="root"),
]
