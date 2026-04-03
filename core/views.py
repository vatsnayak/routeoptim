import csv
import json
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count, Q

from .models import Profile, Customer, Vehicle, Route, Delivery
from .forms import RegistrationForm, CustomerForm, VehicleForm, RouteForm, DeliveryForm
from .decorators import RoleRequiredMixin, role_required


# ──────────────────────────────────────
# Public / Auth Views
# ──────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.role = form.cleaned_data['role']
            user.profile.contact_info = form.cleaned_data.get('contact_info', '')
            user.profile.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', 'customer')
    context = {'role': role}

    if role == 'admin':
        context['total_deliveries'] = Delivery.objects.count()
        context['pending_deliveries'] = Delivery.objects.filter(status='pending').count()
        context['in_transit_deliveries'] = Delivery.objects.filter(status='in-transit').count()
        context['delivered_count'] = Delivery.objects.filter(status='delivered').count()
        context['total_vehicles'] = Vehicle.objects.count()
        context['total_routes'] = Route.objects.count()
        context['total_customers'] = Customer.objects.count()
        context['recent_deliveries'] = Delivery.objects.order_by('-scheduled_time')[:5]
    elif role == 'driver':
        context['my_deliveries'] = Delivery.objects.filter(driver=request.user).order_by('-scheduled_time')
        context['pending_count'] = Delivery.objects.filter(driver=request.user, status='pending').count()
        context['in_transit_count'] = Delivery.objects.filter(driver=request.user, status='in-transit').count()
        try:
            context['my_vehicle'] = request.user.vehicle
        except Vehicle.DoesNotExist:
            context['my_vehicle'] = None
    else:
        context['my_deliveries'] = Delivery.objects.filter(
            customer__name__icontains=request.user.username
        ).order_by('-scheduled_time')

    return render(request, 'dashboard.html', context)


# ──────────────────────────────────────
# Map View
# ──────────────────────────────────────

@login_required
def map_view(request):
    deliveries = Delivery.objects.exclude(status='delivered').select_related('customer', 'driver')
    vehicles = Vehicle.objects.filter(latitude__isnull=False)

    markers = []
    for d in deliveries:
        if d.delivery_lat and d.delivery_lng:
            markers.append({
                'id': d.id,
                'type': 'delivery',
                'lat': d.delivery_lat,
                'lng': d.delivery_lng,
                'label': f'Delivery #{d.id}',
                'customer': d.customer.name,
                'address': d.delivery_address,
                'status': d.status,
            })
    for v in vehicles:
        markers.append({
            'id': v.id,
            'type': 'vehicle',
            'lat': v.latitude,
            'lng': v.longitude,
            'label': v.license_plate,
            'model': v.model,
            'driver': str(v.driver) if v.driver else 'Unassigned',
        })

    return render(request, 'map/map_view.html', {
        'markers_json': json.dumps(markers),
    })


# ──────────────────────────────────────
# Customer Tracking Portal (public)
# ──────────────────────────────────────

def track_delivery(request, tracking_id):
    delivery = get_object_or_404(Delivery, tracking_id=tracking_id)
    return render(request, 'tracking/track.html', {'delivery': delivery})


def track_lookup(request):
    if request.method == 'POST':
        tid = request.POST.get('tracking_id', '').strip()
        try:
            delivery = Delivery.objects.get(tracking_id=tid)
            return redirect('track-delivery', tracking_id=delivery.tracking_id)
        except (Delivery.DoesNotExist, ValueError):
            messages.error(request, 'Tracking ID not found. Please check and try again.')
    return render(request, 'tracking/lookup.html')


def rate_delivery(request, tracking_id):
    delivery = get_object_or_404(Delivery, tracking_id=tracking_id, status='delivered')
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        if rating:
            delivery.rating = int(rating)
            delivery.rating_comment = comment
            delivery.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('track-delivery', tracking_id=delivery.tracking_id)
    return render(request, 'tracking/rate.html', {'delivery': delivery})


# ──────────────────────────────────────
# Charts API (JSON endpoints)
# ──────────────────────────────────────

