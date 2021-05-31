from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import UserPreferences

user_model = get_user_model()
@receiver(post_save, sender=user_model)
def initialize_setting(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(username=instance)

@receiver(post_save, sender=user_model)
def save_default_setting(sender, instance, **kwargs):
    instance.userpreferences.save()