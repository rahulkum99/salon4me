from django.test import TestCase
from .models import Category, Shop, Service
from decimal import Decimal


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name="Electronics",
            is_publish=True
        )

    def test_category_creation(self):
        self.assertEqual(self.category.category_name, "Electronics")
        self.assertTrue(self.category.is_publish)

    def test_slug_generation(self):
        self.assertEqual(self.category.slug, "electronics")


class ShopModelTest(TestCase):
    def setUp(self):
        self.shop = Shop.objects.create(
            name="Tech Store",
            owner="John Doe",
            address="123 Tech Street",
            contact_number="1234567890",
            email="techstore@example.com",
            latitude=Decimal("12.971598"),
            longitude=Decimal("77.594566"),
            is_active=True
        )

    def test_shop_coordinates(self):
        self.assertEqual(Decimal(self.shop.latitude), Decimal("12.971598"))
        self.assertEqual(Decimal(self.shop.longitude), Decimal("77.594566"))

    def test_shop_creation(self):
        self.assertEqual(self.shop.name, "Tech Store")
        self.assertEqual(self.shop.owner, "John Doe")
        self.assertTrue(self.shop.is_active)

    def test_slug_generation(self):
        self.assertEqual(self.shop.slug, "tech-store")



class ServiceModelTest(TestCase):
    def setUp(self):
        self.shop = Shop.objects.create(
            name="Gadget World",
            owner="Jane Smith",
            address="45 Gadget Lane",
            contact_number="9876543210",
            email="gadgetworld@example.com",
            is_active=True
        )
        self.service = Service.objects.create(
            shop=self.shop,
            service_name="Smartphone Repair",
            mrp_price=Decimal("500.00"),
            dis_price=Decimal("450.00"),
            product_description="We fix all smartphone issues.",
            is_publish=True
        )

    def test_service_creation(self):
        self.assertEqual(self.service.service_name, "Smartphone Repair")
        self.assertEqual(self.service.shop.name, "Gadget World")
        self.assertTrue(self.service.is_publish)

    def test_slug_generation(self):
        self.assertEqual(self.service.slug, "smartphone-repair")

    def test_price_fields(self):
        self.assertEqual(self.service.mrp_price, Decimal("500.00"))
        self.assertEqual(self.service.dis_price, Decimal("450.00"))
