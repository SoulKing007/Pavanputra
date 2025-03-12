from django.contrib import admin
from .models import Booking, Tour, TourDeparture
from django.contrib.auth import get_user_model

CustomUser = get_user_model()  

# Register Tour model
@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = [
        'name',                # Tour name
        'price',                # Tour price
        'start_date',           # Tour start date
        'end_date',             # Tour end date
        'default_duration_days', # Duration in days
        'accommodation',        # Accommodation details
        'transportation',       # Transportation details
        'food_facilities',      # Food details
        'rating',               # Tour rating
        'reviews'               # Number of reviews
    ]
    list_editable = [
        'price',                # Make price editable directly in the list view
        'default_duration_days', # Make duration editable
        'start_date', 'end_date'
    ]
    search_fields = ['name', 'accommodation', 'transportation']
    list_filter = ['start_date', 'end_date', 'rating']  # Filters for easy search

# Register TourDeparture model
@admin.register(TourDeparture)
class TourDepartureAdmin(admin.ModelAdmin):
    list_display = ('tour', 'departure_date', 'duration_days', 'available_slots', 'end_date')
    list_editable = ('duration_days', 'available_slots')  # Editable fields
    list_filter = ('departure_date', 'tour')
    search_fields = ('tour__name',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'tour', 'tour_departure', 'number_of_people', 'price', 'total_price'
    )
    search_fields = ('user__username', 'tour__name', 'full_name', 'email')
    list_filter = ('tour', 'tour_departure__departure_date', 'state', 'city')

    # Custom admin for CustomUser to show booking count
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'booking_count')  # Add booking count column

    def booking_count(self, obj):
        # Count how many bookings each user has
        return obj.bookings.count()

    booking_count.short_description = 'Total Bookings'  # Column name in admin

# Unregister and register the custom user model
admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)

from .models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback_text', 'submitted_at')  # Ensure 'created_at' exists in the model
    search_fields = ('user__username', 'feedback_text')      # Enable search by username and feedback
    list_filter = ('submitted_at',)                            # Ensure 'created_at' exists in the model

admin.site.register(Feedback, FeedbackAdmin)