from django import forms
from .models import GymClass, ClassType


class ClassTypeForm(forms.ModelForm):
    class Meta:
        model = ClassType
        fields = ["name", "description", "default_duration_minutes", "color"]
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class GymClassForm(forms.ModelForm):
    class Meta:
        model = GymClass
        fields = [
            "class_type", "instructor", "start_datetime", "end_datetime",
            "capacity", "location", "notes",
        ]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["start_datetime"].initial = self.instance.start_datetime.strftime("%Y-%m-%dT%H:%M")
            self.fields["end_datetime"].initial = self.instance.end_datetime.strftime("%Y-%m-%dT%H:%M")