@login_required
def chart_data(request):
    # Delivery status breakdown
    status_counts = {
        'pending': Delivery.objects.filter(status='pending').count(),
        'in_transit': Delivery.objects.filter(status='in-transit').count(),
        'delivered': Delivery.objects.filter(status='delivered').count(),
    }

    # Deliveries per day (last 7 days)
    today = timezone.now().date()
    daily = []
    for i in range(6, -1, -1):
        d = today - timezone.timedelta(days=i)
        count = Delivery.objects.filter(scheduled_time__date=d).count()
        daily.append({'date': d.strftime('%b %d'), 'count': count})

    # Top customers
    top_customers = list(
        Customer.objects.annotate(delivery_count=Count('deliveries'))
        .order_by('-delivery_count')[:5]
        .values('name', 'delivery_count')
    )

    return JsonResponse({
        'status_counts': status_counts,
        'daily_deliveries': daily,
        'top_customers': top_customers,
    })


# ──────────────────────────────────────
# CSV Export
# ──────────────────────────────────────

@login_required
@role_required('admin')
def export_deliveries_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deliveries.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Customer', 'Pickup', 'Delivery Address', 'Status',
                     'Driver', 'Scheduled Time', 'Delivered At', 'Rating'])
    for d in Delivery.objects.select_related('customer', 'driver').order_by('-scheduled_time'):
        writer.writerow([
            d.id, d.customer.name, d.pickup_address, d.delivery_address,
            d.status, d.driver or '', d.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            d.delivered_at.strftime('%Y-%m-%d %H:%M') if d.delivered_at else '',
            d.rating or '',
        ])
    return response


@login_required
@role_required('admin')
def export_routes_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="routes.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Vehicle', 'Distance (km)', 'Est. Time (min)', 'Num Deliveries'])
    for r in Route.objects.select_related('vehicle').order_by('-date'):
        writer.writerow([
            r.id, r.date, r.vehicle or '', r.total_distance, r.estimated_time,
            r.deliveries.count(),
        ])
    return response


# ──────────────────────────────────────
# Dark Mode Toggle
# ──────────────────────────────────────

@login_required
def toggle_dark_mode(request):
    profile = request.user.profile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return JsonResponse({'dark_mode': profile.dark_mode})


# ──────────────────────────────────────
# Driver: Update Delivery Status
# ──────────────────────────────────────

@login_required
def update_delivery_status(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Delivery.STATUS_CHOICES):
            delivery.status = new_status
            if new_status == 'delivered':
                delivery.delivered_at = timezone.now()
            delivery.save()
            messages.success(request, f'Delivery #{delivery.id} marked as {delivery.get_status_display()}.')
    return redirect('delivery-detail', pk=pk)


# ──────────────────────────────────────
# Delivery CRUD
# ──────────────────────────────────────

class DeliveryListView(RoleRequiredMixin, ListView):
    model = Delivery
    template_name = 'deliveries/delivery_list.html'
    context_object_name = 'deliveries'
    allowed_roles = ['admin', 'driver', 'customer']

    def get_queryset(self):
        qs = super().get_queryset().order_by('-scheduled_time')
        role = self.request.user.profile.role
        if role == 'driver':
            return qs.filter(driver=self.request.user)
        return qs


class DeliveryDetailView(RoleRequiredMixin, DetailView):
    model = Delivery
    template_name = 'deliveries/delivery_detail.html'
    allowed_roles = ['admin', 'driver', 'customer']


