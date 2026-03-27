from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    profile_image = models.ImageField(
        upload_to='profile_pic/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True, max_length=200)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User')
    )

    favorites = models.ManyToManyField(
        'videos.Video',
        related_name='favorited_by',
        blank=True
    )

    roles = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='User')

    def __str__(self):
        return self.username
