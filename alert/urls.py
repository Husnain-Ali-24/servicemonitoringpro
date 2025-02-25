from django.contrib import admin
from django.urls import path,include
from alert.views import *

urlpatterns = [
    path("alert_status/<int:user_id>/", alertView,name="alert_status"),
    path('mark-as-read/<int:alert_id>/', mark_as_read, name='mark_as_read'),
    path('clear-alert/<int:alert_id>/', clear_alert, name='clear_alert'),
]