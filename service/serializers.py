from rest_framework import serializers
from .models import Category, Shop, Service, TimeSlot, ServiceAddress, Coupon


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'slug', 'is_publish', 'category_image']


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'owner', 'address',
            'contact_number', 'email', 'is_active',
            'image', 'latitude', 'longitude'
        ]


class ServiceSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'shop', 'service_name', 'mrp_price', 'dis_price',
            'product_description', 'is_publish', 'slug',
            'fake_review', 'fake_rating', 'image',
            'total_reviews', 'average_rating'
        ]
        read_only_fields = ['slug', 'total_reviews', 'average_rating']


class TimeSlotSerializer(serializers.ModelSerializer):
    service = serializers.StringRelatedField()  # Displays the `__str__` representation of the Service

    class Meta:
        model = TimeSlot
        fields = ['id', 'service', 'start_time', 'end_time']


class ServiceAddressSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = ServiceAddress
        fields = ['id', 'city_name', 'category']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'coupon_code', 'is_expired', 'discount_price', 'minimum_amount']
