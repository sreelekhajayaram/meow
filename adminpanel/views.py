from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
import csv
from reportlab.pdfgen import canvas
from io import BytesIO

from shop.models import Category, Product, Order, OrderItem
from shop.models import ProductImage
from booking.models import PortraitBooking
from accounts.models import UserProfile
from feedback.models import Feedback
from .forms import CategoryForm, ProductForm

User = get_user_model()


@staff_member_required
def dashboard(request):
    data = {
        'products': Product.objects.count(),
        'orders': Order.objects.count(),
        'bookings': PortraitBooking.objects.count(),
        'users': UserProfile.objects.count(),
    }

    # Filter for latest orders
    order_status_filter = request.GET.get('order_status', '').strip()
    latest_orders = Order.objects.select_related('user').order_by('-created_at')
    if order_status_filter:
        latest_orders = latest_orders.filter(order_status=order_status_filter)
    latest_orders = latest_orders[:5]

    # Filter for latest bookings
    booking_status_filter = request.GET.get('booking_status', '').strip()
    latest_bookings = PortraitBooking.objects.select_related('user').order_by('-created_at')
    if booking_status_filter:
        latest_bookings = latest_bookings.filter(booking_status=booking_status_filter)
    latest_bookings = latest_bookings[:5]

    recent_users = User.objects.order_by('-date_joined')[:5]
    return render(request, 'adminpanel/dashboard.html', {
        'stats': data,
        'latest_orders': latest_orders,
        'latest_bookings': latest_bookings,
        'recent_users': recent_users,
        'order_status_filter': order_status_filter,
        'booking_status_filter': booking_status_filter,
        'order_status_choices': Order.ORDER_STATUS_CHOICES,
        'booking_status_choices': PortraitBooking.BOOKING_STATUS_CHOICES,
    })


@staff_member_required
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Total', 'Payment Status', 'Order Status', 'Created'])
    for order in Order.objects.select_related('user'):
        writer.writerow([order.id, order.user.username, order.total_price, order.payment_status, order.order_status, order.created_at])
    return response


@staff_member_required
def export_bookings_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Name', 'Email', 'Phone', 'Price', 'Status', 'Preferred Date'])
    for booking in PortraitBooking.objects.select_related('user'):
        writer.writerow([booking.id, booking.user.username, booking.name, booking.email, booking.phone, booking.price, booking.booking_status, booking.preferred_date])
    return response


@staff_member_required
def export_bookings_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, "Portrait Bookings List")
    y = 760
    for booking in PortraitBooking.objects.select_related('user').order_by('-created_at')[:20]:
        preferred_date_str = booking.preferred_date.strftime('%Y-%m-%d') if booking.preferred_date else 'N/A'
        text = f"#{booking.id} - {booking.user.email} - {booking.name} - ₹{booking.price} - {booking.booking_status} - {preferred_date_str}"
        p.drawString(60, y, text)
        y -= 20
        if y < 50:
            p.showPage()
            y = 760
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


@staff_member_required
def export_users_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, "Users List")
    y = 760
    for profile in UserProfile.objects.select_related('user'):
        text = f"{profile.user.email} — role: {profile.role} — joined: {profile.user.date_joined.strftime('%Y-%m-%d')}"
        p.drawString(60, y, text)
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


@staff_member_required
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['Email', 'Role', 'Date Joined', 'Last Login'])
    for user in User.objects.select_related('profile').all().order_by('-date_joined'):
        role = getattr(getattr(user, 'profile', None), 'role', '')
        writer.writerow([
            user.email,
            role,
            user.date_joined.strftime('%Y-%m-%d'),
            user.last_login.strftime('%Y-%m-%d') if user.last_login else '',
        ])
    return response


