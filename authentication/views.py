from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User
from authentication.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

class LoginAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return render(request, "login.html")  # Initial login page

    def post(self, request):
        email = request.POST.get("email")  # Fetch email from form
        password = request.POST.get("password")  # Fetch password from form

        if not email or not password:
            return render(request, "login.html", {"error": "Email and password are required"})

        try:
            # Check if the user exists
            user = User.objects.get(email=email)

            # Validate password
            if check_password(password, user.password):
                # request.session.cycle_key() 
                login(request, user)
                return redirect(reverse("dashboard", args=[user.id]))
            else:
                return render(request, "login.html", {"error": "Invalid email or password"})

        except User.DoesNotExist:
            return render(request, "login.html", {"error": "User does not exist"})

class SignUpAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return render(request, "signup.html")

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Save the user and profile data
            return render(request,"signupSuccess.html")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url=reverse_lazy('login')) 
def signupSuccessView(request):
    return render(request,"signupSuccess.html")

def logoutView(request):
    logout(request)
    return redirect("login")