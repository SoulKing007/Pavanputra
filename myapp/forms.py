from django import forms
from django.contrib.auth.models import User
from .models import Booking, Tour


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['tour', 'full_name', 'age', 'gender', 'email', 'phone_number', 'number_of_people', 'special_requests']

    # Add placeholders to each field
    tour = forms.ModelChoiceField(
        queryset=Tour.objects.all(),  # Get all available tours
        widget=forms.Select(attrs={'placeholder': 'Select a tour'}),
        empty_label="Choose a Tour",  # Optional: Add a label for the empty option
    )
    full_name = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )
    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter your age'})
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        widget=forms.Select(attrs={'placeholder': 'Select your gender'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )
    number_of_people = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter number of people'})
    )
    special_requests = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Any special requests? (optional)', 'rows': 3}),
        required=False
    )

    # Custom validation for number of people (must be <= available_slots)
    def clean_number_of_people(self):
        number_of_people = self.cleaned_data['number_of_people']
        tour = self.cleaned_data['tour']
        if number_of_people > tour.available_slots:
            raise forms.ValidationError(f"Only {tour.available_slots} spots are available for this tour.")
        return number_of_people
# Signup Form
class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'required': 'True'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'required': 'True'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': 'True'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'required': 'True'})
    )

    # Clean method to validate password confirmation
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # Ensure username has no spaces
        if " " in username:
            raise forms.ValidationError("Username should not contain spaces.")

        return cleaned_data

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'required': True})  
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': True})  
    )
