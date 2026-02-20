from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ClientProfile, TrainerProfile


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ["phone", "date_of_birth", "goal", "avatar"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class ClientCreateForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class ClientEditForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


# ── Trainer forms ──────────────────────────────────────────────────────────────

class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = TrainerProfile
        fields = ["phone", "specialty", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class TrainerCreateForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
        return user


class TrainerEditForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
