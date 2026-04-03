from django.contrib import admin
from .models import Profile, Customer, Vehicle, Route, Delivery


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'contact_info']
    list_filter = ['role']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_info', 'address']
    search_fields = ['name']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'model', 'capacity', 'driver']
    list_filter = ['model']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'vehicle', 'total_distance', 'estimated_time']
    list_filter = ['date']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'driver', 'scheduled_time']
    list_filter = ['status']
    search_fields = ['pickup_address', 'delivery_address']
