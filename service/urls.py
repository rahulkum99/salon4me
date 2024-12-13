from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryViewSet, ShopViewSet, ServiceViewSet, CouponViewSet, ServiceAddressListView, TimeSlotListCreateView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'shops', ShopViewSet, basename='shop')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
    path('service-addresses/', ServiceAddressListView.as_view(), name='service-address-list'),
    path('time-slots/', TimeSlotListCreateView.as_view(), name='time-slot-list'),
]
