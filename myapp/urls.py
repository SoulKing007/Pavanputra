from django.urls import path, include
from . import views  # Import the views from myapp
from .views import dashboard, get_cities, get_states, profile_view, logout_confirm_view, logout_view

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # Signup Page
    path('login/', views.login_view, name='login'),      # Login Page
    path('logout/', logout_confirm_view, name='logout_confirm'),   # Logout Page
    path('logout/confirm/', logout_view, name='logout'),
    path('', views.index, name='index'),                 # Home Page
    path('base/', views.base, name='base'),
    path('auth/', include('django.contrib.auth.urls')),
    path('accounts/profile/', profile_view, name='profile'),
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset_verify/', views.password_reset_verify, name='password_reset_verify'),
    path('booking/', views.booking_view, name='booking'),  # Booking page URL
    path('confirmation/<int:booking_id>', views.booking_confirmation, name='booking_confirmation'),  # Confirmation page
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('api/states/', get_states, name='get_states'),
    path('api/cities/<int:state_id>/', get_cities, name='get_cities'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),

]   