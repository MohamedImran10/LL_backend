from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class FlightSearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    date = models.CharField(max_length=50)
    results = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.origin} to {self.destination} on {self.date}"


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_user = models.BooleanField(default=True)
    flights = models.JSONField(default=list, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        sender = "User" if self.is_user else "Agent"
        return f"{sender}: {self.message[:50]}..."
