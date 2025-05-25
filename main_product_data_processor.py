"""
Main Product Data Processor
Orchestrates data collection from all sources and generates ranked product list
"""
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Import scrapers and normalizer
try:
    from google_trends import GoogleTrendsAnalyzer
except ImportError:
    logging.warning("Google Trends module not found - using mock data")
    GoogleTrendsAnalyzer = None

try:
    from aliexpress_scraper import AliExpressScraper
except ImportError:
    logging.warning("AliExpress scraper not found - using mock data")
    AliExpressScraper = None

try:
    from amazon_scraper import AmazonScraper
except ImportError:
    logging.warning("Amazon scraper not found - using mock data")
    AmazonScraper = None

try:
    from tiktok_scraper import TikTokScraper
except ImportError:
    logging.warning("TikTok scraper not found - using mock data")
    TikTokScraper = None

from product_normaliser import ProductNormalizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductDataProcessor:
    def __init__(self):
        self.normalizer = ProductNormalizer()
        self.results = {}
        
        # Target keywords for product research
        self.target_keywords = [
            'electric lint remover',
            'phone holder car',
            'led strip lights',
            'wireless earbuds',
            'portable blender',
            'car phone mount',
            'bluetooth speaker',
            'fitness tracker',
            'laptop stand',
            'phone case'
        ]
    
    def collect_google_trends_data(self):
        """Collect Google Trends data"""
        logger.info("🔍 Collecting Google Trends data...")
        
        if GoogleTrendsAnalyzer is None:
            logger.warning("Using mock Google Trends data")
            return self.get_mock_trends_data()
        
        try:
            trends_analyzer = GoogleTrendsAnalyzer()
            trends_data = []
            
            for keyword in self.target_keywords:
                try:
                    result = trends_analyzer.analyze_keyword(keyword)
                    if result:
                        trends_data.append(result)
                except Exception as e:
                    logger.error(f"Failed to get trends for '{keyword}': {e}")
                    continue
            
            logger.info(f"✅ Collected trends data for {len(trends_data)} keywords")
            return trends_data
            
        except Exception as e:
            logger.error(f"Google Trends collection failed: {e}")
            return self.get_mock_trends_data()
    
    def collect_aliexpress_data(self):
        """Collect AliExpress product data"""
        logger.info("🛒 Collecting AliExpress data...")
        
        if AliExpressScraper is None:
            logger.warning("Using mock AliExpress data")
            return self.get_mock_aliexpress_data()
        
        try:
            ali_scraper = AliExpressScraper()
            ali_products = []
            
            for keyword in self.target_keywords:
                try:
                    products = ali_scraper.search_products(keyword, max_results=3)
                    ali_products.extend(products)
                except Exception as e:
                    logger.error(f"Failed to scrape AliExpress for '{keyword}': {e}")
                    continue
            
            logger.info(f"✅ Collected {len(ali_products)} AliExpress products")
            return ali_products
            
        except Exception as e:
            logger.error(f"AliExpress collection failed: {e}")
            return self.get_mock_aliexpress_data()
    
    def collect_amazon_data(self):
        """Collect Amazon product data"""
        logger.info("📦 Collecting Amazon data...")
        
        if AmazonScraper is None:
            logger.warning("Using mock Amazon data")
            return self.get_mock_amazon_data()
        
        try:
            amz_scraper = AmazonScraper()
            amz_products = []
            
            for keyword in self.target_keywords:
                try:
                    products = amz_scraper.search_products(keyword, max_results=3)
                    amz_products.extend(products)
                except Exception as e:
                    logger.error(f"Failed to scrape Amazon for '{keyword}': {e}")
                    continue
            
            logger.info(f"✅ Collected {len(amz_products)} Amazon products")
            return amz_products
            
        except Exception as e:
            logger.error(f"Amazon collection failed: {e}")
            return self.get_mock_amazon_data()
    
    def collect_tiktok_data(self):
        """Collect TikTok viral data"""
        logger.info("🎵 Collecting TikTok data...")
        
        if TikTokScraper is None:
            logger.warning("Using mock TikTok data")
            return self.get_mock_tiktok_data()
        
        try:
            tiktok_scraper = TikTokScraper()
            tiktok_videos = []
            
            for keyword in self.target_keywords:
                try:
                    videos = tiktok_scraper.search_videos(keyword, max_results=5)
                    tiktok_videos.extend(videos)
                except Exception as e:
                    logger.error(f"Failed to scrape TikTok for '{keyword}': {e}")
                    continue
            
            logger.info(f"✅ Collected {len(tiktok_videos)} TikTok videos")
            return tiktok_videos
            
        except Exception as e:
            logger.error(f"TikTok collection failed: {e}")
            return self.get_mock_tiktok_data()
    
    def get_mock_trends_data(self):
        """Provide mock Google Trends data for testing"""
        return [
            {
                'keyword': 'electric lint remover',
                'momentum': 1.8,
                'avg_interest': 72,
                'max_interest': 89,
                'related_queries': ['fabric shaver', 'lint brush', 'clothes defuzzer']
            },
            {
                'keyword': 'phone holder car',
                'momentum': 1.2,
                'avg_interest': 65,
                'max_interest': 84,
                'related_queries': ['car phone mount', 'dashboard holder', 'windshield mount']
            },
            {
                'keyword': 'led strip lights',
                'momentum': 0.9,
                'avg_interest': 58,
                'max_interest': 76,
                'related_queries': ['rgb led strip', 'smart led lights', 'room decoration']
            },
            {
                'keyword': 'wireless earbuds',
                'momentum': -0.2,
                'avg_interest': 82,
                'max_interest': 95,
                'related_queries': ['bluetooth earbuds', 'noise cancelling', 'true wireless']
            },
            {
                'keyword': 'portable blender',
                'momentum': 1.5,
                'avg_interest': 48,
                'max_interest': 67,
                'related_queries': ['personal blender', 'smoothie maker', 'travel blender']
            }
        ]
    
    def get_mock_aliexpress_data(self):
        """Provide mock AliExpress data for testing"""
        return [
            {
                'name': 'Electric Lint Remover Fabric Shaver',
                'orders': 15420,
                'reviews': 892,
                'rating': 4.4,
                'price': 12.99,
                'url': 'https://www.aliexpress.com/item/mock-lint-remover'
            },
            {
                'name': 'Car Phone Holder Dashboard Mount',
                'orders': 8750,
                'reviews': 634,
                'rating': 4.2,
                'price': 8.50,
                'url': 'https://www.aliexpress.com/item/mock-phone-holder'
            },
            {
                'name': 'RGB LED Strip Lights Smart',
                'orders': 12300,
                'reviews': 756,
                'rating': 4.1,
                'price': 18.99,
                'url': 'https://www.aliexpress.com/item/mock-led-strip'
            },
            {
                'name': 'Bluetooth Wireless Earbuds',
                'orders': 32100,
                'reviews': 1845,
                'rating': 4.3,
                'price': 22.50,
                'url': 'https://www.aliexpress.com/item/mock-earbuds'
            },
            {
                'name': 'Portable Blender USB Rechargeable',
                'orders': 6890,
                'reviews': 423,
                'rating': 4.0,
                'price': 15.75,
                'url': 'https://www.aliexpress.com/item/mock-blender'
            }
        ]
    
    def get_mock_amazon_data(self):
        """Provide mock Amazon data for testing"""
        return [
            {
                'name': 'Electric Lint Remover - Fabric Defuzzer',
                'reviews': 2340,
                'rating': 4.1,
                'price': 16.99,
                'bsr': 125,
                'is_prime': True,
                'url': 'https://www.amazon.com/mock-lint-remover'
            },
            {
                'name': 'Phone Holder for Car Dashboard',
                'reviews': 1890,
                'rating': 4.0,
                'price': 12.99,
                'bsr': 89,
                'is_prime': True,
                'url': 'https://www.amazon.com/mock-phone-holder'
            },
            {
                'name': 'LED Strip Lights RGB Color Changing',
                'reviews': 3450,
                'rating': 4.2,
                'price': 24.99,
                'bsr': 156,
                'is_prime': True,
                'url': 'https://www.amazon.com/mock-led-strip'
            },
            {
                'name': 'Wireless Earbuds Bluetooth 5.0',
                'reviews': 8920,
                'rating': 4.3,
                'price': 29.99,
                'bsr': 45,
                'is_prime': True,
                'url': 'https://www.amazon.com/mock-earbuds'
            },
            {
                'name': 'Portable Blender Personal Size',
                'reviews': 1250,
                'rating': 3.9,
                'price': 19.99,
                'bsr': 234,
                'is_prime': True,
                'url': 'https://www.amazon.com/mock-blender'
            }
        ]
    
    def get_mock_tiktok_data(self):
        """Provide mock TikTok data for testing"""
        return [
            {
                'title': 'This lint remover is AMAZING! #lintremover #cleaning #satisfying',
                'views': 2150000,
                'likes': 189000,
                'comments': 3400,
                'shares': 12500,
                'url': 'https://www.tiktok.com/@user/video/mock-lint',
                'hashtags': ['lintremover', 'cleaning', 'satisfying']
            },
            {
                'title': 'Best phone holder for your car! #phoneholder #cardrive #musthave',
                'views': 850000,
                'likes': 67000,
                'comments': 1200,
                'shares': 4500,
                'url': 'https://www.tiktok.com/@user/video/mock-phone',
                'hashtags': ['phoneholder', 'cardrive', 'musthave']
            },
            {
                'title': 'LED lights room transformation! #ledlights #roomdecor #aesthetic',
                'views': 1200000,
                'likes': 98000,
                'comments': 2800,
                'shares': 8900,
                'url': 'https://www.tiktok.com/@user/video/mock-led',
                'hashtags': ['ledlights', 'roomdecor', 'aesthetic']
            },
            {
                'title': 'Testing cheap wireless earbuds #earbuds #tech #review',
                'views': 650000,
                'likes': 45000,
                'comments': 890,
                'shares': 2100,
                'url': 'https://www.tiktok.com/@user/video/mock-earbuds',
                'hashtags': ['earbuds', 'tech', 'review']
            },
            {
                'title': 'Portable blender hack for smoothies! #blender #smoothie #healthy',
                'views': 920000,
                'likes': 72000,
                'comments': 1800,
                'shares': 5600,
                'url': 'https://www.tiktok.com/@user/video/mock-blender',
                'hashtags': ['blender', 'smoothie', 'healthy']
            }
        ]
    
    def process_all_data(self):
        """Main processing pipeline"""
        logger.info("🚀 Starting product data processing...")
        
        try:
            # Collect data from all sources
            trends_data = self.collect_google_trends_data()
            ali_data = self.collect_aliexpress_data()
            amz_data = self.collect_amazon_data()
            tiktok_data = self.collect_tiktok_data()
            
            # Add data to normalizer
            self.normalizer.add_trend_data(trends_data)
            self.normalizer.add_aliexpress_data(ali_data)
            self.normalizer.add_amazon_data(amz_data)
            self.normalizer.add_tiktok_data(tiktok_data)
            
            # Calculate scores and get top products
            top_products = self.normalizer.get_top_products(20)
            
            # Export to CSV
            csv_success = self.normalizer.export_to_csv('products_scored.csv', top_n=50)
            
            # Save to JSON for web interface
            self.save_results_json(top_products)
            
            # Print summary
            stats = self.normalizer.get_summary_stats()
            self.print_summary(top_products[:5], stats, csv_success)
            
            return top_products
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def save_results_json(self, products):
        """Save results to JSON file for web interface"""
        try:
            results_data = {
                'timestamp': datetime.now().isoformat(),
                'products': products,
                'total_count': len(products)
            }
            
            with open('products_results.json', 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Saved results to products_results.json")
            
        except Exception as e:
            logger.error(f"Failed to save JSON results: {e}")
    
    def print_summary(self, top_products, stats, csv_success):
        """Print processing summary"""
        print("\n" + "="*80)
        print("🏆 DROPSHIPPING PRODUCT RANKINGS - TOP 5")
        print("="*80)
        
        for i, product in enumerate(top_products, 1):
            print(f"\n{i}. {product['product_name']}")
            print(f"   📊 Score: {product['score']}")
            print(f"   📈 Trend Momentum: {product['trend_momentum']}")
            print(f"   🛒 AliExpress Orders: {product['orders']:,}")
            print(f"   🎵 TikTok Views: {product['tiktok_views']}")
            print(f"   ⭐ Amazon Reviews: {product['reviews']:,}")
            print(f"   🔗 Sources: {', '.join(product['data_sources'])}")
        
        print(f"\n📈 SUMMARY STATISTICS")
        print(f"   Total Products Analyzed: {stats['total_products']}")
        print(f"   Products with Multiple Sources: {stats['products_with_multiple_sources']}")
        print(f"   Average Score: {stats['avg_composite_score']}")
        print(f"   Highest Score: {stats['top_score']}")
        
        if csv_success:
            print(f"\n✅ Results exported to products_scored.csv")
        else:
            print(f"\n❌ Failed to export CSV")
        
        print("="*80)

def main():
    """Main entry point"""
    processor = ProductDataProcessor()
    results = processor.process_all_data()
    
    if results:
        print(f"\n🎉 Processing completed successfully!")
        print(f"Found {len(results)} ranked products")
    else:
        print(f"\n❌ Processing failed - check logs for details")

if __name__ == "__main__":
    main()