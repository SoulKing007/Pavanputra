from django.shortcuts import render, redirect
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

    return render(request, "registration/signup.html", {'form': form})  # Pass the form to the template


# Login view

def login_view(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid Username')
            return redirect('registration/login/')
        
        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('registration/login/')
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect('index')
    
    # Render the login page template (GET request)
    return render(request, 'registration/login.html')


# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('registration/logout.html')  # Redirect to login page after logout

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