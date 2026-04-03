import uuid
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('customer', 'Customer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    contact_info = models.CharField(max_length=255, blank=True)
    dark_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=500)
    email = models.EmailField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text="Load capacity in units")
    current_location = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    driver = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vehicle',
    )

    def __str__(self):
        return f"{self.license_plate} - {self.model}"


class Route(models.Model):
    date = models.DateField()
    optimized_path = models.TextField(blank=True, help_text="JSON serialized route data")
    total_distance = models.FloatField(default=0.0, help_text="Distance in km")
    estimated_time = models.FloatField(default=0.0, help_text="Time in minutes")
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes'
    )

    def __str__(self):
        return f"Route #{self.id} - {self.date}"


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    pickup_address = models.CharField(max_length=500)
    delivery_address = models.CharField(max_length=500)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='deliveries')
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    driver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries',
    )
    route = models.ForeignKey(
        Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries'
    )
    # New fields for tracking & maps
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    delivery_lat = models.FloatField(null=True, blank=True)
    delivery_lng = models.FloatField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    # Customer rating
    rating = models.IntegerField(null=True, blank=True, choices=[(i, str(i)) for i in range(1, 6)])
    rating_comment = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "deliveries"

    def __str__(self):
        return f"Delivery #{self.id} - {self.status}"

    @property
    def tracking_url(self):
        return f"/track/{self.tracking_id}/"
