# serializers.py
from django.core.exceptions import ValidationError
from rest_framework import serializers
from authentication.models import *

from django.contrib.auth.models import User
from authentication.models import *


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=15)
    address = serializers.CharField(max_length=100)
    city=serializers.CharField(max_length=25)
    country=serializers.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'address', 'city','country']


    def validate_email(self, value):
        # Check if the email already exists in the database
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email is already taken.")
        return value
    
    def create(self, validated_data):
        # Separate profile data
        profile_data = {key: validated_data.pop(key) for key in ['address', 'phone_number', 'city', 'country']}
        
        # Create the user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_staff=False, 
        )
        
        # Create the profile instance and associate it with the user
        UserProfile.objects.create(user=user, **profile_data)
        
        return user

