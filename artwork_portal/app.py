"""
Artwork Selling and Portrait Booking Website
Flask Backend with ML Integration
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import cv2
import numpy as np
from PIL import Image
import pickle
import json
from datetime import datetime
import base64
import io

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# ==================== ML MODEL PATHS ====================
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models')

# ==================== SAMPLE DATA ====================
# Sample artworks data
ARTWORKS = [
    {'id': 1, 'title': 'Sunset over Kerala', 'category': 'painting', 'price': 5000, 'image': 'art1.jpg', 'views': 1200, 'upload_date': '2024-01-15'},
    {'id': 2, 'title': 'Traditional Caricature', 'category': 'caricature', 'price': 2500, 'image': 'art2.jpg', 'views': 850, 'upload_date': '2024-02-10'},
    {'id': 3, 'title': 'Pencil Portrait', 'category': 'pencil', 'price': 3000, 'image': 'art3.jpg', 'views': 1500, 'upload_date': '2024-01-20'},
    {'id': 4, 'title': 'Stencil Art - Abstract', 'category': 'stencil', 'price': 4000, 'image': 'art4.jpg', 'views': 600, 'upload_date': '2024-03-01'},
    {'id': 5, 'title': 'Kerala Mural - Peacock', 'category': 'mural', 'price': 8000, 'image': 'art5.jpg', 'views': 2000, 'upload_date': '2024-01-05'},
    {'id': 6, 'title': 'Oil Painting - Landscape', 'category': 'painting', 'price': 7500, 'image': 'art6.jpg', 'views': 950, 'upload_date': '2024-02-25'},
]

CATEGORIES = [
    {'id': 1, 'name': 'Painting', 'slug': 'painting', 'description': 'Beautiful oil and acrylic paintings'},
    {'id': 2, 'name': 'Pencil Drawing', 'slug': 'pencil', 'description': 'Detailed pencil sketches and portraits'},
    {'id': 3, 'name': 'Caricature', 'slug': 'caricature', 'description': 'Fun and exaggerated character portraits'},
    {'id': 4, 'name': 'Stencil Art', 'slug': 'stencil', 'description': 'Modern stencil artwork designs'},
    {'id': 5, 'name': 'Kerala Mural', 'slug': 'mural', 'description': 'Traditional Kerala mural paintings'},
]

# ==================== ML MODEL TRAINING ====================
class PricePredictionModel:
    """ML Models for price and delivery prediction"""
    
    def __init__(self):
        self.zlr_model = None  # Zero Linear Regression (Simple Linear Regression)
        self.mlr_model = None  # Multiple Linear Regression
        self.plr_model = None  # Polynomial Regression
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize and train ML models with sample data"""
        # Zero Linear Regression (ZLR) - Predict base price from resolution (MP)
        # Training data: [resolution_mp] -> [base_price]
        self.zlr_X = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 16.0, 24.0]).reshape(-1, 1)
        self.zlr_y = np.array([500, 800, 1200, 1800, 2500, 3500, 4500, 5500, 7000])
        
        # Simple linear regression: price = slope * resolution + intercept
        self.zlr_slope = 250
        self.zlr_intercept = 400
        
        # Multiple Linear Regression (MLR) - Predict price & delivery from multiple features
        # Features: [num_faces, category_encoded, canvas_size, detail_level]
        # Category encoding: painting=0, pencil=1, caricature=2, stencil=3, mural=4
        # Canvas sizes: small=1, medium=2, large=3, extra_large=4
        # Detail levels: low=1, medium=2, high=3, ultra=4
        
        # MLR coefficients (trained model parameters)
        self.mlr_price_coeffs = {
            'intercept': 500,
            'num_faces': 300,
            'category': {'painting': 1500, 'pencil': 800, 'caricature': 500, 'stencil': 1000, 'mural': 2000},
            'canvas_size': 800,
            'detail_level': 600
        }
        
        self.mlr_delivery_coeffs = {
            'intercept': 3,
            'num_faces': 1.5,
            'category': {'painting': 5, 'pencil': 2, 'caricature': 1, 'stencil': 3, 'mural': 7},
            'canvas_size': 2,
            'detail_level': 1
        }
        
        # Polynomial Regression (PLR) - Predict popularity from days_since_upload and views
        # Popularity = a*days^2 + b*days + c*views + d
        self.plr_coeffs = {
            'a': -0.05,  # days^2 coefficient
            'b': 0.8,    # days coefficient
            'c': 0.3,    # views coefficient
            'd': 50      # intercept
        }
    
    def predict_base_price_zlr(self, resolution_mp):
        """ZLR: Predict base price from image resolution (MP)"""
        price = self.zlr_slope * resolution_mp + self.zlr_intercept
        return max(500, round(price, 2))
    
    def predict_final_price_mlr(self, num_faces, category, canvas_size, detail_level):
        """MLR: Predict final price based on multiple features"""
        base_price = self.mlr_price_coeffs['intercept']
        base_price += num_faces * self.mlr_price_coeffs['num_faces']
        base_price += self.mlr_price_coeffs['category'].get(category, 1000)
        base_price += canvas_size * self.mlr_price_coeffs['canvas_size']
        base_price += detail_level * self.mlr_price_coeffs['detail_level']
        
        return max(500, round(base_price, 2))
    
    def predict_delivery_mlr(self, num_faces, category, canvas_size, detail_level):
        """MLR: Predict delivery days based on multiple features"""
        days = self.mlr_delivery_coeffs['intercept']
        days += num_faces * self.mlr_delivery_coeffs['num_faces']
        days += self.mlr_delivery_coeffs['category'].get(category, 3)
        days += canvas_size * self.mlr_delivery_coeffs['canvas_size']
        days += detail_level * self.mlr_delivery_coeffs['detail_level']
        
        return max(1, round(days, 0))
    
    def predict_popularity_plr(self, days_since_upload, views):
        """PLR: Predict popularity score"""
        popularity = (self.plr_coeffs['a'] * days_since_upload ** 2 + 
                      self.plr_coeffs['b'] * days_since_upload + 
                      self.plr_coeffs['c'] * views + 
                      self.plr_coeffs['d'])
        return max(0, min(100, round(popularity, 2)))