@staff_member_required
def user_list(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    if query:
        users = users.filter(email__icontains=query)
    return render(request, 'adminpanel/users.html', {
        'users': users,
        'query': query,
    })


@staff_member_required
def catalog(request):
    cat_form = CategoryForm(request.POST or None, request.FILES or None, prefix="cat")
    prod_form = ProductForm(request.POST or None, request.FILES or None, prefix="prod")

    if request.method == "POST":
        if "cat-submit" in request.POST and cat_form.is_valid():
            cat_form.save()
            messages.success(request, "Category saved.")
            return redirect('admin_catalog')
        if "prod-submit" in request.POST and prod_form.is_valid():
            product = prod_form.save()
            # handle multiple images
            images = request.FILES.getlist('images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            messages.success(request, "Product saved.")
            return redirect('admin_catalog')

    categories = Category.objects.prefetch_related('products').all().order_by('name')
    products = Product.objects.select_related('category').order_by('-created_at')

    # Handle search filters
    category_search = request.GET.get('category_search', '').strip()
    product_search = request.GET.get('product_search', '').strip()

    if category_search:
        categories = categories.filter(name__icontains=category_search) | categories.filter(description__icontains=category_search)

    if product_search:
        products = products.filter(title__icontains=product_search) | products.filter(description__icontains=product_search)

    return render(request, 'adminpanel/catalog.html', {
        'categories': categories,
        'products': products,
        'cat_form': cat_form,
        'prod_form': prod_form,
    })


@staff_member_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated.")
        return redirect('admin_catalog')
    return render(request, 'adminpanel/edit_category.html', {'form': form, 'category': category})


@staff_member_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect('admin_catalog')
    return render(request, 'adminpanel/confirm_delete.html', {'object': category, 'type': 'Category'})


@staff_member_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST":
        if form.is_valid():
            try:
                prod = form.save()
                # handle new uploaded images
                images = request.FILES.getlist('images')
                for img in images:
                    ProductImage.objects.create(product=prod, image=img)
                messages.success(request, "Product updated.")
                return redirect('admin_catalog')
            except Exception as e:
                messages.error(request, f"Error saving product: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'adminpanel/edit_product.html', {'form': form, 'product': product})


@staff_member_required
def delete_product_image(request, pk):
    img = get_object_or_404(ProductImage, pk=pk)
    product_id = img.product.id
    if request.method == 'POST':
        img.delete()
        messages.success(request, "Image removed.")
        return redirect('edit_product', pk=product_id)
    return render(request, 'adminpanel/confirm_delete.html', {'object': img, 'type': 'Product Image'})


@staff_member_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect('admin_catalog')
    return render(request, 'adminpanel/confirm_delete.html', {'object': product, 'type': 'Product'})


@staff_member_required
def portrait_orders(request):
    """View for managing portrait booking orders"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    bookings = PortraitBooking.objects.select_related('user').order_by('-created_at')

    if query:
        bookings = bookings.filter(
            name__icontains=query
        ) | bookings.filter(
            email__icontains=query
        ) | bookings.filter(
            order_id__icontains=query
        )

    if status_filter:
        bookings = bookings.filter(booking_status=status_filter)

    return render(request, 'adminpanel/portrait_orders.html', {
        'bookings': bookings,
        'query': query,
        'status_filter': status_filter,
    })


@staff_member_required
def download_reference_image(request, booking_id):
    """Download reference image for a portrait booking"""
    booking = get_object_or_404(PortraitBooking, id=booking_id)
    if not booking.reference_image:
        messages.error(request, "No reference image found for this booking.")
        return redirect('portrait_orders')

    # Get the file
    file_path = booking.reference_image.path
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{booking.reference_image.name.split("/")[-1]}"'
        return response


@staff_member_required
def order_detail(request, order_id):
    """View detailed information for a specific order"""
    order = get_object_or_404(Order.objects.select_related('user'), id=order_id)
    order_items = order.items.select_related('product').all()
    for item in order_items:
        item.line_total = item.quantity * item.price
    return render(request, 'adminpanel/order_details.html', {
        'order': order,
        'order_items': order_items,
    })


@staff_member_required
def booking_detail(request, booking_id):
    """View detailed information for a specific booking"""
    booking = get_object_or_404(PortraitBooking.objects.select_related('user'), id=booking_id)
    return render(request, 'adminpanel/booking_details.html', {
        'booking': booking,
    })


@staff_member_required
def manage_feedback(request):
    """View and manage customer feedback"""
    feedbacks = Feedback.objects.select_related('user').order_by('-created_at')
    return render(request, 'adminpanel/manage_feedback.html', {
        'feedbacks': feedbacks,
    })


@staff_member_required
def delete_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    if request.method == "POST":
        feedback.delete()
        messages.success(request, "Feedback deleted.")
        return redirect('manage_feedback')
    return render(request, 'adminpanel/confirm_delete.html', {'object': feedback, 'type': 'Feedback'})


@staff_member_required
def manage_order_status(request):
    """Manage order and booking statuses"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('status')

        if order_id:
            order = get_object_or_404(Order, id=order_id)
            order.order_status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
        elif booking_id:
            booking = get_object_or_404(PortraitBooking, id=booking_id)
            booking.booking_status = new_status
            booking.save()
            messages.success(request, f"Booking #{booking.id} status updated to {new_status}.")

        return redirect('manage_order_status')

    # Get all orders and bookings
    orders = Order.objects.select_related('user').order_by('-created_at')
    bookings = PortraitBooking.objects.select_related('user').order_by('-created_at')

    context = {
        'orders': orders,
        'bookings': bookings,
        'order_status_choices': Order.ORDER_STATUS_CHOICES,
        'booking_status_choices': PortraitBooking.BOOKING_STATUS_CHOICES,
    }
    return render(request, 'adminpanel/manage_order_status.html', context)


@staff_member_required
def reset_user_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        temp_password = request.POST.get('temp_password')
        if username and temp_password:
            try:
                user = User.objects.get(username=username)
                user.set_password(temp_password)
                user.save()
                user.profile.is_temp_password = True
                user.profile.save()
                messages.success(request, f"Password reset for user {username}. They will be required to change it on next login.")
                return redirect('admin_dashboard')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Please provide both username and temporary password.")
    return render(request, 'adminpanel/reset_password.html')





