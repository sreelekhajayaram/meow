from django.apps import apps


def categories(request):
    if apps.is_installed('shop'):
        Category = apps.get_model('shop', 'Category')
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
        
        nav_categories = sorted(Category.objects.all(), key=get_sort_key)
        return {'nav_categories': nav_categories}
    return {'nav_categories': []}


def cart_count(request):
    if request.user.is_authenticated and apps.is_installed('shop'):
        CartItem = apps.get_model('shop', 'CartItem')
        return {'cart_count': CartItem.objects.filter(user=request.user).count()}
    return {'cart_count': 0}

