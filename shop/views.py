from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse
import json

from .forms import CheckoutForm
from .models import CartItem, Category, Order, OrderItem, Product
from booking.forms import INDIA_STATE_DISTRICTS


def home(request):
    # Define custom ordering for specific categories
    # Required order: Paintings, Mural Paintings, Stencil Artworks, Pencil Drawings, Pen Art, then others (caricature last)
    category_order = {
        'paintings': 1,
        'mural': 2,
        'stencil': 3,
        'pencil': 4,
        'pen_art': 5,
        'ghibli_art': 99,  # Second to last
        'caricature': 100,  # Last
    }
    
    def get_sort_key(category):
        """Return sort key: defined categories get explicit order, others get high order to maintain relative order"""
        return category_order.get(category.name, 100)
    
    categories = sorted(Category.objects.all(), key=get_sort_key)

    # Handle search and category filtering
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search')

    # Featured Gallery: Select exactly ONE product from EACH category
    # Get the latest product from each category that has products
    featured_products = []
    for category in categories:
        # Get the latest product in this category (by created_at)
        product = category.products.order_by('-created_at').first()
        if product:
            featured_products.append(product)

    # Start with base queryset for shop section
    products = Product.objects.order_by('-created_at')

    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            products = Product.objects.none()

    if search_query:
        products = products.filter(title__icontains=search_query) | products.filter(description__icontains=search_query)

    # Apply slice after filtering
    products = products[:6]

    return render(request, 'home.html', {'products': featured_products, 'categories': categories})


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'category.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get('quantity', 1))
    qty = max(1, qty)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += qty
    else:
        cart_item.quantity = qty
    cart_item.save()
    messages.success(request, f"Added {product.title} to cart.")
    if request.POST.get('buy_now'):
        return redirect('checkout')
    return redirect('cart')


@login_required
def cart_view(request):
    items = CartItem.objects.filter(user_id=request.user.id).select_related('product')
    subtotal = sum(item.line_total for item in items)
    return render(request, 'cart.html', {'items': items, 'subtotal': subtotal})


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    qty = int(request.POST.get('quantity', 1))
    cart_item.quantity = max(1, qty)
    cart_item.save()
    messages.success(request, "Cart updated.")
    return redirect('cart')


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')


