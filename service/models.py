from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from django.db.models import Avg
from django.core.exceptions import ValidationError


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    is_publish = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to='categories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class Shop(BaseModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
    owner = models.CharField(max_length=100)  # Can link to User model if applicable
    address = models.TextField()
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='shop_images', null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Latitude of the shop's location (e.g., 12.971598)."
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Longitude of the shop's location (e.g., 77.594566)."
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Shop, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        return Decimal(super().latitude)

    @property
    def longitude(self):
        return Decimal(super().longitude)


class Service(BaseModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="services")
    service_name = models.CharField(max_length=100)
    mrp_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    dis_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    product_description = models.TextField()
    is_publish = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    fake_review = models.IntegerField(null=True, blank=True)
    fake_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='shop_images', null=True, blank=True, default='default_shop.jpg')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.service_name)
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.service_name

    def total_reviews(self):
        return self.product_reviews.count()

    @property
    def average_rating(self):
        avg_rating = self.product_reviews.aggregate(Avg('rating'))['rating__avg']
        return avg_rating if avg_rating is not None else 0


class TimeSlot(BaseModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="time_slots")
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"TimeSlot: {self.service.service_name} ({self.start_time} - {self.end_time})"


class ServiceAddress(BaseModel):
    city_name = models.CharField(max_length=180, unique=True)
    category = models.ManyToManyField(Category, related_name="city_services")

    def __str__(self):
        return self.city_name


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)

    def __str__(self):
        return self.coupon_code

    def clean(self):
        
        if self.discount_price >= self.minimum_amount:
            raise ValidationError("Discount price must be less than the minimum amount.")
