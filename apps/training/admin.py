from django.contrib import admin
from .models import TrainingPlan, PlanSection


class PlanSectionInline(admin.StackedInline):
    model = PlanSection
    extra = 1


@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ["title", "plan_type", "assigned_to", "created_by", "is_active", "created_at"]
    list_filter = ["plan_type", "is_active"]
    inlines = [PlanSectionInline]
