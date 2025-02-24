from django.urls import path,include
from monitoring.views import *

urlpatterns = [
    path("dashboard/<int:user_id>/", dashboard,name="dashboard"),
    path("addsite/<int:user_id>/", add_website,name="add_website"),
    path("remove_website/<int:website_id>/<int:user_id>/", remove_website,name="remove_website"),
    path("", Alerting,name="alert"),
]