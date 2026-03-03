# Django Media Files Configuration Guide
## Complete Solution for Image Loading Issues

---

## Part 1: Common Causes of Image Loading Issues

### 1.1 MEDIA_URL and MEDIA_ROOT Misconfiguration ❌ FIXED
- ✅ Already configured correctly in settings.py

### 1.2 Static vs Media Confusion
- STATIC_URL = `/static/` → CSS, JS, admin files (collected via `collectstatic`)
- MEDIA_URL = `/media/` → User-uploaded files (images, documents)

### 1.3 Missing Media Serving in urls.py ❌ FIXED
- ✅ Already configured for DEBUG=True mode

### 1.4 DEBUG=False Behavior ❌ NEEDS FIX
- When DEBUG=False, Django doesn't serve media files
- Need external server (Nginx/Apache) or cloud storage

### 1.5 Wrong Image Paths in Database
- Paths should be RELATIVE (e.g., `categories/image.jpg`)
- Should NOT be absolute paths

### 1.6 Not Copying Media Files to Server ❌ NEEDS FIX
- Must copy media folder to production server

### 1.7 File Permission Issues (Linux Server) ❌ NEEDS FIX
- Need correct ownership and permissions

---

## Part 2: Current Configuration Analysis

### Your settings.py (artstore/settings.py) - ✅ CORRECT:
```
python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Your urls.py (artstore/urls.py) - ✅ CORRECT for Development:
```
python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your url patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Template Usage - ✅ CORRECT:
```
html
<img src="{{ category.image.url }}" alt="{{ category.name }}">
<img src="{{ product.image.url }}" alt="{{ product.title }}">
```

---

## Part 3: How to Fix Image Loading Issues

### FIX 1: Running on Another Computer (Development)

**Problem:** Images work locally but not on another system

**Solution:**
```
bash
# 1. Make sure media folder exists in project root
ls -la media/

# 2. If not exists, create it
mkdir -p media

# 3. Ensure DEBUG=True in settings or environment
export DEBUG=True

# 4. Run server
python manage.py runserver
```

---

### FIX 2: Hosting on Server (DEBUG=False / Production)

**Problem:** Images don't load when DEBUG=False

**Solution Options:**

#### Option A: Nginx Configuration (Recommended for VPS/Server)
```
nginx
# /etc/nginx/sites-available/yourproject

server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/your/project;
    
    # Django application
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Static files (CSS, JS)
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files (User-uploaded images) - CRITICAL FOR IMAGES
    location /media/ {
        alias /path/to/your/project/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

#### Option B: Apache Configuration
```
apache
# /etc/apache2/sites-available/yourproject.conf

<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /path/to/your/project
    
    # Media files - CRITICAL
    Alias /media/ /path/to/your/project/media/
    
    <Directory /path/to/your/project/media>
        Require all granted
        Options -Indexes
    </Directory>
    
    # Static files
    Alias /static/ /path/to/your/project/staticfiles/
    
    <Directory /path/to/your/project/staticfiles>
        Require all granted
    </Directory>
    
    # Gunicorn proxy
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

#### Option C: Using WhiteNoise (Simple Alternative)
```
bash
# Install whitenoise
pip install whitenoise
```

```
python
# settings.py - Add to MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... other middleware
]

# Update STATICFILES_STORAGE
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# For media files, also add:
MEDIAFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

---

### FIX 3: Cloud Storage (Recommended for Scalability)

#### Using AWS S3:
```
bash
pip install django-storages boto3
```

```
python
# settings.py
INSTALLED_APPS = [
    # ...
    'storages',
]

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# Use S3 for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# For static files
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
```

#### Using Cloudinary (Great for Heroku/Render):
```
bash
pip install cloudinary django-cloudinary-storage
```

```
python
# settings.py
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="your_cloud_name",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = 'https://res.cloudinary.com/your_cloud_name/image/upload/'
```

---

## Part 4: Working Django Model Examples

### Model: Category
```
python
# shop/models.py
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('paintings', 'Paintings'),
        ('pencil', 'Pencil Drawings'),
        ('caricature', 'Caricatures'),
    ]
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    def __str__(self):
        return self.get_name_display()
