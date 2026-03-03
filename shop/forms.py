from django import forms
from django.core import validators
import re
from booking.forms import INDIAN_STATES, INDIA_STATE_DISTRICTS


class CheckoutForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Make email read-only and populate from user
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['class'] = 'form-control form-control-lg bg-light'

        # Update district field to be a select with dynamic options
        # Include all districts from INDIA_STATE_DISTRICTS for validation
        all_districts = [('', 'Select District')]
        for districts in INDIA_STATE_DISTRICTS.values():
            for district in districts:
                if (district, district) not in all_districts:
                    all_districts.append((district, district))

        self.fields['district'] = forms.ChoiceField(
            choices=all_districts,
            label='District',
            widget=forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'id': 'id_district'
            })
        )
    
    name = forms.CharField(
        max_length=150,
        label='Full Name',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Your full name',
            'autocomplete': 'off'
        })
    )
    email = forms.EmailField(
        label='Email Address',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'you@example.com',
            'autocomplete': 'email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        label='Phone Number',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '+91 XXXXX XXXXX',
            'autocomplete': 'tel'
        })
    )
    address = forms.CharField(
        label='Street Address',
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control form-control-lg',
            'placeholder': 'Street address'
        })
    )
    state = forms.ChoiceField(
        choices=INDIAN_STATES,
        label='State',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'id': 'id_state'
        })
    )
    district = forms.ChoiceField(
        choices=[('', 'Select District')],
        label='District',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'id': 'districtSelect'
        })
    )
    pincode = forms.CharField(
        max_length=15,
        label='PIN Code',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'PIN code',
            'pattern': '[0-9]{6}',
            'maxlength': '6'
        }),
        help_text='6-digit postal code'
    )
    
    # Validation methods
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Name is required')
        # Only allow alphabets and spaces
        if not re.match(r'^[a-zA-Z\s]+$', name):
            raise forms.ValidationError('Name should only contain alphabets')
        return name
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise forms.ValidationError('Phone number is required')
        # Remove any spaces or special characters
        phone_digits = re.sub(r'[^\d]', '', phone)
        # Check if exactly 10 digits
        if len(phone_digits) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits')
        if not phone_digits.isdigit():
            raise forms.ValidationError('Phone number should only contain digits')
        return phone_digits
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('Email is required')
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise forms.ValidationError('Please enter a valid email address')
        return email
    
    def clean_address(self):
        address = self.cleaned_data.get('address', '').strip()
        if not address:
            raise forms.ValidationError('Address is required')
        return address
    
    def clean_state(self):
        state = self.cleaned_data.get('state', '').strip()
        if not state:
            raise forms.ValidationError('Please select a state')
        return state
    
    def clean_district(self):
        district = self.cleaned_data.get('district', '').strip()
        if not district:
            raise forms.ValidationError('Please select a district')
        return district
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode', '').strip()
        if not pincode:
            raise forms.ValidationError('PIN code is required')
        # Check if exactly 6 digits
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError('PIN code must be exactly 6 digits')
        return pincode