@login_required
def buy_now_direct(request, product_id):
    """Handle Buy Now button click - creates a temporary order for single product only"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.stock == 0:
        messages.error(request, f"{product.title} is out of stock.")
        return redirect('product_detail', slug=product.slug)
    
    # Get quantity from POST or GET
    qty = int(request.POST.get('quantity', request.GET.get('quantity', 1)))
    qty = max(1, qty)
    
    # Validate quantity doesn't exceed stock
    if qty > product.stock:
        messages.error(request, f"Only {product.stock} items available in stock.")
        return redirect('product_detail', slug=product.slug)
    
    # Calculate total for this single product
    product_total = qty * product.price
    
    # Store buy now data in session (NOT in cart - completely separate flow)
    request.session['buy_now_data'] = {
        'product_id': product.id,
        'product_title': product.title,
        'quantity': qty,
        'price': float(product.price),
        'total': float(product_total),
    }
    request.session['buy_now_total'] = str(product_total)
    
    # Clear any existing checkout data to avoid confusion
    if 'checkout_data' in request.session:
        del request.session['checkout_data']
    
    # Redirect to checkout for Buy Now flow
    return redirect('buy_now_checkout')


@login_required
def buy_now_checkout(request):
    """Checkout page specifically for Buy Now - only shows the single product"""
    buy_now_data = request.session.get('buy_now_data')
    
    if not buy_now_data:
        messages.warning(request, "No product selected for purchase.")
        return redirect('home')
    
    # Get product to verify it's still available
    try:
        product = Product.objects.get(id=buy_now_data['product_id'])
    except Product.DoesNotExist:
        messages.error(request, "Product no longer available.")
        return redirect('home')
    
    # Check stock again
    if product.stock == 0:
        messages.error(request, f"{product.title} is now out of stock.")
        del request.session['buy_now_data']
        return redirect('home')
    
    # Prepare item for display
    item = type('obj', (object,), {
        'product': product,
        'quantity': buy_now_data['quantity'],
        'line_total': buy_now_data['total']
    })()
    
    subtotal = buy_now_data['total']
    
    initial = {
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
    }
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Store checkout data with buy_now flag
            checkout_data = form.cleaned_data
            checkout_data['is_buy_now'] = True
            request.session['checkout_data'] = checkout_data
            request.session['checkout_total'] = str(subtotal)
            return redirect('payment_portal')
    else:
        form = CheckoutForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'items': [item],
        'subtotal': subtotal,
        'is_buy_now': True,
        'buy_now_product': buy_now_data,
        'state_district_map': json.dumps(INDIA_STATE_DISTRICTS)
    }
    return render(request, 'checkout.html', context)


def _create_order_from_buy_now(user, checkout_data, buy_now_data):
    """Create order from Buy Now flow - only creates order for the single product"""
    product = Product.objects.get(id=buy_now_data['product_id'])
    
    order = Order.objects.create(
        user_id=user.id,
        shipping_name=checkout_data.get('name'),
        shipping_email=checkout_data.get('email'),
        shipping_phone=checkout_data.get('phone'),
        shipping_address=checkout_data.get('address'),
        shipping_district=checkout_data.get('district'),
        shipping_state=checkout_data.get('state'),
        shipping_pincode=checkout_data.get('pincode'),
        payment_status='paid',
        order_status='pending',
    )
    
    # Create only ONE order item for the Buy Now product
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=buy_now_data['quantity'],
        price=product.price,
    )
    
    # Reduce stock for the single product
    if product.stock >= buy_now_data['quantity']:
        product.stock -= buy_now_data['quantity']
        product.save(update_fields=['stock'])
    
    order.update_totals()
    return order


@login_required
def checkout(request):
    items = CartItem.objects.filter(user_id=request.user.id).select_related('product')
    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('home')
    # Check for out of stock items
    out_of_stock_items = [item for item in items if item.product.stock == 0]
    if out_of_stock_items:
        for item in out_of_stock_items:
            messages.error(request, f"{item.product.title} is out of stock. Please remove it from your cart.")
        return redirect('cart')
    subtotal = sum(item.line_total for item in items)

    initial = {
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
    }
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            request.session['checkout_data'] = form.cleaned_data
            request.session['checkout_total'] = str(subtotal)
            return redirect('payment_portal')
    else:
        form = CheckoutForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'state_district_map': json.dumps(INDIA_STATE_DISTRICTS)
    }
    return render(request, 'checkout.html', context)


@login_required
def payment_portal(request):
    booking_id = request.session.get('booking_pending')
    if booking_id:
        from booking.models import PortraitBooking
        booking = PortraitBooking.objects.filter(id=booking_id, user_id=request.user.id).first()
        if not booking:
            messages.error(request, "Booking not found.")
            return redirect('booking')
        subtotal = booking.price
        return render(request, 'payment_portal.html', {'items': [], 'subtotal': subtotal, 'booking': booking})

    # Check if this is a Buy Now order (single product, not cart-based)
    buy_now_data = request.session.get('buy_now_data')
    if buy_now_data:
        # This is a Buy Now flow - get only the single product
        try:
            product = Product.objects.get(id=buy_now_data['product_id'])
            item = type('obj', (object,), {
                'product': product,
                'quantity': buy_now_data['quantity'],
                'line_total': buy_now_data['total']
            })()
            subtotal = buy_now_data['total']
            checkout_data = request.session.get('checkout_data')
            if not checkout_data:
                return redirect('buy_now_checkout')
            return render(request, 'payment_portal.html', {
                'items': [item], 
                'subtotal': subtotal,
                'is_buy_now': True,
                'buy_now_product': buy_now_data
            })
        except Product.DoesNotExist:
            messages.error(request, "Product no longer available.")
            return redirect('home')

    # Regular cart-based checkout
    items = CartItem.objects.filter(user_id=request.user.id).select_related('product')
    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('home')
    subtotal = sum(item.line_total for item in items)
    checkout_data = request.session.get('checkout_data')
    if not checkout_data:
        return redirect('checkout')
    return render(request, 'payment_portal.html', {'items': items, 'subtotal': subtotal})


@login_required
def order_success(request, order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id, user_id=user.id)
    return render(request, 'order_success.html', {'order': order})


def order_failed(request):
    messages.error(request, "Payment failed. Please try again.")
    return render(request, 'order_failed.html')


def _create_order_from_cart(user, checkout_data):
    items = CartItem.objects.filter(user_id=user.id).select_related('product')
    order = Order.objects.create(
        user_id=user.id,
        shipping_name=checkout_data.get('name'),
        shipping_email=checkout_data.get('email'),
        shipping_phone=checkout_data.get('phone'),
        shipping_address=checkout_data.get('address'),
        shipping_district=checkout_data.get('district'),
        shipping_state=checkout_data.get('state'),
        shipping_pincode=checkout_data.get('pincode'),
        payment_status='paid',
        order_status='pending',
    )
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )
        # reduce stock safely
        if item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
            item.product.save(update_fields=['stock'])
    order.update_totals()
    items.delete()
    return order


@login_required
def simulate_success(request):
    checkout_data = request.session.get('checkout_data')
    booking_id = request.session.get('booking_pending')
    buy_now_data = request.session.get('buy_now_data')
    user = request.user
    # Force evaluation of lazy proxy by accessing .id early
    user_id = user.id
    
    # Handle Portrait Booking payment
    if booking_id:
        from booking.models import PortraitBooking
        booking = PortraitBooking.objects.filter(id=booking_id, user_id=user_id).first()
        if booking:
            booking.booking_status = 'paid'
            booking.save(update_fields=['booking_status'])
            request.session.pop('booking_pending', None)
            return redirect('booking_success', booking_id=booking.id)
    
    # Handle Buy Now order (single product, not cart-based)
    if buy_now_data and checkout_data and checkout_data.get('is_buy_now'):
        order = _create_order_from_buy_now(request.user, checkout_data, buy_now_data)
        # Clear all session data
        request.session.pop('checkout_data', None)
        request.session.pop('checkout_total', None)
        request.session.pop('buy_now_data', None)
        request.session.pop('buy_now_total', None)
        return redirect('order_success', order_id=order.id)
    
    # Handle regular cart-based order
    if not checkout_data:
        return redirect('checkout')
    order = _create_order_from_cart(request.user, checkout_data)
    request.session.pop('checkout_data', None)
    request.session.pop('checkout_total', None)
    return redirect('order_success', order_id=order.id)


@login_required
def simulate_failure(request):
    request.session.pop('checkout_data', None)
    request.session.pop('checkout_total', None)
    request.session.pop('booking_pending', None)
    messages.error(request, "Payment failed.")
    return redirect('order_failed')


@login_required
def place_order_cod(request):
    """Place an order for Cash On Delivery without processing card payment.
    Expects a POST request. Returns JSON with redirect URL to dashboard.
    """
    if request.method != 'POST':
        return redirect('payment_portal')

    checkout_data = request.session.get('checkout_data')
    booking_id = request.session.get('booking_pending')
    user = request.user
    # Force evaluation of lazy proxy by accessing .id early
    user_id = user.id

    if booking_id:
        from booking.models import PortraitBooking
        booking = PortraitBooking.objects.filter(id=booking_id, user_id=user_id).first()
        if booking:
            # mark booking as pending payment (COD)
            booking.booking_status = 'pending'
            booking.save(update_fields=['booking_status'])
            request.session.pop('booking_pending', None)
            return JsonResponse({'redirect_url': reverse('booking_success', args=[booking.id])})

    if not checkout_data:
        return JsonResponse({'redirect_url': reverse('checkout')})

    # Create order (uses helper which defaults to paid) then change status to pending for COD
    order = _create_order_from_cart(user, checkout_data)
    order.payment_status = 'pending'
    order.save(update_fields=['payment_status'])
    request.session.pop('checkout_data', None)
    request.session.pop('checkout_total', None)
    messages.success(request, "Order placed. Please pay on delivery.")
    return JsonResponse({'redirect_url': reverse('user_dashboard')})
