from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
import os
import uuid
from random import randint
from imagekit.models import ProcessedImageField
def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]  #取“.”为分隔符，取最后一个
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join('user', str(instance.user_id), "avatar", filename)
class UserInfo(models.Model):
    user_id = models.PositiveIntegerField()
    avatar = ProcessedImageField(
        upload_to=user_directory_path,
        format='JPEG',
        options={'quality': 100},
        blank=True,
        null=True,
        verbose_name='头像',
    )
    def __str__(self):
        user = User.objects.get(id=self.user_id)
        return user.username
def get_default_avatar_url():
    return '/static/img/user_default_avatar/0' + str(randint(1, 8)) + '.svg'
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_avatar_url = get_default_avatar_url()
        UserInfo.objects.create(user_id=instance.id, avatar=default_avatar_url)
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     phone = models.CharField(max_length=20, blank=True)
#     avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
#     bio = models.TextField(max_length=500, blank=True)
#
#     def __str__(self):
#         return 'user {}'.format(self.user.username)










# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()







# Create your models here.
