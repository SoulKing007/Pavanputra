from django import forms
from django.contrib.auth.models import User

# Signup Form
class SignupForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username', 'required': 'True'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'required': 'True'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': 'True'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'required': 'True'}))

    # Clean method to validate password confirmation
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username', 'required': 'True'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': 'True'}))
