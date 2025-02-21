from django.contrib.auth.models import AbstractUser, User
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
    
    # Model to represent a Tour
class Tour(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_slots = models.IntegerField(default=0)  # Number of available spots for the tour

    def __str__(self):
        return self.name


# Model to represent a Booking for a specific Tour
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    number_of_people = models.IntegerField()
    special_requests = models.TextField(blank=True)  # Optional field for special requests

    def __str__(self):
        return f"Booking for {self.full_name} on {self.tour.name}"

class State(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-increment ID
    state_id = models.IntegerField(unique=True)  # External state ID
    state_name = models.CharField(max_length=100)

    class Meta:
        managed = False  
        db_table = 'States'  

    def __str__(self):
        return self.state_name


class City(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-increment ID
    city_name = models.CharField(max_length=100)
    city_id = models.IntegerField(unique=True)  # External city ID
    state = models.ForeignKey(State, on_delete=models.CASCADE, db_column='state_id')  # Match foreign key column

    class Meta:
        managed = False  
        db_table = 'City'  

    def __str__(self):
        return f"{self.city_name}, {self.state.state_name}"