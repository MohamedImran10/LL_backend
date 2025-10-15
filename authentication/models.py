from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model that extends Django's default User.
    This will be used for admin users and maintains default Django structure.
    """
    pass

class AppUser(models.Model):
    """
    Separate model for regular app users (signup/login from Flutter app).
    This keeps admin users and app users completely separate.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'app_users'
        verbose_name = 'App User'
        verbose_name_plural = 'App Users'
    
    def __str__(self):
        return self.email
