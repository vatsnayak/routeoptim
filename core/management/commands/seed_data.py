from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile, Customer, Vehicle, Route, Delivery
from datetime import date, datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create users
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@routeoptim.com', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()
        admin_user.profile.role = 'admin'
        admin_user.profile.contact_info = '+1-555-0100'
        admin_user.profile.save()

        driver1, _ = User.objects.get_or_create(
            username='driver1',
            defaults={'email': 'driver1@routeoptim.com', 'first_name': 'John', 'last_name': 'Smith'}
        )
        driver1.set_password('driver123')
        driver1.save()
        driver1.profile.role = 'driver'
        driver1.profile.contact_info = '+1-555-0201'
        driver1.profile.save()

        driver2, _ = User.objects.get_or_create(
            username='driver2',
            defaults={'email': 'driver2@routeoptim.com', 'first_name': 'Jane', 'last_name': 'Doe'}
        )
        driver2.set_password('driver123')
        driver2.save()
        driver2.profile.role = 'driver'
        driver2.profile.contact_info = '+1-555-0202'
        driver2.profile.save()

        cust_user, _ = User.objects.get_or_create(
            username='customer1',
            defaults={'email': 'customer1@routeoptim.com'}
        )
        cust_user.set_password('customer123')
        cust_user.save()
        cust_user.profile.role = 'customer'
        cust_user.profile.save()

        # Create customers with coordinates
        customers_data = [
            ('Acme Corp', '+1-555-1001', '123 Business Ave, New York, NY', 'acme@example.com', 40.7580, -73.9855),
            ('TechStart Inc', '+1-555-1002', '456 Innovation Blvd, San Francisco, CA', 'tech@example.com', 37.7749, -122.4194),
            ('Local Bakery', '+1-555-1003', '789 Main St, Chicago, IL', 'bakery@example.com', 41.8781, -87.6298),
            ('Green Grocers', '+1-555-1004', '321 Oak Rd, Boston, MA', 'green@example.com', 42.3601, -71.0589),
            ('City Pharmacy', '+1-555-1005', '654 Pine St, Seattle, WA', 'pharmacy@example.com', 47.6062, -122.3321),
        ]
        customers = []
        for name, contact, address, email, lat, lng in customers_data:
            c, _ = Customer.objects.get_or_create(
                name=name,
                defaults={'contact_info': contact, 'address': address, 'email': email,
                          'latitude': lat, 'longitude': lng}
            )
            customers.append(c)

        # Create vehicles with coordinates
        vehicles_data = [
            ('ABC-1234', 'Ford Transit', 500, driver1, 40.7484, -73.9967),
            ('XYZ-5678', 'Mercedes Sprinter', 800, driver2, 40.7527, -73.9772),
        ]
        vehicles = []
        for plate, model, cap, driver, lat, lng in vehicles_data:
            v, _ = Vehicle.objects.get_or_create(
                license_plate=plate,
                defaults={'model': model, 'capacity': cap, 'driver': driver,
                          'current_location': 'Warehouse District',
                          'latitude': lat, 'longitude': lng}
            )
            vehicles.append(v)

        # Create deliveries with coordinates
        now = timezone.now()
        deliveries_data = [
            ('Warehouse A, Manhattan', '123 Business Ave, New York, NY', customers[0],
             now + timedelta(hours=2), 'pending', None,
             40.7484, -73.9967, 40.7580, -73.9855),
            ('Warehouse A, Manhattan', '456 Innovation Blvd, San Francisco, CA', customers[1],
             now + timedelta(hours=3), 'pending', None,
             40.7484, -73.9967, 37.7749, -122.4194),
            ('Warehouse B, Brooklyn', '789 Main St, Chicago, IL', customers[2],
             now + timedelta(hours=1), 'in-transit', driver1,
             40.6782, -73.9442, 41.8781, -87.6298),
            ('Warehouse A, Manhattan', '321 Oak Rd, Boston, MA', customers[3],
             now - timedelta(hours=5), 'delivered', driver2,
             40.7484, -73.9967, 42.3601, -71.0589),
            ('Warehouse B, Brooklyn', '654 Pine St, Seattle, WA', customers[4],
             now + timedelta(hours=4), 'pending', None,
             40.6782, -73.9442, 47.6062, -122.3321),
            ('Warehouse A, Manhattan', '159 Broadway, New York, NY', customers[0],
             now + timedelta(hours=6), 'pending', None,
             40.7484, -73.9967, 40.7614, -73.9776),
            ('Warehouse B, Brooklyn', '742 Evergreen Terrace, Chicago, IL', customers[2],
             now - timedelta(hours=2), 'delivered', driver1,
             40.6782, -73.9442, 41.8827, -87.6233),
        ]
        for data in deliveries_data:
            pickup, delivery_addr, customer, sched, status, driver, p_lat, p_lng, d_lat, d_lng = data
            d, created = Delivery.objects.get_or_create(
                pickup_address=pickup,
                delivery_address=delivery_addr,
                customer=customer,
                defaults={
                    'scheduled_time': sched, 'status': status, 'driver': driver,
                    'pickup_lat': p_lat, 'pickup_lng': p_lng,
                    'delivery_lat': d_lat, 'delivery_lng': d_lng,
                    'delivered_at': sched if status == 'delivered' else None,
                }
            )
            if not created and not d.pickup_lat:
                d.pickup_lat, d.pickup_lng = p_lat, p_lng
                d.delivery_lat, d.delivery_lng = d_lat, d_lng
                d.save()

        self.stdout.write(self.style.SUCCESS('Done! Sample data created.'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write(f'  Admin:    admin / admin123')
        self.stdout.write(f'  Driver:   driver1 / driver123')
        self.stdout.write(f'  Driver:   driver2 / driver123')
        self.stdout.write(f'  Customer: customer1 / customer123')