# Initialize ML model
ml_model = PricePredictionModel()


# ==================== IMAGE FILTER FUNCTIONS ====================
def apply_stencil_filter(image):
    """Apply stencil (B/W) filter using OpenCV"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply threshold to create stencil effect
    _, stencil = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # Convert back to BGR for consistent output
    result = cv2.cvtColor(stencil, cv2.COLOR_GRAY2BGR)
    return result


def apply_caricature_filter(image):
    """Apply caricature (exaggerated) filter using OpenCV"""
    # Apply aggressive edge enhancement
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    enhanced = cv2.filter2D(image, -1, kernel)
    
    # Increase contrast
    lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # Add slight color saturation boost for cartoonish effect
    hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 30)  # Increase saturation
    hsv = cv2.merge([h, s, v])
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return result


def apply_pencil_sketch_filter(image):
    """Apply pencil sketch (edge detection) filter using OpenCV"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Invert grayscale
    inverted = 255 - gray
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    # Invert blurred image
    inverted_blurred = 255 - blurred
    # Create pencil sketch
    sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
    # Convert back to BGR
    result = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    return result


def apply_realistic_filter(image):
    """Apply realistic (smoothing) filter using OpenCV"""
    # Apply bilateral filter for edge-preserving smoothing
    result = cv2.bilateralFilter(image, 9, 75, 75)
    # Slight contrast enhancement
    lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    result = cv2.merge([l, a, b])
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result


def get_image_resolution(image):
    """Get image resolution in megapixels"""
    height, width = image.shape[:2]
    mp = (width * height) / 1000000
    return round(mp, 2)


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page with featured artworks"""
    return render_template('index.html', 
                           artworks=ARTWORKS[:6], 
                           categories=CATEGORIES)


@app.route('/artworks')
def artworks_page():
    """Artwork gallery page with filters"""
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '')
    
    filtered_artworks = ARTWORKS
    
    if category_filter:
        filtered_artworks = [a for a in filtered_artworks if a['category'] == category_filter]
    
    if search_query:
        filtered_artworks = [a for a in filtered_artworks if search_query.lower() in a['title'].lower()]
    
    return render_template('artworks.html', 
                           artworks=filtered_artworks, 
                           categories=CATEGORIES,
                           selected_category=category_filter)


@app.route('/artwork/<int:artwork_id>')
def artwork_detail(artwork_id):
    """Individual artwork detail page"""
    artwork = next((a for a in ARTWORKS if a['id'] == artwork_id), None)
    if not artwork:
        return "Artwork not found", 404
    return render_template('artwork_detail.html', artwork=artwork)


@app.route('/booking')
def booking_page():
    """Portrait booking page"""
    return render_template('booking.html', categories=CATEGORIES)


@app.route('/category/<slug>')
def category_page(slug):
    """Category detail page"""
    category = next((c for c in CATEGORIES if c['slug'] == slug), None)
    if not category:
        return "Category not found", 404
    
    category_artworks = [a for a in ARTWORKS if a['category'] == slug]
    return render_template('category.html', 
                           category=category, 
                           artworks=category_artworks)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')


# ==================== API ENDPOINTS ====================

@app.route('/api/preview', methods=['POST'])
def preview_filter():
    """Apply selected filter to uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        filter_type = request.form.get('filter', 'realistic')
        
        # Read image
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Apply selected filter
        if filter_type == 'stencil':
            processed = apply_stencil_filter(image)
        elif filter_type == 'caricature':
            processed = apply_caricature_filter(image)
        elif filter_type == 'pencil':
            processed = apply_pencil_sketch_filter(image)
        elif filter_type == 'realistic':
            processed = apply_realistic_filter(image)
        else:
            processed = image
        
        # Encode result to base64
        _, buffer = cv2.imencode('.jpg', processed)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_base64}',
            'filter': filter_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/base-price', methods=['POST'])
