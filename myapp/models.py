from datetime import timedelta
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
    phone = models.CharField(max_length=15, blank=True, null=True)  # Ensure this field exists

    def __str__(self):
        return self.username

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
    
class Tour(models.Model):
    name  = models.CharField(max_length=255)   
    description = models.TextField()
    start_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)  # Set a new default price
    end_date = models.DateField()
    default_duration_days = models.PositiveIntegerField(default=7)  # Default trip duration
    accommodation = models.CharField(max_length=100, default='5-star accommodation')
    transportation = models.CharField(max_length=100, default='Transportation included')
    food_facilities = models.CharField(max_length=100, default='Food facilities included')
    rating = models.FloatField(default=4.5)
    reviews = models.PositiveIntegerField(default=100)
    image = models.ImageField(upload_to='tours/', default='default.jpg')
    def __str__(self):
        return self.name

class TourDeparture(models.Model):
    departure_date = models.DateField(default=timezone.now)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='departures')
    duration_days = models.PositiveIntegerField(default=7)  # Default from tour
    available_slots = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.tour.name} - {self.departure_date} ({self.duration_days} days, {self.available_slots} slots left)"
    
    def book_slots(self, num_people):
        if num_people > self.available_slots:
            raise ValueError("Not enough slots available.")
        self.available_slots -= num_people
        self.save()

    @property
    def end_date(self):
        return self.departure_date + timedelta(days=self.duration_days)

    def save(self, *args, **kwargs):
        """Ensure duration_days is set from the parent Tour if not provided."""
        if not self.duration_days:
            self.duration_days = self.tour.default_duration_days
        super().save(*args, **kwargs)



class ExtraPassenger(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='extra_passengers')
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE)
    tour_departure = models.ForeignKey('TourDeparture', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        return f"Passenger {self.age} years old - {self.gender}"

from django.core.exceptions import ValidationError

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='bookings')  # Link to user
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE)  # Link to Tour
    tour_departure = models.ForeignKey('TourDeparture', on_delete=models.CASCADE, null=True, blank=True)  # Specific departure

    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()

    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    number_of_people = models.PositiveIntegerField()

    special_requests = models.TextField(blank=True)  # Optional field

    state = models.ForeignKey('State', on_delete=models.CASCADE)
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        departure_info = f" ({self.tour_departure.departure_date})" if self.tour_departure else " (No Departure Selected)"
        return f"Booking for {self.full_name} - {self.tour.name}{departure_info}"

    def clean(self):
        """Validate available slots and ensure the departure matches the selected tour."""
        if not self.tour_departure:
            raise ValidationError("A departure date must be selected.")

        if self.number_of_people > self.tour_departure.available_slots:
            raise ValidationError(f"Only {self.tour_departure.available_slots} slots are available.")

        if self.tour_departure.tour != self.tour:
            raise ValidationError("Selected departure date does not match the selected tour.")

    def save(self, *args, **kwargs):
        
        """Ensure the price is updated based on the tour's price."""
        self.price = self.tour.price * self.number_of_people

        """Deduct available slots when saving a new booking."""
        self.clean()  # Ensure all validations are enforced

        if self.pk is None:  # Only deduct slots for new bookings
            if self.number_of_people > self.tour_departure.available_slots:
                raise ValidationError(f"Only {self.tour_departure.available_slots} slots are available.")

            self.tour_departure.available_slots -= self.number_of_people
            self.tour_departure.save()

        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        """Restore available slots when a booking is deleted."""
        if self.tour_departure:
            self.tour_departure.available_slots += self.number_of_people 
            self.tour_departure.save(update_fields=['available_slots'])
        
        super().delete(*args, **kwargs)  # Call the parent delete method
    @property
    def total_price(self):
        return self.price


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
    
class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_charge_id = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.stripe_charge_id}"
    
class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username}"