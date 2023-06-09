from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Profile, CreatedDesign

@receiver(post_save, sender=User)
def usersave(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create( user = instance )