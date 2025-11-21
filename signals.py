from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User )
def create_user_profile(sender, instance, created, **kwargs):
    """Créer un profil d'utilisateur lorsque l'utilisateur est créé."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User )
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil d'utilisateur lorsque l'utilisateur est mis à jour."""
    instance.profile.save()


