from django.test import TestCase
from django.utils.timezone import now
from uuid import uuid4
from .models import CustomUser, OTP, Profile, Address


class CustomUserModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            phone_number="1234567890",
            password="password123"
        )

    def test_user_creation(self):
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertFalse(self.user.is_staff)

    def test_superuser_creation(self):
        superuser = CustomUser.objects.create_superuser(
            email="admin@example.com",
            phone_number="0987654321",
            password="adminpass123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), "testuser@example.com")


class OTPModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            phone_number="1234567890",
            password="password123"
        )
        self.otp = OTP.objects.create(user=self.user, otp_code="123456")

    def test_otp_creation(self):
        self.assertEqual(OTP.objects.count(), 1)
        self.assertEqual(self.otp.otp_code, "123456")
        self.assertTrue(self.otp.is_active)

    def test_otp_string_representation(self):
        self.assertEqual(str(self.otp), f"OTP for {self.user.phone_number}")


class ProfileModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            phone_number="1234567890",
            password="password123"
        )

    def test_profile_auto_creation(self):
        self.assertEqual(Profile.objects.count(), 1)
        profile = self.user.profile
        self.assertEqual(profile.user, self.user)
        self.assertIsNone(profile.bio)

    def test_profile_update(self):
        profile = self.user.profile
        profile.bio = "This is a test bio."
        profile.save()
        self.assertEqual(Profile.objects.first().bio, "This is a test bio.")

    def test_profile_string_representation(self):
        profile = self.user.profile
        self.assertEqual(str(profile), f"{self.user.email}'s Profile")


class AddressModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            phone_number="1234567890",
            password="password123"
        )
        self.address = Address.objects.create(
            user=self.user,
            title="Home",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            country="Test Country",
            postal_code="12345",
            latitude=37.7749,
            longitude=-122.4194
        )

    def test_address_creation(self):
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(self.address.title, "Home")
        self.assertEqual(self.address.city, "Test City")
        self.assertEqual(self.address.latitude, 37.7749)
        self.assertEqual(self.address.longitude, -122.4194)

    def test_address_update(self):
        self.address.title = "Office"
        self.address.save()
        self.assertEqual(Address.objects.first().title, "Office")

    def test_address_string_representation(self):
        self.assertEqual(str(self.address), "Home")
