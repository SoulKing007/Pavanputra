from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

class CustomUser(AbstractUser):
    """Custom user model with additional fields."""
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)

    # Ensure unique related_name for groups and user_permissions
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",  # Custom related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",  # Custom related_name
        blank=True
    )

class OTP(models.Model):
    """OTP model linked to CustomUser."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    otp = models.CharField(max_length=6)
    expiry_time = models.DateTimeField()

    def is_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expiry_time

    def __str__(self):
        return f"OTP for {self.user.username} (Valid until {self.expiry_time})"
