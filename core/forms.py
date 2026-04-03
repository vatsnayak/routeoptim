from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile, Customer, Vehicle, Route, Delivery


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    contact_info = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['contact_info']
        widgets = {
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1-555-0000'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact_info', 'address', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'id': 'address-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'model', 'capacity', 'current_location', 'driver']
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
        }


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['date', 'vehicle', 'optimized_path', 'total_distance', 'estimated_time']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'optimized_path': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_distance': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_time': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['pickup_address', 'delivery_address', 'customer', 'scheduled_time',
                  'status', 'driver', 'route', 'notes']
        widgets = {
            'pickup_address': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_address': forms.TextInput(attrs={'class': 'form-control', 'id': 'delivery-address-input'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional delivery notes...'}),
        }


class DeliveryFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + list(Delivery.STATUS_CHOICES)
    search = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search customer, address...'}))
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES,
                               widget=forms.Select(attrs={'class': 'form-select'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}))


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'}),
        help_text='CSV with columns: pickup_address, delivery_address, customer_name, scheduled_time (YYYY-MM-DD HH:MM)'
    )
