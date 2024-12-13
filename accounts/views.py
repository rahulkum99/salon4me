# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from .models import CustomUser,OTP,Profile,Address
from .serializers import CustomRegisterSerializer,UpdateEmailSerializer, UpdatePhoneNumberSerializer,ProfileSerializer,AddressSerializer
from django.contrib.auth import authenticate,password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from .utils import create_otp, verify_otp


class EmailPhoneRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")  # Email or Phone Number
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate using the custom backend
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Generate JWT token for the authenticated user
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return Response({
                "access_token": str(access_token),
                "refresh_token": str(refresh),
                # "user": {
                #     "id": user.id,
                #     "email": user.email,
                #     "phone_number": user.phone_number
                # }
            }, status=status.HTTP_200_OK)
        
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # Check if the required fields are provided
        if not old_password or not new_password or not confirm_password:
            return Response({"detail": "All fields (old_password, new_password, confirm_password) are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the old password is correct
        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if new password and confirm password match
        if new_password != confirm_password:
            return Response({"detail": "New password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password strength if necessary (example)
        try:
            # Validate the new password using Django's default password validators
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)



class PasswordResetRequestView(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')  # This can be email or phone number
        if not identifier:
            return Response({"detail": "Email or phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to find the user by email
            user = CustomUser.objects.get(email=identifier)
        except CustomUser.DoesNotExist:
            try:
                # If email doesn't exist, check for phone number
                user = CustomUser.objects.get(phone_number=identifier)
            except CustomUser.DoesNotExist:
                return Response({"detail": "User with this email or phone number does not exist."}, 
                                status=status.HTTP_400_BAD_REQUEST)

        # Generate a reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        # Send reset link or code
        if '@' in identifier:  # If it's an email
            reset_url = f"{get_current_site(request).domain}/auth/password/reset/confirm/{uid}/{token}/"
            email_subject = "Password Reset Request"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            # send_mail(email_subject, message, 'no-reply@example.com', [user.email])

        else:  # If it's a phone number, send SMS (Twilio example)
            reset_code = token  # In this case, we use the token as the reset code for simplicity
            message = f"Your password reset code is {reset_code}. Use this code to reset your password."
            
            # client = Client('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN')  # Replace with your Twilio credentials
            # client.messages.create(
            #     body=message,
            #     from_='+1234567890',  # Your Twilio phone number
            #     to=user.phone_number
            # )
        print(message)
        return Response({"detail": "Password reset link/code sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            # Decode the user ID from the UID base64 string
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"detail": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the token is valid
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the new password from the request
        new_password = request.data.get('new_password')
        try:
            # Validate the new password using Django's default password validators
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password:
            return Response({"detail": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        # Set the new password
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def send_otp(request):
    phone_number = request.data.get('phone_number')
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    otp = create_otp(user)
    # Here you would implement your logic to send OTP via SMS or any other method
    print(f"OTP sent to {phone_number}: {otp.otp_code}")

    return Response({"detail": "OTP sent successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_otp_view(request):
    phone_number = request.data.get('phone_number')
    otp_code = request.data.get('otp_code')

    try:
        user = CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except CustomUser.MultipleObjectsReturned:
        return Response({"error": "Multiple users found with this phone number"}, status=status.HTTP_400_BAD_REQUEST)

    if verify_otp(user, otp_code):
        # Generate JWT tokens (access and refresh)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "detail": "OTP verification successful",
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client


class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if code is None:
            return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)      
        # Prepare data for the token request
        token_request_data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
            "grant_type": "authorization_code",
        }
        
        # Send request to Google's OAuth2 token endpoint
        token_url = "https://oauth2.googleapis.com/token"
        response = requests.post(token_url, data=token_request_data)
        
        # Handle the response from Google
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to obtain token"}, status=status.HTTP_400_BAD_REQUEST)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class UpdateEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UpdateEmailSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Email updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UpdatePhoneNumberSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Phone number updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProfileDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)



class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class AddressDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    lookup_field = 'uid'  # Ensure this matches the URL field

    def get_queryset(self):
        # Log the request user and query results for debugging
        print("Request user:", self.request.user)
        filtered_queryset = self.queryset.filter(user=self.request.user)
        print("Filtered queryset:", filtered_queryset)
        return filtered_queryset