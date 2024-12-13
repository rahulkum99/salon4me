from django.contrib import admin
from .models import Category, Shop, Service, TimeSlot, ServiceAddress, Coupon

# Register the models with default admin configurations
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'is_publish', 'slug')
    search_fields = ('category_name',)
    list_filter = ('is_publish',)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'latitude', 'longitude')
    search_fields = ('name', 'owner', 'address')
    list_filter = ('is_active',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'shop', 'mrp_price', 'dis_price', 'is_publish', 'slug')
    search_fields = ('service_name', 'shop__name')
    list_filter = ('is_publish',)
    raw_id_fields = ('shop',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('service', 'start_time', 'end_time')
    search_fields = ('service__service_name',)
    raw_id_fields = ('service',)


@admin.register(ServiceAddress)
class ServiceAddressAdmin(admin.ModelAdmin):
    list_display = ('city_name',)
    search_fields = ('city_name',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_code', 'is_expired', 'discount_price', 'minimum_amount')
    search_fields = ('coupon_code',)
    list_filter = ('is_expired',)