```

### Model: Product
```
python
# shop/models.py
class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')  # Saved to MEDIA_ROOT/products/
    slug = models.SlugField(max_length=255, unique=True)
    
    def __str__(self):
        return self.title
```

---

## Part 5: Image Upload Form & View

### Form:
```
python
# shop/forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'category', 'price', 'image']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
```

### View:
```
python
# shop/views.py
from django.shortcuts import render, redirect
from .forms import ProductForm

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})
```

---

## Part 6: Displaying Images in Templates

### Basic Usage:
```
html
<!-- Single image -->
<img src="{{ product.image.url }}" alt="{{ product.title }}">

<!-- With fallback -->
{% if product.image %}
    <img src="{{ product.image.url }}" alt="{{ product.title }}">
{% else %}
    <img src="{% static 'images/no-image.png' %}" alt="No image">
{% endif %}

<!-- Category image -->
{% if category.image %}
    <img src="{{ category.image.url }}" alt="{{ category.name }}">
{% endif %}
```

### With CSS styling:
```
html
<img src="{{ product.image.url }}" 
     alt="{{ product.title }}" 
     class="img-responsive" 
     style="max-width: 100%; height: auto;">
```

---

## Part 7: Debugging Steps

### Step 1: Verify Image URL in Django Shell
```
bash
python manage.py shell
```

```python
from shop.models import Category

# Get first category
cat = Category.objects.first()

# Check image path
print(cat.image.url)    # Should print: /media/categories/filename.jpg
print(cat.image.path)   # Should print: full filesystem path to file
```

### Step 2: Verify File Actually Exists
```
python
import os
from django.conf import settings

cat = Category.objects.first()
if cat.image:
    full_path = os.path.join(settings.MEDIA_ROOT, cat.image.name)
    print(f"Full path: {full_path}")
    print(f"File exists: {os.path.exists(full_path)}")
```

### Step 3: Test Image URL Directly
```
# In browser, visit:
http://localhost:8000/media/categories/your-image.jpg
```

If this returns 404, the issue is with media serving.

### Step 4: Check Network Tab in Browser
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Reload page
4. Look for failed image requests (red 404 errors)
5. Check the actual URL being requested

### Step 5: Server Permissions (Linux)
```
bash
# Check media directory
ls -la /path/to/project/media/

# Fix ownership (Ubuntu/Debian)
sudo chown -R www-data:www-data /path/to/project/media/

# Fix ownership (CentOS/RHEL)
sudo chown -R apache:apache /path/to/project/media/

# Fix permissions
sudo chmod -R 755 /path/to/project/media/
```

---

## Part 8: Deployment Checklist

### Development (Local Machine)
- [x] MEDIA_ROOT defined in settings.py
- [x] MEDIA_URL defined in settings.py
- [x] static() in urls.py with DEBUG check
- [x] Images stored in media/ folder

### Production (VPS/Server)
- [ ] DEBUG=False in settings.py
- [ ] ALLOWED_HOSTS includes your domain
- [ ] Nginx/Apache configured for /media/
- [ ] Media folder copied to server
- [ ] File permissions correct (755 for folders, 644 for files)
- [ ] Run: `python manage.py collectstatic`

### Cloud Hosting (Heroku/Render/AWS)
- [ ] DEBUG=False
- [ ] Cloud storage configured (S3/Cloudinary)
- [ ] ALLOWED_HOSTS configured

---

## Part 9: Quick Fix Commands

### Fix Permissions (Linux Server):
```
bash
# Navigate to project
cd /path/to/your/project

# Fix media folder
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/

# Fix static folder
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/
```

### Collect Static Files:
```
bash
python manage.py collectstatic
```

### Test Server:
```
bash
# Test media URL directly
curl -I http://localhost:8000/media/categories/test.jpg
```

---

## Summary

Your Django project is **already correctly configured** for development. The issues you're experiencing are:

1. **On another computer**: Make sure to copy the `media/` folder or run migrations properly
2. **In production (DEBUG=False)**: Configure Nginx/Apache to serve media files OR use cloud storage

For the quickest fix when running on another system, ensure:
```
bash
# 1. Media folder exists
mkdir -p media

# 2. Run with DEBUG=True
export DEBUG=True

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

For production, use the Nginx configuration provided in Option A above.
