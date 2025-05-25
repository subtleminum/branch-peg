"""
Flask Web Interface for Dropshipping Product Rankings
Displays ranked products in a clean, responsive interface
"""
from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dropshipping-product-ranker-2024'

class ProductWebInterface:
    def __init__(self):
        self.products_data = []
        self.load_products_data()
    
    def load_products_data(self):
        """Load products data from JSON file"""
        try:
            if os.path.exists('products_results.json'):
                with open('products_results.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.products_data = data.get('products', [])
                    logger.info(f"Loaded {len(self.products_data)} products from JSON")
            else:
                logger.warning("products_results.json not found - using sample data")
                self.products_data = self.get_sample_data()
        except Exception as e:
            logger.error(f"Failed to load products data: {e}")
            self.products_data = self.get_sample_data()
    
    def get_sample_data(self):
        """Provide sample data when JSON file is not available"""
        return [
            {
                "product_name": "Electric Lint Remover",
                "score": 0.87,
                "trend_momentum": 1.8,
                "trend_slope": 1.8,
                "ali_orders": 15420,
                "orders": 15420,
                "ali_reviews": 892,
                "amz_reviews": 2340,
                "reviews": 2340,
                "tiktok_total_views": 2150000,
                "tiktok_views": "2.1M",
                "tiktok_videos": 12,
                "ali_url": "https://www.aliexpress.com/item/mock-lint-remover",
                "link_ali": "https://www.aliexpress.com/item/mock-lint-remover",
                "amz_url": "https://www.amazon.com/mock-lint-remover",
                "link_amazon": "https://www.amazon.com/mock-lint-remover",
                "tiktok_url": "https://www.tiktok.com/@user/video/mock-lint",
                "link_tiktok": "https://www.tiktok.com/@user/video/mock-lint",
                "related_queries": ["fabric shaver", "lint brush", "clothes defuzzer"],
                "data_sources": ["Google Trends", "AliExpress", "Amazon", "TikTok"],
                "ali_price": 12.99,
                "amz_price": 16.99,
                "ali_rating": 4.4,
                "amz_rating": 4.1
            },
            {
                "product_name": "Portable Blender USB Rechargeable",
                "score": 0.72,
                "trend_momentum": 1.5,
                "trend_slope": 1.5,
                "ali_orders": 6890,
                "orders": 6890,
                "ali_reviews": 423,
                "amz_reviews": 1250,
                "reviews": 1250,
                "tiktok_total_views": 920000,
                "tiktok_views": "920K",
                "tiktok_videos": 8,
                "ali_url": "https://www.aliexpress.com/item/mock-blender",
                "link_ali": "https://www.aliexpress.com/item/mock-blender",
                "amz_url": "https://www.amazon.com/mock-blender",
                "link_amazon": "https://www.amazon.com/mock-blender",
                "tiktok_url": "https://www.tiktok.com/@user/video/mock-blender",
                "link_tiktok": "https://www.tiktok.com/@user/video/mock-blender",
                "related_queries": ["personal blender", "smoothie maker", "travel blender"],
                "data_sources": ["Google Trends", "AliExpress", "Amazon", "TikTok"],
                "ali_price": 15.75,
                "amz_price": 19.99,
                "ali_rating": 4.0,
                "amz_rating": 3.9
            },
            {
                "product_name": "Car Phone Holder Dashboard Mount",
                "score": 0.68,
                "trend_momentum": 1.2,
                "trend_slope": 1.2,
                "ali_orders": 8750,
                "orders": 8750,
                "ali_reviews": 634,
                "amz_reviews": 1890,
                "reviews": 1890,
                "tiktok_total_views": 850000,
                "tiktok_views": "850K",
                "tiktok_videos": 6,
                "ali_url": "https://www.aliexpress.com/item/mock-phone-holder",
                "link_ali": "https://www.aliexpress.com/item/mock-phone-holder",
                "amz_url": "https://www.amazon.com/mock-phone-holder",
                "link_amazon": "https://www.amazon.com/mock-phone-holder",
                "tiktok_url": "https://www.tiktok.com/@user/video/mock-phone",
                "link_tiktok": "https://www.tiktok.com/@user/video/mock-phone",
                "related_queries": ["car phone mount", "dashboard holder", "windshield mount"],
                "data_sources": ["Google Trends", "AliExpress", "Amazon", "TikTok"],
                "ali_price": 8.50,
                "amz_price": 12.99,
                "ali_rating": 4.2,
                "amz_rating": 4.0
            },
            {
                "product_name": "RGB LED Strip Lights Smart",
                "score": 0.65,
                "trend_momentum": 0.9,
                "trend_slope": 0.9,
                "ali_orders": 12300,
                "orders": 12300,
                "ali_reviews": 756,
                "amz_reviews": 3450,
                "reviews": 3450,
                "tiktok_total_views": 1200000,
                "tiktok_views": "1.2M",
                "tiktok_videos": 15,
                "ali_url": "https://www.aliexpress.com/item/mock-led-strip",
                "link_ali": "https://www.aliexpress.com/item/mock-led-strip",
                "amz_url": "https://www.amazon.com/mock-led-strip",
                "link_amazon": "https://www.amazon.com/mock-led-strip",
                "tiktok_url": "https://www.tiktok.com/@user/video/mock-led",
                "link_tiktok": "https://www.tiktok.com/@user/video/mock-led",
                "related_queries": ["rgb led strip", "smart led lights", "room decoration"],
                "data_sources": ["Google Trends", "AliExpress", "Amazon", "TikTok"],
                "ali_price": 18.99,
                "amz_price": 24.99,
                "ali_rating": 4.1,
                "amz_rating": 4.2
            },
            {
                "product_name": "Bluetooth Wireless Earbuds",
                "score": 0.58,
                "trend_momentum": -0.2,
                "trend_slope": -0.2,
                "ali_orders": 32100,
                "orders": 32100,
                "ali_reviews": 1845,
                "amz_reviews": 8920,
                "reviews": 8920,
                "tiktok_total_views": 650000,
                "tiktok_views": "650K",
                "tiktok_videos": 4,
                "ali_url": "https://www.aliexpress.com/item/mock-earbuds",
                "link_ali": "https://www.aliexpress.com/item/mock-earbuds",
                "amz_url": "https://www.amazon.com/mock-earbuds",
                "link_amazon": "https://www.amazon.com/mock-earbuds",
                "tiktok_url": "https://www.tiktok.com/@user/video/mock-earbuds",
                "link_tiktok": "https://www.tiktok.com/@user/video/mock-earbuds",
                "related_queries": ["bluetooth earbuds", "noise cancelling", "true wireless"],
                "data_sources": ["Google Trends", "AliExpress", "Amazon", "TikTok"],
                "ali_price": 22.50,
                "amz_price": 29.99,
                "ali_rating": 4.3,
                "amz_rating": 4.3
            }
        ]
    
    def get_products(self, limit=None):
        """Get products data with optional limit"""
        if limit:
            return self.products_data[:limit]
        return self.products_data
    
    def refresh_data(self):
        """Refresh products data from file"""
        self.load_products_data()

# Initialize web interface
web_interface = ProductWebInterface()

@app.route('/')
def index():
    """Main dashboard page"""
    products = web_interface.get_products(20)  # Show top 20
    
    # Calculate summary statistics
    total_products = len(web_interface.products_data)
    avg_score = sum(p.get('score', 0) for p in products) / max(len(products), 1)
    top_score = max((p.get('score', 0) for p in products), default=0)
    
    stats = {
        'total_products': total_products,
        'avg_score': round(avg_score, 3),
        'top_score': round(top_score, 3),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return render_template('dashboard.html', products=products, stats=stats)

@app.route('/api/products')
def api_products():
    """API endpoint to get products data"""
    limit = request.args.get('limit', type=int)
    products = web_interface.get_products(limit)
    
    return jsonify({
        'success': True,
        'products': products,
        'total_count': len(web_interface.products_data)
    })

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh data"""
    try:
        web_interface.refresh_data()
        return jsonify({
            'success': True,
            'message': 'Data refreshed successfully',
            'total_products': len(web_interface.products_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export/csv')
def api_export_csv():
    """API endpoint to export CSV"""
    try:
        from flask import send_file
        if os.path.exists('products_scored.csv'):
            return send_file('products_scored.csv', as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'CSV file not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    products = web_interface.get_products()
    
    if 0 <= product_id < len(products):
        product = products[product_id]
        return render_template('product_detail.html', product=product)
    else:
        return "Product not found", 404

# Create templates directory and files
def create_templates():
    """Create HTML templates for Flask app"""
    import os
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dropshipping Product Rankings</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* Header */
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; border-radius: 15px; margin-bottom: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        
        /* Stats Cards */
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); text-align: center; }
        .stat-card h3 { color: #667eea; font-size: 1.8em; margin-bottom: 5px; }
        .stat-card p { color: #666; font-size: 0.9em; }
        
        /* Controls */
        .controls { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 0.9em; transition: all 0.3s; }
        .btn:hover { background: #5a67d8; transform: translateY(-1px); }
        
        /* Product Grid */
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
        .product-card { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); transition: all 0.3s; border-left: 4px solid #667eea; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
        
        .product-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
        .product-name { font-size: 1.3em; font-weight: 600; color: #333; margin-bottom: 5px; line-height: 1.3; }
        .score-badge { background: linear-gradient(135deg, #48bb78, #38a169); color: white; padding: 8px 15px; border-radius: 20px; font-weight: 600; font-size: 1.1em; }
        
        .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0; }
        .metric { text-align: center; }
        .metric-value { font-size: 1.4em; font-weight: 600; color: #667eea; }
        .metric-label { font-size: 0.8em; color: #666; margin-top: 2px; }
        
        .sources { margin: 15px 0; }
        .source-tag { display: inline-block; background: #e2e8f0; color: #4a5568; padding: 4px 8px; border-radius: 12px; font-size: 0.75em; margin: 2px; }
        
        .links { display: flex; gap: 10px; margin-top: 15px; }
        .link-btn { flex: 1; padding: 8px 12px; border-radius: 6px; text-decoration: none; text-align: center; font-size: 0.85em; font-weight: 500; transition: all 0.3s; }
        .link-ali { background: #ff6b35; color: white; }
        .link-amazon { background: #ff9900; color: white; }
        .link-tiktok { background: #ff0050; color: white; }
        .link-btn:hover { opacity: 0.8; transform: scale(1.02); }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 2em; }
            .products-grid { grid-template-columns: 1fr; }
            .metrics { grid-template-columns: 1fr; }
            .links { flex-direction: column; }
        }
        
        /* Loading and Empty States */
        .loading { text-align: center; padding: 50px; color: #666; }
        .empty-state { text-align: center; padding: 50px; background: white; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 Dropshipping Product Rankings</h1>
            <p>AI-powered analysis of trending products across Google Trends, AliExpress, Amazon & TikTok</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{{ stats.total_products }}</h3>
                <p>Total Products Analyzed</p>
            </div>
            <div class="stat-card">
                <h3>{{ "%.3f"|format(stats.avg_score) }}</h3>
                <p>Average Score</p>
            </div>
            <div class="stat-card">
                <h3>{{ "%.3f"|format(stats.top_score) }}</h3>
                <p>Highest Score</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.last_updated }}</h3>
                <p>Last Updated</p>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
            <button class="btn" onclick="exportCSV()" style="margin-left: 10px;">📊 Export CSV</button>
        </div>
        
        {% if products %}
        <div class="products-grid">
            {% for product in products %}
            <div class="product-card">
                <div class="product-header">
                    <div>
                        <div class="product-name">{{ product.product_name }}</div>
                    </div>
                    <div class="score-badge">{{ "%.3f"|format(product.score) }}</div>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{{ "{:,}".format(product.orders) }}</div>
                        <div class="metric-label">AliExpress Orders</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ product.tiktok_views }}</div>
                        <div class="metric-label">TikTok Views</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ "%.2f"|format(product.trend_slope) }}</div>
                        <div class="metric-label">Trend Momentum</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ "{:,}".format(product.reviews) }}</div>
                        <div class="metric-label">Amazon Reviews</div>
                    </div>
                </div>
                
                <div class="sources">
                    {% for source in product.data_sources %}
                    <span class="source-tag">{{ source }}</span>
                    {% endfor %}
                </div>
                
                <div class="links">
                    {% if product.link_ali %}
                    <a href="{{ product.link_ali }}" class="link-btn link-ali" target="_blank">AliExpress</a>
                    {% endif %}
                    {% if product.link_amazon %}
                    <a href="{{ product.link_amazon }}" class="link-btn link-amazon" target="_blank">Amazon</a>
                    {% endif %}
                    {% if product.link_tiktok %}
                    <a href="{{ product.link_tiktok }}" class="link-btn link-tiktok" target="_blank">TikTok</a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <h3>No products found</h3>
            <p>Run the data processor to analyze products</p>
        </div>
        {% endif %}
    </div>
    
    <script>
        function refreshData() {
            const btn = event.target;
            btn.textContent = '🔄 Refreshing...';
            btn.disabled = true;
            
            fetch('/api/refresh')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Failed to refresh data: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('Error refreshing data: ' + error);
                })
                .finally(() => {
                    btn.textContent = '🔄 Refresh Data';
                    btn.disabled = false;
                });
        }
        
        function exportCSV() {
            window.open('/api/export/csv', '_blank');
        }
    </script>
</body>
</html>'''
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    logger.info("Created HTML templates")

# Initialize templates on startup
create_templates()