class DeliveryCreateView(RoleRequiredMixin, CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'deliveries/delivery_form.html'
    success_url = reverse_lazy('delivery-list')
    allowed_roles = ['admin', 'driver']


class DeliveryUpdateView(RoleRequiredMixin, UpdateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'deliveries/delivery_form.html'
    success_url = reverse_lazy('delivery-list')
    allowed_roles = ['admin', 'driver']


class DeliveryDeleteView(RoleRequiredMixin, DeleteView):
    model = Delivery
    template_name = 'deliveries/delivery_confirm_delete.html'
    success_url = reverse_lazy('delivery-list')
    allowed_roles = ['admin']


# ──────────────────────────────────────
# Vehicle CRUD
# ──────────────────────────────────────

class VehicleListView(RoleRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicles/vehicle_list.html'
    context_object_name = 'vehicles'
    allowed_roles = ['admin', 'driver']


class VehicleDetailView(RoleRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'vehicles/vehicle_detail.html'
    allowed_roles = ['admin', 'driver']


class VehicleCreateView(RoleRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicle-list')
    allowed_roles = ['admin']


class VehicleUpdateView(RoleRequiredMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicle-list')
    allowed_roles = ['admin']


class VehicleDeleteView(RoleRequiredMixin, DeleteView):
    model = Vehicle
    template_name = 'vehicles/vehicle_confirm_delete.html'
    success_url = reverse_lazy('vehicle-list')
    allowed_roles = ['admin']


# ──────────────────────────────────────
# Route CRUD
# ──────────────────────────────────────

class RouteListView(RoleRequiredMixin, ListView):
    model = Route
    template_name = 'routes/route_list.html'
    context_object_name = 'routes'
    allowed_roles = ['admin', 'driver']

    def get_queryset(self):
        return super().get_queryset().order_by('-date')


class RouteDetailView(RoleRequiredMixin, DetailView):
    model = Route
    template_name = 'routes/route_detail.html'
    allowed_roles = ['admin', 'driver']


class RouteCreateView(RoleRequiredMixin, CreateView):
    model = Route
    form_class = RouteForm
    template_name = 'routes/route_form.html'
    success_url = reverse_lazy('route-list')
    allowed_roles = ['admin']


class RouteUpdateView(RoleRequiredMixin, UpdateView):
    model = Route
    form_class = RouteForm
    template_name = 'routes/route_form.html'
    success_url = reverse_lazy('route-list')
    allowed_roles = ['admin']


class RouteDeleteView(RoleRequiredMixin, DeleteView):
    model = Route
    template_name = 'routes/route_confirm_delete.html'
    success_url = reverse_lazy('route-list')
    allowed_roles = ['admin']


@login_required
@role_required('admin')
def optimize_route(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle')
        delivery_ids = request.POST.getlist('deliveries')

        if not vehicle_id or not delivery_ids:
            messages.error(request, 'Please select a vehicle and at least one delivery.')
            return redirect('route-optimize')

        vehicle = Vehicle.objects.get(id=vehicle_id)
        deliveries = Delivery.objects.filter(id__in=delivery_ids)

        ordered = list(deliveries.order_by('delivery_address'))
        total_distance = len(ordered) * 5.0
        estimated_time = len(ordered) * 15.0

        path_data = json.dumps([
            {'stop': i + 1, 'address': d.delivery_address, 'delivery_id': d.id,
             'lat': d.delivery_lat, 'lng': d.delivery_lng}
            for i, d in enumerate(ordered)
        ])

        route = Route.objects.create(
            date=date.today(),
            optimized_path=path_data,
            total_distance=total_distance,
            estimated_time=estimated_time,
            vehicle=vehicle,
        )

        for delivery in ordered:
            delivery.route = route
            delivery.driver = vehicle.driver
            delivery.status = 'in-transit'
            delivery.save()

        messages.success(request, f'Route #{route.id} created with {len(ordered)} deliveries.')
        return redirect('route-detail', pk=route.id)

    vehicles = Vehicle.objects.filter(driver__isnull=False)
    pending_deliveries = Delivery.objects.filter(status='pending', route__isnull=True)
    return render(request, 'routes/route_optimize.html', {
        'vehicles': vehicles,
        'pending_deliveries': pending_deliveries,
    })


# ──────────────────────────────────────
# Customer CRUD
# ──────────────────────────────────────

class CustomerListView(RoleRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    allowed_roles = ['admin']


class CustomerDetailView(RoleRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    allowed_roles = ['admin']


class CustomerCreateView(RoleRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer-list')
    allowed_roles = ['admin']


class CustomerUpdateView(RoleRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer-list')
    allowed_roles = ['admin']


class CustomerDeleteView(RoleRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customer-list')
    allowed_roles = ['admin']
