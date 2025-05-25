"""
Product data normalizer and scorer
Combines data from all sources and calculates composite scores
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime
import re
import logging
import csv
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductNormalizer:
    def __init__(self):
        self.products_data = []
        self.normalized_products = []
        
        # Scoring weights as per specification
        self.weights = {
            'trend_momentum': 0.35,
            'aliexpress_velocity': 0.25,
            'tiktok_virality': 0.20,
            'amazon_popularity': 0.15,
            'competition_penalty': -0.10
        }
    
    def add_trend_data(self, trend_results):
        """Add Google Trends data"""
        logger.info(f"Adding trend data for {len(trend_results)} keywords")
        
        for trend in trend_results:
            product_name = trend.get('keyword', '')
            
            # Find or create product entry
            product = self.find_or_create_product(product_name)
            product.update({
                'trend_momentum': trend.get('momentum', 0),
                'trend_avg_interest': trend.get('avg_interest', 0),
                'trend_max_interest': trend.get('max_interest', 0),
                'related_queries': trend.get('related_queries', []),
                'has_trend_data': True
            })
    
    def add_aliexpress_data(self, aliexpress_products):
        """Add AliExpress product data"""
        logger.info(f"Adding AliExpress data for {len(aliexpress_products)} products")
        
        for ali_product in aliexpress_products:
            product_name = self.clean_product_name(ali_product.get('name', ''))
            
            # Find matching product or create new one
            product = self.find_or_create_product(product_name)
            product.update({
                'ali_orders': ali_product.get('orders', 0),
                'ali_reviews': ali_product.get('reviews', 0),
                'ali_rating': ali_product.get('rating', 0),
                'ali_price': ali_product.get('price', 0),
                'ali_url': ali_product.get('url', ''),
                'has_ali_data': True
            })
    
    def add_amazon_data(self, amazon_products):
        """Add Amazon product data"""
        logger.info(f"Adding Amazon data for {len(amazon_products)} products")
        
        for amz_product in amazon_products:
            product_name = self.clean_product_name(amz_product.get('name', ''))
            
            # Find matching product or create new one
            product = self.find_or_create_product(product_name)
            product.update({
                'amz_reviews': amz_product.get('reviews', 0),
                'amz_rating': amz_product.get('rating', 0),
                'amz_price': amz_product.get('price', 0),
                'amz_bsr': amz_product.get('bsr', 999),
                'amz_is_prime': amz_product.get('is_prime', False),
                'amz_url': amz_product.get('url', ''),
                'has_amz_data': True
            })
    
    def add_tiktok_data(self, tiktok_videos):
        """Add TikTok viral data"""
        logger.info(f"Processing {len(tiktok_videos)} TikTok videos")
        
        # Group videos by product mentions
        product_mentions = {}
        
        for video in tiktok_videos:
            if not video:
                continue
                
            title = video.get('title', '')
            hashtags = video.get('hashtags', [])
            
            # Extract potential product names from title and hashtags
            potential_products = self.extract_products_from_video(title, hashtags)
            
            for product_keyword in potential_products:
                if product_keyword not in product_mentions:
                    product_mentions[product_keyword] = {
                        'videos': [],
                        'total_views': 0,
                        'total_likes': 0,
                        'total_comments': 0,
                        'total_shares': 0,
                        'sample_url': ''
                    }
                
                product_mentions[product_keyword]['videos'].append(video)
                product_mentions[product_keyword]['total_views'] += video.get('views', 0)
                product_mentions[product_keyword]['total_likes'] += video.get('likes', 0)
                product_mentions[product_keyword]['total_comments'] += video.get('comments', 0)
                product_mentions[product_keyword]['total_shares'] += video.get('shares', 0)
                
                # Store first video URL as sample
                if not product_mentions[product_keyword]['sample_url'] and video.get('url'):
                    product_mentions[product_keyword]['sample_url'] = video.get('url')
        
        # Add aggregated TikTok data to products
        for product_keyword, mention_data in product_mentions.items():
            product = self.find_or_create_product(product_keyword)
            
            video_count = len(mention_data['videos'])
            product.update({
                'tiktok_video_count': video_count,
                'tiktok_total_views': mention_data['total_views'],
                'tiktok_total_likes': mention_data['total_likes'],
                'tiktok_total_comments': mention_data['total_comments'],
                'tiktok_total_shares': mention_data['total_shares'],
                'tiktok_avg_views': mention_data['total_views'] / max(video_count, 1),
                'tiktok_url': mention_data['sample_url'],
                'tiktok_sample_videos': mention_data['videos'][:3],  # Keep sample videos
                'has_tiktok_data': True
            })
    
    def find_or_create_product(self, product_name):
        """Find existing product or create new one"""
        clean_name = self.clean_product_name(product_name)
        
        if not clean_name or len(clean_name) < 3:
            return {}
        
        # Look for existing product with similar name
        for product in self.products_data:
            if self.are_similar_products(product.get('name', ''), clean_name):
                return product
        
        # Create new product
        new_product = {
            'name': clean_name,
            'created_at': datetime.now().isoformat(),
            'has_trend_data': False,
            'has_ali_data': False,
            'has_amz_data': False,
            'has_tiktok_data': False
        }
        
        self.products_data.append(new_product)
        return new_product
    
    def clean_product_name(self, name):
        """Clean and standardize product names"""
        if not name:
            return ''
        
        # Remove common prefixes/suffixes
        clean_name = re.sub(r'^(New|Hot|Best|Top|Premium|Professional)\s+', '', name, flags=re.I)
        clean_name = re.sub(r'\s+(Set|Kit|Pack|Bundle|Piece|Pcs)$', '', clean_name, flags=re.I)
        
        # Remove excessive punctuation and numbers
        clean_name = re.sub(r'[^\w\s-]', ' ', clean_name)
        clean_name = re.sub(r'\b\d+\s*(pcs?|pieces?|set|pack)\b', '', clean_name, flags=re.I)
        
        # Normalize whitespace
        clean_name = ' '.join(clean_name.split())
        
        return clean_name.strip()[:100]  # Limit length
    
    def are_similar_products(self, name1, name2):
        """Check if two product names refer to similar products"""
        if not name1 or not name2:
            return False
        
        # Normalize names
        norm1 = set(name1.lower().split())
        norm2 = set(name2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(norm1.intersection(norm2))
        union = len(norm1.union(norm2))
        
        if union == 0:
            return False
        
        similarity = intersection / union
        return similarity > 0.6  # 60% similarity threshold
    
    def extract_products_from_video(self, title, hashtags):
        """Extract potential product keywords from video title and hashtags"""
        products = set()
        
        if not title:
            return list(products)
        
        # Common product patterns in titles
        product_patterns = [
            r'(\w+\s+\w+)\s+(?:review|unboxing|haul)',
            r'(?:review|trying|testing)\s+(\w+\s+\w+)',
            r'(\w+\s+\w+)\s+(?:from|on)\s+(?:amazon|aliexpress)',
            r'(?:amazing|viral|must.have)\s+(\w+(?:\s+\w+)?)',
        ]
        
        title_lower = title.lower()
        
        for pattern in product_patterns:
            matches = re.findall(pattern, title_lower, re.I)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                products.add(match.strip())
        
        # Extract from hashtags
        for hashtag in hashtags:
            # Skip generic hashtags
            if hashtag.lower() not in ['viral', 'trending', 'fyp', 'foryou', 'tiktok']:
                if len(hashtag) > 3:
                    products.add(hashtag)
        
        # Clean and filter products
        cleaned_products = []
        for product in products:
            cleaned = self.clean_product_name(product)
            if len(cleaned) > 5 and len(cleaned.split()) >= 2:  # Multi-word products
                cleaned_products.append(cleaned)
        
        return cleaned_products[:5]  # Limit to top 5 per video
    
    def normalize_scores(self):
        """Normalize all metrics to 0-1 scale using min-max normalization"""
        if not self.products_data:
            logger.warning("No products data to normalize")
            return
        
        df = pd.DataFrame(self.products_data)
        
        # Define metrics to normalize with realistic ranges
        metrics_config = {
            'trend_momentum': {'min_val': -2, 'max_val': 2},
            'trend_avg_interest': {'min_val': 0, 'max_val': 100},
            'ali_orders': {'min_val': 0, 'max_val': 50000},
            'ali_reviews': {'min_val': 0, 'max_val': 5000},
            'amz_reviews': {'min_val': 0, 'max_val': 50000},
            'amz_bsr': {'min_val': 1, 'max_val': 1000, 'reverse': True},  # Lower BSR is better
            'tiktok_total_views': {'min_val': 0, 'max_val': 10000000},
            'tiktok_video_count': {'min_val': 0, 'max_val': 100}
        }
        
        # Fill missing values with 0
        for metric in metrics_config.keys():
            if metric not in df.columns:
                df[metric] = 0
            df[metric] = df[metric].fillna(0)
        
        # Normalize each metric
        for metric, config in metrics_config.items():
            min_val = config.get('min_val', df[metric].min())
            max_val = config.get('max_val', df[metric].max())
            
            if max_val > min_val:
                if config.get('reverse', False):
                    # For metrics where lower is better (like BSR)
                    df[f'{metric}_normalized'] = 1 - ((df[metric] - min_val) / (max_val - min_val))
                else:
                    df[f'{metric}_normalized'] = (df[metric] - min_val) / (max_val - min_val)
            else:
                df[f'{metric}_normalized'] = 0.5  # Default if no variation
            
            # Clip to 0-1 range
            df[f'{metric}_normalized'] = df[f'{metric}_normalized'].clip(0, 1)
        
        self.normalized_df = df
        logger.info(f"Normalized scores for {len(df)} products")
    
    def calculate_composite_scores(self):
        """Calculate final composite scores using weighted metrics"""
        if not hasattr(self, 'normalized_df'):
            self.normalize_scores()
        
        df = self.normalized_df.copy()
        
        # Calculate component scores
        df['trend_score'] = df.get('trend_momentum_normalized', 0) * 0.7 + \
                           df.get('trend_avg_interest_normalized', 0) * 0.3
        
        df['ali_velocity_score'] = df.get('ali_orders_normalized', 0) * 0.6 + \
                                  df.get('ali_reviews_normalized', 0) * 0.4
        
        df['amz_popularity_score'] = df.get('amz_reviews_normalized', 0) * 0.5 + \
                                    df.get('amz_bsr_normalized', 0) * 0.5
        
        df['tiktok_virality_score'] = df.get('tiktok_total_views_normalized', 0) * 0.7 + \
                                     df.get('tiktok_video_count_normalized', 0) * 0.3
        
        # Competition penalty (high reviews = saturated market)
        df['competition_score'] = (df.get('amz_reviews_normalized', 0) + 
                                  df.get('ali_reviews_normalized', 0)) / 2
        
        # Calculate final composite score using specified weights
        df['composite_score'] = (
            df['trend_score'] * self.weights['trend_momentum'] +
            df['ali_velocity_score'] * self.weights['aliexpress_velocity'] +
            df['tiktok_virality_score'] * self.weights['tiktok_virality'] +
            df['amz_popularity_score'] * self.weights['amazon_popularity'] +
            df['competition_score'] * self.weights['competition_penalty']
        )
        
        # Ensure score is between 0 and 1
        df['composite_score'] = df['composite_score'].clip(0, 1)
        
        # Sort by composite score
        df = df.sort_values('composite_score', ascending=False)
        
        self.scored_df = df
        logger.info("Calculated composite scores for all products")
        
        return df
    
    def get_top_products(self, n=10):
        """Get top N products by composite score"""
        if not hasattr(self, 'scored_df'):
            self.calculate_composite_scores()
        
        top_products = []
        
        for _, row in self.scored_df.head(n).iterrows():
            product = {
                'product_name': row.get('name', ''),
                'score': round(row.get('composite_score', 0), 3),
                'trend_momentum': round(row.get('trend_momentum', 0), 3),
                'trend_slope': round(row.get('trend_momentum', 0), 2),  # Alias for compatibility
                'ali_orders': int(row.get('ali_orders', 0)),
                'orders': int(row.get('ali_orders', 0)),  # Alias for compatibility
                'ali_reviews': int(row.get('ali_reviews', 0)),
                'amz_reviews': int(row.get('amz_reviews', 0)),
                'reviews': int(row.get('amz_reviews', 0)),  # Alias for compatibility
                'tiktok_total_views': int(row.get('tiktok_total_views', 0)),
                'tiktok_views': self.format_number(row.get('tiktok_total_views', 0)),  # Formatted
                'tiktok_videos': int(row.get('tiktok_video_count', 0)),
                'ali_url': row.get('ali_url', ''),
                'link_ali': row.get('ali_url', ''),  # Alias for compatibility
                'amz_url': row.get('amz_url', ''),
                'link_amazon': row.get('amz_url', ''),  # Alias for compatibility
                'tiktok_url': row.get('tiktok_url', ''),
                'link_tiktok': row.get('tiktok_url', ''),  # Alias for compatibility
                'related_queries': row.get('related_queries', []),
                'data_sources': self.get_data_sources(row),
                'ali_price': round(row.get('ali_price', 0), 2),
                'amz_price': round(row.get('amz_price', 0), 2),
                'ali_rating': round(row.get('ali_rating', 0), 1),
                'amz_rating': round(row.get('amz_rating', 0), 1)
            }
            
            top_products.append(product)
        
        return top_products
    
    def format_number(self, num):
        """Format large numbers (e.g., 1200000 -> '1.2M')"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(int(num))
    
    def get_data_sources(self, row):
        """Get list of data sources for a product"""
        sources = []
        if row.get('has_trend_data', False):
            sources.append('Google Trends')
        if row.get('has_ali_data', False):
            sources.append('AliExpress') 
        if row.get('has_amz_data', False):
            sources.append('Amazon')
        if row.get('has_tiktok_data', False):
            sources.append('TikTok')
        return sources
    
    def export_to_csv(self, filename='products_scored.csv', top_n=50):
        """Export scored products to CSV file"""
        if not hasattr(self, 'scored_df'):
            self.calculate_composite_scores()
        
        # Get top products
        top_products = self.get_top_products(top_n)
        
        if not top_products:
            logger.warning("No products to export")
            return False
        
        # Define CSV columns
        csv_columns = [
            'product_name', 'score', 'trend_momentum', 'trend_slope',
            'ali_orders', 'orders', 'ali_reviews', 'amz_reviews', 'reviews',
            'tiktok_total_views', 'tiktok_views', 'tiktok_videos',
            'ali_price', 'amz_price', 'ali_rating', 'amz_rating',
            'link_ali', 'link_amazon', 'link_tiktok',
            'data_sources', 'related_queries'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                
                for product in top_products:
                    # Convert lists to strings for CSV
                    row = product.copy()
                    row['data_sources'] = '; '.join(row.get('data_sources', []))
                    row['related_queries'] = '; '.join(row.get('related_queries', [])[:3])  # Top 3 only
                    
                    # Only write columns that exist in our fieldnames
                    filtered_row = {k: v for k, v in row.items() if k in csv_columns}
                    writer.writerow(filtered_row)
            
            logger.info(f"Exported {len(top_products)} products to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return False
    
    def get_summary_stats(self):
        """Get summary statistics of the processed data"""
        if not hasattr(self, 'scored_df'):
            self.calculate_composite_scores()
        
        df = self.scored_df
        
        stats = {
            'total_products': len(df),
            'products_with_trend_data': len(df[df['has_trend_data'] == True]),
            'products_with_ali_data': len(df[df['has_ali_data'] == True]),
            'products_with_amz_data': len(df[df['has_amz_data'] == True]),
            'products_with_tiktok_data': len(df[df['has_tiktok_data'] == True]),
            'avg_composite_score': round(df['composite_score'].mean(), 3),
            'top_score': round(df['composite_score'].max(), 3),
            'products_with_multiple_sources': len(df[
                (df['has_trend_data'].astype(int) + 
                 df['has_ali_data'].astype(int) + 
                 df['has_amz_data'].astype(int) + 
                 df['has_tiktok_data'].astype(int)) >= 2
            ])
        }
        
        return stats

if __name__ == "__main__":
    # Test the normalizer with mock data
    normalizer = ProductNormalizer()
    
    # Mock trend data
    trend_data = [
        {'keyword': 'phone holder', 'momentum': 1.2, 'avg_interest': 45, 'related_queries': ['car phone holder', 'desk phone stand']},
        {'keyword': 'led strip lights', 'momentum': 0.8, 'avg_interest': 62, 'related_queries': ['rgb led strip', 'smart led lights']},
        {'keyword': 'wireless earbuds', 'momentum': -0.3, 'avg_interest': 78, 'related_queries': ['bluetooth earbuds', 'noise cancelling']}
    ]
    
    # Mock AliExpress data
    ali_data = [
        {'name': 'Phone Holder Car Mount', 'orders': 12500, 'reviews': 856, 'rating': 4.3, 'price': 15.99, 'url': 'https://aliexpress.com/item1'},
        {'name': 'LED Strip Lights RGB', 'orders': 8900, 'reviews': 632, 'rating': 4.1, 'price': 22.50, 'url': 'https://aliexpress.com/item2'},
        {'name': 'Wireless Bluetooth Earbuds', 'orders': 25000, 'reviews': 1200, 'rating': 4.5, 'price': 29.99, 'url': 'https://aliexpress.com/item3'}
    ]
    
    # Mock Amazon data
    amz_data = [
        {'name': 'Car Phone Holder Mount', 'reviews': 3400, 'rating': 4.2, 'price': 18.99, 'bsr': 15, 'is_prime': True, 'url': 'https://amazon.com/item1'},
        {'name': 'RGB LED Strip Lights', 'reviews': 2100, 'rating': 4.0, 'price': 25.99, 'bsr': 45, 'is_prime': True, 'url': 'https://amazon.com/item2'},
        {'name': 'Wireless Earbuds Bluetooth', 'reviews': 8500, 'rating': 4.4, 'price': 35.99, 'bsr': 8, 'is_prime': True, 'url': 'https://amazon.com/item3'}
    ]
    
    # Mock TikTok data
    tiktok_data = [
        {'title': 'This phone holder changed my life! #phoneholder #cardrive', 'views': 250000, 'likes': 12000, 'comments': 340, 'shares': 890, 'url': 'https://tiktok.com/video1', 'hashtags': ['phoneholder', 'cardrive']},
        {'title': 'LED lights room transformation #ledlights #roomdecor', 'views': 850000, 'likes': 45000, 'comments': 1200, 'shares': 3400, 'url': 'https://tiktok.com/video2', 'hashtags': ['ledlights', 'roomdecor']},
        {'title': 'Testing wireless earbuds from Amazon #earbuds #tech', 'views': 1200000, 'likes': 67000, 'comments': 2100, 'shares': 5600, 'url': 'https://tiktok.com/video3', 'hashtags': ['earbuds', 'tech']}
    ]
    
    # Add data to normalizer
    normalizer.add_trend_data(trend_data)
    normalizer.add_aliexpress_data(ali_data)
    normalizer.add_amazon_data(amz_data)
    normalizer.add_tiktok_data(tiktok_data)
    
    # Get top products
    top_products = normalizer.get_top_products(5)
    
    print("Top 5 Products:")
    print("=" * 50)
    for i, product in enumerate(top_products, 1):
        print(f"{i}. {product['product_name']}")
        print(f"   Score: {product['score']}")
        print(f"   AliExpress Orders: {product['orders']:,}")
        print(f"   TikTok Views: {product['tiktok_views']}")
        print(f"   Data Sources: {', '.join(product['data_sources'])}")
        print()
    
    # Export to CSV
    success = normalizer.export_to_csv('products_scored.csv', top_n=10)
    if success:
        print("✅ Exported products to products_scored.csv")
    
    # Print summary stats
    stats = normalizer.get_summary_stats()
    print(f"\nSummary Statistics:")
    print(f"Total products: {stats['total_products']}")
    print(f"Products with multiple data sources: {stats['products_with_multiple_sources']}")
    print(f"Average composite score: {stats['avg_composite_score']}")
    print(f"Top score: {stats['top_score']}")