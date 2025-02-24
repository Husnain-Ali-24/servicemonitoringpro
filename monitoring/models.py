from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    status = models.CharField(max_length=10, default="UNKNOWN")
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url
    