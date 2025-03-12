from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from myapp.forms import ProfileUpdateForm
from django.contrib import messages
from django.core.mail import EmailMessage
from .forms import SignupForm, LoginForm  # Make sure forms are defined properly
import random
from django.template import TemplateDoesNotExist 
from django.contrib.auth.decorators import login_required
import string
from django.http import JsonResponse
from .models import City
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import OTP, Booking  # We'll create a model to store OTPs
from django.contrib.auth import  get_user_model
from django.http import JsonResponse
from .models import Tour, TourDeparture
from .models import State

def get_tour_departures(request):
    tour_id = request.GET.get('tour_id')

    if not tour_id:
        return JsonResponse({"error": "Tour ID is required", "departures": []}, status=400)

    try:
        departures = TourDeparture.objects.filter(
            tour_id=tour_id, available_slots__gt=0  # Only show departures with available slots
        ).order_by('departure_date').values("id", "departure_date", "available_slots")

        departures_list = [
            {"id": d["id"], "date": d["departure_date"].strftime("%Y-%m-%d"), "slots": d["available_slots"]}
            for d in departures
        ]

        return JsonResponse({"departures": departures_list})

    except Exception as e:
        return JsonResponse({"error": "An error occurred while fetching departures", "details": str(e), "departures": []}, status=500)


# Home page view
def index(request):
    states = State.objects.all()  
    tours = Tour.objects.all()  
    return render(request, 'index.html', {
        'tours': tours,
        'states': states
        
        })

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
User = get_user_model()
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username exists in the correct user model
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
    message = f"Hello {user.username},\n\nYour OTP for password reset is: {otp}\n\nThis OTP is valid for 5 minutes So Please be careful and note done the OTP ASAP."
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
            return redirect(f'/password_reset_verify/?email={email}')
        except User.DoesNotExist:
            messages.error(request, 'Email address not found.')

    return render(request, 'registration/password_reset_request.html')



def password_reset_verify(request):
    """Verify OTP and reset password."""
    if request.method == 'GET':
        email = request.GET.get('email')  # Retrieve email from URL
        print("GET Request Email:", email)  # Debug print
        return render(request, 'registration/password_reset_verify.html', {'email': email})

    if request.method == 'POST':
        email = request.POST.get('email')
        otp_entered = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        # Validate inputs
        if not email or not otp_entered or not new_password:
            messages.error(request, 'Missing required fields.')
            return render(request, 'registration/password_reset_verify.html', {'email': email})

        try:
            user = get_user_model().objects.get(email=email)
            otp_entry = OTP.objects.filter(user=user, otp=otp_entered).first()

            if otp_entry and not otp_entry.is_expired():
                user.set_password(new_password)
                
                # Validate and save password
                try:
                    user.full_clean()  # Check for validation errors
                    user.save()
                    otp_entry.delete()  # Delete OTP after successful password reset

                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('login')
                except Exception as e:
                    print("Password Save Error:", e)  # Debug print
                    messages.error(request, 'Invalid password. Please try a different one.')

            else:
                messages.error(request, 'Invalid or expired OTP.')

        except get_user_model().DoesNotExist:
            print("User Not Found for Email:", email)  # Debug print
            messages.error(request, 'User not found.')

    return render(request, 'registration/password_reset_verify.html', {'email': email})

@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})

from django.urls import reverse
from .forms import BookingForm
from .models import Tour

@login_required(login_url='/login/')  # Redirect to login if not authenticated
def booking_page(request):
    tours = Tour.objects.all()  # Fetch all tours
    form = BookingForm()  # Create an empty form
    return render(request, 'booking_page.html', {
        'form': form,
        'tours': tours,
        'selected_tour': None  # No pre-selected tour
    })

