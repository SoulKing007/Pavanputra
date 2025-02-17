from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class OTP(models.Model):
    # Use the custom user model defined in settings.AUTH_USER_MODEL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    expiry_time = models.DateTimeField()

    def is_expired(self):
        """Check if the OTP has expired"""
        return timezone.now() > self.expiry_time

    def __str__(self):
        return f"OTP for {self.user.username}"
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
