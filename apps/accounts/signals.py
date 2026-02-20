from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import ClientProfile, TrainerProfile


@receiver(post_save, sender=User)
def create_profiles(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.is_superuser:
        # Superadmin: sin perfil adicional
        return
    if instance.is_staff:
        # Entrenador
        TrainerProfile.objects.get_or_create(user=instance)
    else:
        # Cliente
        ClientProfile.objects.get_or_create(user=instance)
