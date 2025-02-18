from django.urls import path, include
from . import views  # Import the views from myapp
from .views import profile_view

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # Signup Page
    path('login/', views.login_view, name='login'),      # Login Page
    path('logout/', views.logout_view, name='logout'),   # Logout Page
    path('', views.index, name='index'),                 # Home Page
    path('auth/', include('django.contrib.auth.urls')),
    path('accounts/profile/', profile_view, name='profile'),
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset_verify/', views.password_reset_verify, name='password_reset_verify'),
]