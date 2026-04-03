from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Profile
    path('profile/', views.profile_settings, name='profile-settings'),
    path('profile/password/', views.change_password, name='change-password'),

    # Map
    path('map/', views.map_view, name='map-view'),

    # Tracking (public)
    path('track/', views.track_lookup, name='track-lookup'),
    path('track/<uuid:tracking_id>/', views.track_delivery, name='track-delivery'),
    path('track/<uuid:tracking_id>/rate/', views.rate_delivery, name='rate-delivery'),

    # API
    path('api/charts/', views.chart_data, name='chart-data'),
    path('api/dark-mode/', views.toggle_dark_mode, name='toggle-dark-mode'),
    path('api/geocode/', views.geocode_address, name='geocode-address'),

    # Export / Import
    path('export/deliveries/', views.export_deliveries_csv, name='export-deliveries'),
    path('export/routes/', views.export_routes_csv, name='export-routes'),
    path('import/deliveries/', views.import_deliveries_csv, name='import-deliveries'),

    # Quick Status Update
    path('deliveries/<int:pk>/status/', views.update_delivery_status, name='delivery-status-update'),

    # Deliveries
    path('deliveries/', views.DeliveryListView.as_view(), name='delivery-list'),
    path('deliveries/create/', views.DeliveryCreateView.as_view(), name='delivery-create'),
    path('deliveries/<int:pk>/', views.DeliveryDetailView.as_view(), name='delivery-detail'),
    path('deliveries/<int:pk>/edit/', views.DeliveryUpdateView.as_view(), name='delivery-update'),
    path('deliveries/<int:pk>/delete/', views.DeliveryDeleteView.as_view(), name='delivery-delete'),

    # Vehicles
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/create/', views.VehicleCreateView.as_view(), name='vehicle-create'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle-update'),
    path('vehicles/<int:pk>/delete/', views.VehicleDeleteView.as_view(), name='vehicle-delete'),

    # Routes
    path('routes/', views.RouteListView.as_view(), name='route-list'),
    path('routes/create/', views.RouteCreateView.as_view(), name='route-create'),
    path('routes/optimize/', views.optimize_route, name='route-optimize'),
    path('routes/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),
    path('routes/<int:pk>/edit/', views.RouteUpdateView.as_view(), name='route-update'),
    path('routes/<int:pk>/delete/', views.RouteDeleteView.as_view(), name='route-delete'),

    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer-update'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer-delete'),
]
