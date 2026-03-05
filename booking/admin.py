from django.contrib import admin
from django.utils.html import format_html
from .models import PortraitBooking


@admin.register(PortraitBooking)
class PortraitBookingAdmin(admin.ModelAdmin):
    # ============================================================
    # UPDATED: Added frame_type to list_display - Part 1
    # ============================================================
    list_display = ['id', 'name', 'size', 'frame_type', 'booking_status', 'price', 'created_at']
    list_filter = ['booking_status', 'created_at', 'frame_type', 'category']
    search_fields = ['name', 'email', 'phone', 'frame_type', 'category']
    readonly_fields = ['created_at', 'user', 'price']
    
    # ============================================================
    # UPDATED: Added frame_type and category to fieldsets - Part 1 & 2
    # ============================================================
    fieldsets = (
        ('User Info', {'fields': ('user', 'name', 'email', 'phone')}),
        ('Address', {'fields': ('address', 'district', 'state', 'pincode')}),
        ('Booking Details', {
            'fields': (
                'category', 'size', 'frame_type',  # Added frame_type - Part 1
                'preferred_date', 'price', 'reference_image', 'description'
            )
        }),
        ('Status', {'fields': ('booking_status', 'created_at')}),
    )

    def reference_image_tag(self, obj):
        if obj.reference_image:
            return format_html('<a href="{}" target="_blank">Download / View</a>', obj.reference_image.url)
        return '-'
    reference_image_tag.short_description = 'Reference Image'
