from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import SignupForm, LoginForm  # Make sure forms are defined properly
import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import OTP  # We'll create a model to store OTPs
# Home page view
def index(request):
    return render(request, 'index.html')

# Signup view
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            # Get cleaned data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Get the active user model (CustomUser or default User)
            User = get_user_model()

            # Check if username/email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already in use")
            else:
                # Create the user with create_user (handles password hashing)
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                messages.success(request, "Account created successfully!")
                return redirect('login')  # Redirect to login page after successful signup
        else:
            messages.error(request, "Form is not valid")
    else:
        form = SignupForm()  # Create an empty form instance

    return render(request, "signup.html", {'form': form})  # Pass the form to the template


# Login view
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Get the custom user model
        User = get_user_model()  # This will refer to 'pavanputra.CustomUser'

        try:
            # Try to get the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        # Check if user exists and password is correct
        if user is not None and user.check_password(password):
            login(request, user)  # Log the user in
            messages.success(request, "Logged in successfully.")
            return redirect('index')  # Redirect to the index page after login
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            # If login fails, return the form with the error message
            return render(request, 'login.html', {'email': email})

    return render(request, 'login.html')

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')  # Redirect to login page after logout

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user):
    """Send OTP to user email"""
    otp = generate_otp()

    # Store the OTP with an expiry time (e.g., 5 minutes)
    otp_entry = OTP.objects.create(
        user=user,
        otp=otp,
        expiry_time=timezone.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
    )

    # Send OTP to user's email
    send_mail(
        'Your OTP for Password Reset',
        f'Your OTP for password reset is: {otp}',
        'no-reply@example.com',
        [user.email],
        fail_silently=False,
    )

def password_reset_request(request):
    """Handle OTP request"""
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            send_otp_email(user)
            messages.success(request, 'OTP sent to your email.')
            return redirect('password_reset_verify')
        except User.DoesNotExist:
            messages.error(request, 'Email address not found.')
    return render(request, 'password_reset_request.html')

# View to handle OTP verification and password reset
def password_reset_verify(request):
    """Verify OTP and reset password"""
    if request.method == 'POST':
        email = request.POST['email']
        otp_entered = request.POST['otp']
        new_password = request.POST['new_password']

        try:
            user = User.objects.get(email=email)
            otp_entry = OTP.objects.filter(user=user, otp=otp_entered).first()

            if otp_entry and not otp_entry.is_expired():
                # Reset the password
                user.set_password(new_password)
                user.save()

                # Optionally, delete the OTP after it's used
                otp_entry.delete()

                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid or expired OTP.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    return render(request, 'password_reset_verify.html')