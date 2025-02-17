from django.urls import path
from . import views  # Import the views from myapp

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # Signup Page
    path('login/', views.login_view, name='login'),      # Login Page
    path('logout/', views.logout_view, name='logout'),   # Logout Page
    path('', views.index, name='index'),                 # Home Page
]