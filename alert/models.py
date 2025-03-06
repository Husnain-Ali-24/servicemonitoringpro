from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Alert(models.Model):
    STATUS_CHOICES = [
        ("UNKNOWN", "Unknown"),
        ("UP", "Up"),
        ("DOWN", "Down"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="UNKNOWN")
    timeStamp = models.DateTimeField(auto_now_add=True, blank=True)
    message=models.CharField(max_length=100,null=True)
    is_read=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.url} - {self.status}"