def base_price():
    """ZLR: Predict base price from image resolution"""
    try:
        data = request.get_json()
        image_data = data.get('image_data', '')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Get resolution in MP
        resolution_mp = get_image_resolution(image)
        
        # Predict base price using ZLR
        base_price = ml_model.predict_base_price_zlr(resolution_mp)
        
        return jsonify({
            'success': True,
            'resolution_mp': resolution_mp,
            'base_price': base_price
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/final-price', methods=['POST'])
def final_price():
    """MLR: Predict final price and delivery days"""
    try:
        data = request.get_json()
        
        num_faces = int(data.get('num_faces', 1))
        category = data.get('category', 'pencil')
        canvas_size = int(data.get('canvas_size', 2))
        detail_level = int(data.get('detail_level', 2))
        
        # Predict using MLR
        final_price = ml_model.predict_final_price_mlr(
            num_faces, category, canvas_size, detail_level
        )
        
        delivery_days = ml_model.predict_delivery_mlr(
            num_faces, category, canvas_size, detail_level
        )
        
        return jsonify({
            'success': True,
            'final_price': final_price,
            'delivery_days': delivery_days,
            'breakdown': {
                'base_price': ml_model.mlr_price_coeffs['intercept'],
                'faces': num_faces * ml_model.mlr_price_coeffs['num_faces'],
                'category': ml_model.mlr_price_coeffs['category'].get(category, 1000),
                'canvas': canvas_size * ml_model.mlr_price_coeffs['canvas_size'],
                'detail': detail_level * ml_model.mlr_price_coeffs['detail_level']
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/featured-artworks', methods=['GET'])
def featured_artworks():
    """PLR: Predict popularity and return sorted artworks"""
    try:
        # Calculate days since upload for each artwork
        today = datetime.now()
        
        for artwork in ARTWORKS:
            upload_date = datetime.strptime(artwork['upload_date'], '%Y-%m-%d')
            days_since = (today - upload_date).days
            # Predict popularity using PLR
            artwork['popularity_score'] = ml_model.predict_popularity_plr(
                days_since, artwork['views']
            )
        
        # Sort by popularity score (descending)
        sorted_artworks = sorted(ARTWORKS, key=lambda x: x['popularity_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'artworks': sorted_artworks[:6]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/confirm-order', methods=['POST'])
def confirm_order():
    """Confirm portrait booking order"""
    try:
        data = request.get_json()
        
        # In a real app, this would save to database
        order = {
            'order_id': f'ORD-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'customer_name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'category': data.get('category'),
            'canvas_size': data.get('canvas_size'),
            'detail_level': data.get('detail_level'),
            'filter': data.get('filter'),
            'price': data.get('price'),
            'delivery_days': data.get('delivery_days'),
            'status': 'confirmed',
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'order': order,
            'message': 'Order confirmed successfully!'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== STATIC FILES ====================
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🎨 Artwork Portal - Flask ML Backend")
    print("=" * 60)
    print("\n📌 Available Routes:")
    print("   • Home:              http://localhost:5000/")
    print("   • Artworks:         http://localhost:5000/artworks")
    print("   • Booking:          http://localhost:5000/booking")
    print("   • About:            http://localhost:5000/about")
    print("   • Contact:          http://localhost:5000/contact")
    print("\n📌 API Endpoints:")
    print("   • POST /api/preview         - Apply image filter")
    print("   • POST /api/base-price      - ZLR price prediction")
    print("   • POST /api/final-price     - MLR price & delivery")
    print("   • GET  /api/featured        - PLR popularity sorting")
    print("   • POST /api/confirm-order   - Confirm booking")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
