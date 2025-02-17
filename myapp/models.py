from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Other fields of CustomUser
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    # Ensure the related_name for groups and user_permissions is unique
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Custom related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Custom related_name
        blank=True
    )
