from django import forms
from django.forms import inlineformset_factory
from .models import TrainingPlan, PlanSection


class TrainingPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ["title", "plan_type", "assigned_to", "is_active", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        from django.contrib.auth.models import User
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(
            is_staff=False, is_superuser=False
        ).order_by("last_name", "first_name")
        self.fields["assigned_to"].label_from_instance = lambda u: u.get_full_name() or u.username


class PlanSectionForm(forms.ModelForm):
    class Meta:
        model = PlanSection
        fields = ["title", "order", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6}),
        }


PlanSectionFormSet = inlineformset_factory(
    TrainingPlan,
    PlanSection,
    form=PlanSectionForm,
    extra=1,
    can_delete=True,
)
