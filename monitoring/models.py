from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    status = models.CharField(max_length=10, default="UNKNOWN")
    INTERVAL_CHOICES = [
        (30, "Every 30 sec"),
        (60, "Every 1 min"),
        (120, "Every 2 min"),
        (300, "Every 5 min"),
    ]
    interval = models.IntegerField(choices=INTERVAL_CHOICES, default=60) 
    last_checked = models.DateTimeField(auto_now=True)
    monitoring_type=models.CharField(max_length=50,default="server")

    def __str__(self):
        return self.url
    