@login_required(login_url='/login/')  # Redirect to login if not authenticated
def booking_view(request, id):
    tours = Tour.objects.all()
    selected_tour = get_object_or_404(Tour, id=id)

    if request.method == "POST":
        print(request.POST)

        form = BookingForm(request.POST)
        if form.is_valid():
            tour_departure = form.cleaned_data['tour_departure']
            number_of_people = form.cleaned_data['number_of_people']

            # Ensure we have the latest available slots
            tour_departure.refresh_from_db()

            if tour_departure.available_slots >= number_of_people:
                # Create a booking
                booking = form.save(commit=False)
                booking.user = request.user
                booking.save()

                # Save extra passengers
                extra_passengers = []
                for i in range(1, number_of_people):
                    age = request.POST.get(f'person_{i}_age')
                    gender = request.POST.get(f'person_{i}_gender')
                    if age and gender:
                        passenger = ExtraPassenger.objects.create(
                            booking=booking,
                            tour=selected_tour,
                            tour_departure=tour_departure,
                            user=request.user,
                            age=int(age),
                            gender=gender
                        )
                        extra_passengers.append(passenger)

                # Reduce available slots
                tour_departure.available_slots -= number_of_people
                tour_departure.save()

                # Return a JSON response with redirect URL
                return JsonResponse({
                    'redirect_url': reverse('booking_confirmation', args=[booking.id])
                })
            else:
                return JsonResponse({
                    'message': 'Not enough available slots. Please select fewer people.'
                }, status=400)
        else:
            return JsonResponse({
                'message': 'There was an error in your booking form. Please check your details.'
            }, status=400)
    else:
        form = BookingForm()

    if form.is_valid():
        print("Form is valid")
    else:
        print("Form errors:", form.errors)

    return render(request, 'booking_page.html', {
        'form': form,
        'tours': tours,
        'selected_tour': selected_tour,
    })

@login_required(login_url='/login/')
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'confirmation.html', {'booking': booking})

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'bookings': bookings, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})

def base(request):
    return render(request, 'base.html')


from .models import State, City

def get_states(request):
    states = list(State.objects.values('state_id', 'state_name'))
    return JsonResponse({'states': states})
from django.views.decorators.http import require_GET
@require_GET
def get_cities(request):
    state_id = request.GET.get('state_id')
    if state_id:
        cities = City.objects.filter(state_id=state_id).values('id', 'city_name')
        return JsonResponse({'cities': list(cities)})
    return JsonResponse({'cities': []})

def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)  # Ensure the user owns the booking
    tour_name = booking.tour.name  # Get tour name
    departure_date = booking.tour_departure.departure_date.strftime("%Y-%m-%d") if booking.tour_departure else "No Departure Selected"

    # Restore available slots before deleting

    booking.delete()

    messages.success(request, f"Your booking for {tour_name} on {departure_date} has been deleted successfully.")  #  Improved message
    return redirect('dashboard')

