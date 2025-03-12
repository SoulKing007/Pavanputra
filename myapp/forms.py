from django import forms
from django.contrib.auth.models import User
from .models import Booking, City, State, Tour, TourDeparture
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Feedback
from myapp.models import CustomUser
User = get_user_model()
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User

class BookingForm(forms.ModelForm):
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'readonly': 'readonly'}), 
        required=False
    )  # Read-only price field
    class Meta:
        model = Booking
        fields = [
            'tour', 'tour_departure', 'full_name', 'age', 'gender', 'email', 
            'phone_number', 'number_of_people', 'state', 'city', 'special_requests'
        ]

    # Tour selection
    tour = forms.ModelChoiceField(
        queryset=Tour.objects.all(),
        widget=forms.Select(attrs={'id': 'id_tour'}),
        empty_label="Choose a Tour"
    )

    # Tour Departure (Filtered dynamically based on selected tour)
    tour_departure = forms.ModelChoiceField(
        queryset=TourDeparture.objects.none(),  # Will be populated dynamically
        widget=forms.Select(attrs={'id': 'id_tour_departure'}),
        empty_label="Select a Departure Date"
    )

    # Full name
    full_name = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )

    # Age (Minimum 18)
    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter your age'}),
        min_value=18,
        error_messages={'min_value': "You must be at least 18 years old to book."}
    )

    # Gender
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        widget=forms.Select()
    )

    # Email
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )

    # Phone Number
    phone_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )

    # Number of People
    number_of_people = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter number of people', 'id': 'id_number_of_people'}),
        min_value=1
    )

    # State selection
    state = forms.ModelChoiceField(
        queryset=State.objects.all(),
        widget=forms.Select(attrs={'id': 'id_state'}),
        empty_label="Select State"
    )

    # City selection (filtered dynamically)
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),  # Will be updated dynamically
        widget=forms.Select(attrs={'id': 'id_city'}),
        empty_label="Select City"
    )

    # Special Requests
    special_requests = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Any special requests? (optional)', 'rows': 3}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate cities based on selected state
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                self.fields['city'].queryset = City.objects.none()
        elif hasattr(self.instance, "pk") and self.instance.pk and self.instance.state:
            self.fields['city'].queryset = self.instance.state.city_set.all()

        # Dynamically populate tour departures based on selected tour
        if 'tour' in self.data:
            try:
                tour_id = int(self.data.get('tour'))
                self.fields['tour_departure'].queryset = TourDeparture.objects.filter(
                    tour_id=tour_id, available_slots__gt=0  # Only show available departures
                ).select_related("tour").order_by('departure_date')
            except (ValueError, TypeError):
                self.fields['tour_departure'].queryset = TourDeparture.objects.none()
        elif hasattr(self.instance, "pk") and self.instance.pk and self.instance.tour:
            self.fields['tour_departure'].queryset = self.instance.tour.departures.filter(available_slots__gt=0)

    def clean_number_of_people(self):
        """Ensure number of people does not exceed available slots."""
        number_of_people = self.cleaned_data.get('number_of_people')
        tour_departure = self.cleaned_data.get('tour_departure')

        if not tour_departure:
            raise forms.ValidationError("Please select a departure date.")

        tour_departure.refresh_from_db()  # Ensure latest slots are checked
        if number_of_people > tour_departure.available_slots:
            raise forms.ValidationError(f"Only {tour_departure.available_slots} spots are available for this departure.")

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

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']
        widgets = {
            'feedback_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your feedback here...'
            }),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone"]