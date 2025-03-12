from django.urls import path, include
from . import views  # Import the views from myapp
from django.contrib.auth import views as auth_views
from .views import dashboard, get_cities, get_states, profile_view, logout_confirm_view, logout_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # Signup Page
    path('login/', views.login_view, name='login'),      # Login Page
    path('logout/', logout_confirm_view, name='logout_confirm'),   # Logout Page
    path('logout/confirm/', logout_view, name='logout'),
    path('', views.index, name='index'),                 # Home Page
    path('base/', views.base, name='base'),
    path('accounts/profile/', profile_view, name='profile'),
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset_verify/', views.password_reset_verify, name='password_reset_verify'),
    path('booking/', views.booking_page, name='booking_page'),
    path('booking/<int:id>/', views.booking_view, name='booking'),  # Booking page URL
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('api/states/', get_states, name='get_states'),
    path('api/cities/', get_cities, name='get_cities'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('get_tour_departures/', views.get_tour_departures, name='get_tour_departures'),
    path('get_tour_price/', views.get_tour_price, name='get_tour_price'),
    path('bengaluru/', views.bengaluru, name='bengaluru'),
    path('kolakata/', views.kolakata, name='kolakata'),
    path('himachal_pradesh/', views.himachal_pradesh, name='himachal_pradesh'),
    path('ladak/', views.ladak, name='ladak'),
    path('chennai/', views.chennai, name='chennai'),
    path('delhi/', views.delhi, name='delhi'),
    path('dwarka/', views.dwarka, name='dwarka'),
    path('goa/', views.goa, name='goa'),
    path('hampi/', views.hampi, name='hampi'),
    path('jaipur/', views.jaipur, name='jaipur'),
    path('jammu/', views.jammu, name='jammu'),
    path('kerala/', views.kerala, name='kerala'),
    path('maharashtra/', views.maharashtra, name='maharashtra'),
    path('mysore/', views.mysore, name='mysore'),
    path('varanasi/', views.varanasi, name='varanasi'),
    path('tour/<str:name>/', views.tour_detail, name='tour_detail'),
    path('viewpack/', views.viewpack, name='viewpack'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),

    path('create-checkout-session/<int:booking_id>/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)