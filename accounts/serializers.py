# serializers.py
from rest_framework import serializers
from .models import CustomUser,Profile,Address
from django.core.validators import RegexValidator

class CustomRegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
                required=False,
                allow_blank=True,
                validators=[
                        RegexValidator(
                            regex=r'^\d{10}$',  # Ensures exactly 10 digits
                            message="Phone number must be number and exactly 10 digits."
                        )
                    ]
                )
    email = serializers.EmailField(required=False, allow_blank=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'password1', 'password2']

    def validate(self, data):
        # Ensure that either email or phone_number is provided
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError("Either email or phone number is required.")
        
        # Check if password1 and password2 match
        if data.get('password1') != data.get('password2'):
            raise serializers.ValidationError("Passwords do not match.")
        
        return data

    def validate_email(self, value):
        if value and CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if value and CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        # Remove password2 from validated data since it's not needed for user creation
        validated_data.pop('password2')
        
        # Create a user instance
        user = CustomUser.objects.create_user(
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=validated_data.get('password1')
        )
        return user



class UpdatePhoneNumberSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ]
    )

    class Meta:
        model = CustomUser
        fields = ['phone_number']

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class UpdateEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['email']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'user', 'bio', 'profile_picture', 'date_of_birth',
            'gender', 'phone_number','is_verified',
        ]
        read_only_fields = ['user']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'uid', 'user', 'title', 'address', 'city', 'state', 
            'country', 'postal_code', 'latitude', 'longitude'
        ]
        read_only_fields = ['user']