from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True)
    goals = models.TextField(max_length=500, blank=True)
    weight = models.FloatField(default=-1.0)
    gender = models.CharField(max_length=20)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='members')

    def __str__(self):
        return "Profile of {}".format(user.get_username())

class Dietlog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    
    @classmethod
    def create(cls, user, name):
        dietlog = cls(user=user, name=name)
        
        return dietlog


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



