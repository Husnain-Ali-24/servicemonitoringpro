# models.py

from django.db import models
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django's default User model
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    city=models.CharField(max_length=25)
    country=models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user.username}'s profile"
