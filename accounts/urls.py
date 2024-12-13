from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView,TokenVerifyView
from dj_rest_auth.views import PasswordResetConfirmView
from . views import *

urlpatterns = [
    # Registration Email and Phone login URLs
    path('registration/', EmailPhoneRegistrationView.as_view(), name='email_phone_registration'),
    path("login/",CustomLoginView.as_view(), name='custom_login'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Custom reset confirm

    path('send-otp/', send_otp, name='send-otp'),
    path('verify-otp/', verify_otp_view, name='verify-otp'),

    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("result/",GoogleLoginCallback.as_view(),name="google_login_callback"),

    path('facebook/', FacebookLogin.as_view(), name='fb_login'),

    path('update-email/', UpdateEmailView.as_view(), name='update_email'),
    path('update-phone/', UpdatePhoneNumberView.as_view(), name='update_phone'),

    path('profile/', ProfileDetail.as_view(), name='profile-detail'),
    
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<uuid:uid>/', AddressDetailView.as_view(), name='address-detail'),
]