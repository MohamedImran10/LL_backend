from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('validate/', views.validate_token, name='validate_token'),
    path('profile/', views.user_profile, name='user_profile'),
    path('health/', views.health_check, name='health_check'),
]
