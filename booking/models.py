from django.conf import settings
from django.db import models
import django.utils.timezone


from django.conf import settings
from django.db import models
import django.utils.timezone


class PortraitBooking(models.Model):
    # ============================================================
    # FRAME TYPE CHOICES - Added for Part 1
    # ============================================================
    FRAME_CHOICES = [
        ('Plastic', 'Plastic'),
        ('Wooden', 'Wooden'),
        ('Metal', 'Metal'),
        ('Premium Wooden', 'Premium Wooden'),
        ('Vintage Gold', 'Vintage Gold'),
        ('Matte Black', 'Matte Black'),
    ]
    
    # ============================================================
    # UPDATED CATEGORY CHOICES - Part 2
    # Now includes: Caricature, Pen Art, Painting, Pencil Drawing, Stencil Art
    # ============================================================
    CATEGORY_CHOICES = [
        ('caricature', 'Caricature'),
        ('pen_art', 'Pen Art'),
        ('paintings', 'Painting'),
        ('pencil', 'Pencil Drawing'),
        ('stencil', 'Stencil Art'),
    ]
    
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    district = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    pincode = models.CharField(max_length=15)
    
    # ============================================================
    # NEW FIELD: frame_type - Part 1
    # ============================================================
    frame_type = models.CharField(
        max_length=50, 
        choices=FRAME_CHOICES, 
        blank=True, 
        default='',
        help_text="Select frame type for your portrait"
    )
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='paintings')
    reference_image = models.ImageField(upload_to='bookings/', blank=True, null=True)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=50)
    preferred_date = models.DateField(blank=True, null=True)  # Optional - removed from form
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portrait_bookings')

    def __str__(self):
        return f"PortraitBooking {self.id} - {self.name}"


class Size(models.Model):
    name = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference_image = models.ImageField(upload_to='size_references/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.dimensions})"
