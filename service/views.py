from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Category, Shop, Service, TimeSlot, ServiceAddress, Coupon
from .serializers import (
    CategorySerializer, ShopSerializer, ServiceSerializer,
    TimeSlotSerializer, ServiceAddressSerializer, CouponSerializer
)

from django.conf import settings
from .utils import get_distances


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Adjust permissions as needed


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def get_queryset(self):
        # Example filter: return only active shops
        return Shop.objects.filter(is_active=True)



class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        # Filter by shop if a query parameter is provided
        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            return Service.objects.filter(shop__id=shop_id)
        return super().get_queryset()


class TimeSlotListCreateView(generics.ListCreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class ServiceAddressListView(generics.ListAPIView):
    queryset = ServiceAddress.objects.all()
    serializer_class = ServiceAddressSerializer


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_queryset(self):
        # Filter expired or active coupons based on query parameter
        is_expired = self.request.query_params.get('is_expired')
        if is_expired is not None:
            return Coupon.objects.filter(is_expired=is_expired.lower() == 'true')
        return super().get_queryset()


class NearestShopView(APIView):
    def get(self, request, *args, **kwargs):
        user_lat = request.query_params.get('latitude', None)
        user_lon = request.query_params.get('longitude', None)

        if not user_lat or not user_lon:
            return Response({"error": "Please provide latitude and longitude"}, status=400)

        user_lat = float(user_lat)
        user_lon = float(user_lon)

        # Fetch all active shops
        shops = Shop.objects.filter(is_active=True)
        shop_locations = [(shop.latitude, shop.longitude) for shop in shops]

        # Get distances using Google API
        try:
            api_key = settings.GOOGLE_MAPS_API_KEY
            distances = get_distances(user_lat, user_lon, shop_locations, api_key)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # Annotate shops with distances
        for shop, distance in zip(shops, distances):
            shop.distance = distance

        # Sort shops by distance
        sorted_shops = sorted(shops, key=lambda x: x.distance)

        # Serialize and return the nearest shops
        serializer = ShopSerializer(sorted_shops, many=True)
        return Response(serializer.data)