import random
from django.utils import timezone
from .models import OTP

def generate_otp():
    return str(random.randint(100000, 999999))

def create_otp(user):
    otp_code = generate_otp()
    otp = OTP.objects.create(user=user, otp_code=otp_code)
    return otp

def verify_otp(user, otp_code):
    try:
        otp = OTP.objects.get(user=user, otp_code=otp_code, is_active=True, created_at__gte=timezone.now() - timezone.timedelta(minutes=15))
        otp.is_active = False
        otp.save()
        return True
    except OTP.DoesNotExist:
        return False