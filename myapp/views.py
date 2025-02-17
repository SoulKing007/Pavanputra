from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import SignupForm, LoginForm  # Make sure forms are defined properly

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
