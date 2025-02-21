from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import EmailMessage
from .forms import SignupForm, LoginForm  # Make sure forms are defined properly
import random
from django.contrib.auth.decorators import login_required
import string
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import OTP, Booking  # We'll create a model to store OTPs
# Home page view
def index(request):
    return render(request, 'index.html')

# Signup view
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            User = get_user_model()

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already in use")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, "Account created successfully! You can now log in.")
                return redirect('login')  # Redirect only if user is created

        # If form is invalid, show errors
        messages.error(request, "Please correct the errors below.")

    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {'form': form})

# Login view

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('login')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('login')

        # Log in the user
        login(request, user)

        # Redirect to intended page (if coming from booking) or profile
        next_url = request.GET.get('next')  
        return redirect(next_url if next_url else 'profile')  # Redirect properly

    return render(request, 'registration/login.html')


# Logout view
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')  # Redirect to login page after logout
    return redirect('logout_confirm')  

@login_required
def logout_confirm_view(request):
    return render(request, 'registration/logout.html')

import logging

logger = logging.getLogger(__name__)  # Enable logging

def send_otp_email(user, otp):
    subject = "Your Password Reset OTP"
    message = f"Hello {user.username},\n\nYour OTP for password reset is: {otp}\n\nThis OTP is valid for 5 minutes."
    from_email = "niravthapa69@gmail.com"  # Replace with your email
    recipient_list = [user.email]

    logger.info(f"Sending OTP to {user.email}")  # Log email sending
    print(f"Sending OTP to {user.email}")  # Debugging print

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def generate_otp():
    """Generate a 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))

def password_reset_request(request):
    """Handle OTP request"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()

            # Save OTP in the database with expiry time
            OTP.objects.create(
                user=user,
                otp=otp,
                expiry_time=timezone.now() + timedelta(minutes=5)
            )

            send_otp_email(user, otp)  # Send OTP email
            messages.success(request, 'OTP sent to your email.')

            # Redirect to the verify OTP page with the email in URL
            return redirect(f'/password_reset/verify/?email={email}')
        except User.DoesNotExist:
            messages.error(request, 'Email address not found.')

    return render(request, 'registration/password_reset_request.html')


def password_reset_verify(request):
    """Verify OTP and reset password."""
    if request.method == 'GET':
        email = request.GET.get('email')  # Retrieve email from URL

    if request.method == 'POST':
        email = request.POST.get('email')  # Get email from form
        otp_entered = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        # Validate inputs
        if not email or not otp_entered or not new_password:
            messages.error(request, 'Missing required fields.')
            return render(request, 'registration/password_reset_verify.html')

        try:
            user = get_user_model().objects.get(email=email)
            otp_entry = OTP.objects.filter(user=user, otp=otp_entered).first()

            if otp_entry and not otp_entry.is_expired():
                user.set_password(new_password)
                user.save()
                otp_entry.delete()  # Delete OTP after use

                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid or expired OTP.')

        except get_user_model().DoesNotExist:
            messages.error(request, 'User not found.')

    return render(request, 'registration/password_reset_verify.html')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html') 


from .forms import BookingForm
from .models import Tour

@login_required(login_url='/login/')  # Redirect to login if not authenticated
def booking_view(request):
    tours = Tour.objects.filter(available_slots__gt=0)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            tour = form.cleaned_data['tour']
            number_of_people = form.cleaned_data['number_of_people']

            # Check slot availability
            if tour.available_slots >= number_of_people:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.save()

                # Update available slots
                tour.available_slots -= number_of_people
                tour.save()

                messages.success(request, 'Booking successful!')
                return redirect('booking_confirmation', booking_id=booking.id)
            else:
                messages.error(request, 'Not enough available slots.')

    else:
        form = BookingForm()

    return render(request, 'booking_page.html', {'form': form, 'tours': tours})

@login_required(login_url='/login/')
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'confirmation.html', {'booking': booking})

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'bookings': bookings})

def base(request):
    return render(request, 'base.html')


from .models import State, City

def get_states(request):
    states = list(State.objects.values('state_id', 'state_name'))
    return JsonResponse({'states': states})

def get_cities(request, state_id):
    cities = list(City.objects.filter(state__state_id=state_id).values('city_id', 'city_name'))
    return JsonResponse({'cities': cities})

def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)  # Ensure the user owns the booking
    booking.delete()
    messages.success(request, "Your booking has been deleted successfully.")
    return redirect('dashboard')