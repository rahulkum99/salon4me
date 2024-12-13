from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import CustomUser

class EmailPhoneBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to find user by email or phone number
        try:
            user = CustomUser.objects.get(email=username)  # If username is email
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(phone_number=username)  # If username is phone number
            except CustomUser.DoesNotExist:
                return None  # No user found
        
        # Check if password matches
        if user.check_password(password):
            return user
        return None
