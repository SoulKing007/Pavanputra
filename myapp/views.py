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
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully.")
                return redirect('index')  # Redirect to home page after login
            else:
                messages.error(request, "Invalid username or password.")
    else:
        login_form = LoginForm()

    return render(request, 'login.html', {'login_form': login_form})


# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')  # Redirect to login page after logout
