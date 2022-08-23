from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Message(models.Model):
    sender = models.ForeignKey(User, null=True, default=None, related_name='sent_message', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, null=True, default=None, related_name='received_message', on_delete=models.CASCADE)
    message = models.TextField(max_length=1024)
    seen = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(auto_now=False, blank=True, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
