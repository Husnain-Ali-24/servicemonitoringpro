"""
URL configuration for alumni_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from authentication.views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Login (Generate Access & Refresh Tokens)
    TokenRefreshView,  # Refresh Expired Access Token
)

urlpatterns = [
    path("/login", LoginAPIView.as_view(),name="login"),
    path("/signup", SignUpAPI.as_view(), name='signup'),
    path("/signupSuccess", signupSuccessView, name='signupSuccess'),
    path("/logout", logoutView, name='logout'),


    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login & get tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
]
