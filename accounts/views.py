from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models

from shop.models import Order
from booking.models import PortraitBooking
from .forms import UserLoginForm, UserRegistrationForm

User = get_user_model()


@login_required
def logout_view(request):
    """ Log the user out """
    logout(request)
    messages.success(request, "You have successfully been logged out")
    return redirect(reverse('home'))


def login_view(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in")
        return redirect(reverse('home'))
    if request.method == "POST":
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user_obj = User.objects.filter(email__iexact=email).first()
            if not user_obj:
                login_form.add_error(None, "Your email or password is incorrect")
            else:
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    # Check if user has temporary password
                    if hasattr(user, 'profile') and user.profile.is_temp_password:
                        messages.info(request, "Please change your temporary password.")
                        return redirect(reverse('change_password'))
                    messages.success(request, "You have successfully logged in")
                    if user.is_staff or user.is_superuser:
                        return redirect(reverse('admin_dashboard'))
                    return redirect(reverse('home'))
                else:
                    login_form.add_error(None, "Your email or password is incorrect")
    else:
        login_form = UserLoginForm()

    context = {'login_form': login_form}
    return render(request, 'login.html', context)


def register_user(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))

    if request.method == "POST":
        registration_form = UserRegistrationForm(request.POST)

        if registration_form.is_valid():
            user = registration_form.save()
            authenticated_user = authenticate(request, username=user.username,
                                              password=registration_form.cleaned_data['password1'])
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(
                    request,
                    "You have successfully registered and are now logged in")
                return redirect(reverse('home'))
            messages.error(request, "Unable to register your account")
    else:
        registration_form = UserRegistrationForm()

    context = {'registration_form': registration_form}
    return render(request, 'registration.html', context)


@login_required
def user_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    bookings = PortraitBooking.objects.filter(user=request.user).order_by('-created_at')
    total_spent = orders.aggregate(total=models.Sum('total_price'))['total'] or 0
    return render(request, 'user_dashboard_enhanced.html', {'orders': orders, 'bookings': bookings, 'total_spent': total_spent})


def forgot_password(request):
    """Display forgot password message"""
    return render(request, 'forgot_password.html')


@login_required
def change_password(request):
    """Allow user to change temporary password"""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_temp_password:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect(reverse('home'))

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            request.user.profile.is_temp_password = False
            request.user.profile.save()
            messages.success(request, "Password changed successfully. Please login again.")
            logout(request)
            return redirect(reverse('login'))

    return render(request, 'change_password.html')