def get_tour_price(request):
    tour_id = request.GET.get('tour_id')
    if tour_id:
        try:
            tour = Tour.objects.get(id=tour_id)
            return JsonResponse({'price': tour.price})
        except Tour.DoesNotExist:
            return JsonResponse({'error': 'Tour not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def bengaluru(request):
    tours = Tour.objects.all()
    return render(request, 'packages/bengaluru.html', {'tours': tours})

def kolakata(request):
    tours = Tour.objects.all()
    return render(request, 'packages/kolakata.html', {'tours': tours})

def himachal_pradesh(request):
    tours = Tour.objects.all()
    return render(request, 'packages/himachal_pradesh.html', {'tours': tours})

def ladak(request):
    tours = Tour.objects.all()
    return render(request, 'packages/ladak.html', {'tours': tours})

def chennai(request):
    tours = Tour.objects.all()
    return render(request, 'packages/chennai.html', {'tours': tours})

def delhi(request):
    tours = Tour.objects.all()
    return render(request, 'packages/delhi.html', {'tours': tours})

def dwarka(request):
    tours = Tour.objects.all()
    return render(request, 'packages/dwarka.html', {'tours': tours})

def goa(request):
    tours = Tour.objects.all()
    return render(request, 'packages/goa.html', {'tours': tours})

def hampi(request):
    tours = Tour.objects.all()
    return render(request, 'packages/hampi.html', {'tours': tours})

def jaipur(request):
    tours = Tour.objects.all()
    return render(request, 'packages/jaipur.html', {'tours': tours})

def jammu(request):
    tours = Tour.objects.all()
    return render(request, 'packages/jamukashmir.html', {'tours': tours})

def kerala(request):
    tours = Tour.objects.all()
    return render(request, 'packages/kerala.html', {'tours': tours})

def maharashtra(request):
    tours = Tour.objects.all()
    return render(request, 'packages/maharashtra.html', {'tours': tours})

def mysore(request):
    tours = Tour.objects.all()
    return render(request, 'packages/mysore.html', {'tours': tours})

def varanasi(request):
    tours = Tour.objects.all()
    return render(request, 'packages/varanasi.html', {'tours': tours})


def viewpack(request):
    tours = Tour.objects.all()  
    return render(request, 'packages/view.html', {
        'tours': tours,
        
        })
import urllib.parse

# Mapping tour names to their respective templates
TEMPLATE_MAP = {
    'Bengaluru': 'packages/bengaluru.html',
    'Delhi' : 'packages/delhi.html',
    'Chennai Heritage Tour': 'packages/chennai.html',
    'Dwarka': 'packages/dwarka.html',
    'Goa Beach Getaway': 'packages/goa.html',
    'Hampi': 'packages/hampi.html',
    'Himachal Hills Escape': 'packages/himachal_pradesh.html',
    'Jaipur': 'packages/jaipur.html',
    'Jammu & Kashmir Paradise': 'packages/jamukashmir.html',
    'Kerala Backwaters Retreat': 'packages/kerala.html',
    'Leh-Ladakh Adventure': 'packages/ladak.html',
    'Maharashtra Cultural Tour': 'packages/maharashtra.html',
    'Mysore': 'packages/mysore.html',
    'Varanasi Spiritual Tour': 'packages/varanasi.html'
}

def tour_detail(request, name):
    decoded_name = urllib.parse.unquote(name)
    template_name = TEMPLATE_MAP.get(decoded_name)
    print("Decoded Name:", decoded_name)  # Debug
    print("Template Name:", template_name)  # Debug
    tours = Tour.objects.all()  

    if template_name:
        try:
            return render(request, template_name)
        except TemplateDoesNotExist:
            return render(request, '404.html')  # Show 404 if template is missing
    else:
        return render(request, '404.html',{'tours': tours})




import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from .models import Payment
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        booking_id = self.kwargs['booking_id']
        booking = get_object_or_404(Booking, id=booking_id)

        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': f'Tour Package: {booking.tour.name}',
                        },
                        'unit_amount': int(booking.total_price * 100),  # Amount in paise
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'http://127.0.0.1:8000/payment-success/?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'http://127.0.0.1:8000/payment-failed/?booking_id={booking_id}',
            client_reference_id=booking_id,
            metadata={'booking_id': booking_id},  # Pass booking ID to Stripe
        )
        return JsonResponse({
            'id': checkout_session.id
        })




def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        # Retrieve the checkout session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        booking_id = session.client_reference_id

        try:
            # Update payment status to 'paid'
            booking = Booking.objects.get(id=booking_id)
            if session.payment_status == 'paid':
                booking.payment_status = 'paid'
            else:
                booking.payment_status = 'failed'
            booking.save()
        except Booking.DoesNotExist:
            print(f"Booking with ID {booking_id} not found.")
    
    return render(request, 'payment_success.html')

def payment_failed(request):
    booking_id = request.GET.get('booking_id')
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.payment_status = 'failed'
            booking.save()
        except Booking.DoesNotExist:
            print(f"Booking with ID {booking_id} not found.")
    
    return render(request, 'payment_failed.html')

def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)  # Fetch the specific booking
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'booking': booking  # Pass the specific booking instance
    }
    return render(request, 'checkout.html', context)

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session.get('client_reference_id')

        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.payment_status = 'paid'
                booking.save()
                print(f"Payment completed for booking ID: {booking_id}")
            except Booking.DoesNotExist:
                print(f"Booking with ID {booking_id} not found.")
                
    return JsonResponse({'status': 'success'})
from .forms import FeedbackForm

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Associate feedback with the logged-in user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('index')  # Redirect to the same page
    else:
        form = FeedbackForm()
    
    return render(request, 'index.html', {'form': form})