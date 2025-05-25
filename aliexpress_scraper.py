"""
AliExpress scraper for product data
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
from fake_useragent import UserAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AliExpressScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.base_url = "https://www.aliexpress.com"
        
    def get_headers(self):
        """Get random headers for requests"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def search_products(self, query, max_pages=3):
        """Search for products on AliExpress"""
        products = []
        
        for page in range(1, max_pages + 1):
            try:
                search_url = f"{self.base_url}/wholesale"
                params = {
                    'SearchText': query,
                    'page': page,
                    'g': 'y',
                    'SortType': 'total_tranpro_desc'  # Sort by orders
                }
                
                response = self.session.get(
                    search_url, 
                    params=params, 
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    page_products = self.parse_search_page(response.text, query)
                    products.extend(page_products)
                    logger.info(f"Scraped page {page} for '{query}': {len(page_products)} products")
                else:
                    logger.warning(f"Failed to fetch page {page} for '{query}': {response.status_code}")
                
                # Random delay to avoid rate limiting
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error scraping page {page} for '{query}': {e}")
                continue
        
        return products
    
    def parse_search_page(self, html, query):
        """Parse product data from search results page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find product containers (AliExpress structure changes frequently)
        product_containers = soup.find_all(['div', 'article'], {'data-product-id': True}) or \
                           soup.find_all('div', class_=re.compile(r'item.*product|product.*item', re.I))
        
        if not product_containers:
            # Fallback: look for common product patterns
            product_containers = soup.find_all('div', class_=re.compile(r'list.*item|search.*item', re.I))
        
        for container in product_containers[:20]:  # Limit to top 20 results per page
            try:
                product = self.extract_product_info(container, query)
                if product:
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error parsing product container: {e}")
                continue
        
        # If no structured containers found, try to extract from scripts
        if not products:
            products = self.extract_from_scripts(soup, query)
        
        return products
    
    def extract_product_info(self, container, query):
        """Extract product information from container"""
        try:
            # Product title
            title_elem = container.find(['h1', 'h2', 'h3', 'a'], title=True) or \
                        container.find('a', href=re.compile(r'/item/'))
            title = title_elem.get('title', '') if title_elem else ''
            
            if not title:
                title_elem = container.find(text=re.compile(r'\w+'))
                title = str(title_elem).strip() if title_elem else ''
            
            # Orders count
            orders_text = container.find(text=re.compile(r'\d+.*sold|orders?', re.I))
            orders = self.extract_number(str(orders_text)) if orders_text else 0
            
            # Price
            price_elem = container.find(['span', 'div'], text=re.compile(r'\$[\d.,]+'))
            price = self.extract_price(price_elem.get_text() if price_elem else '')
            
            # Rating
            rating_elem = container.find(['span', 'div'], text=re.compile(r'\d+\.?\d*\s*star', re.I))
            rating = self.extract_rating(rating_elem.get_text() if rating_elem else '')
            
            # Reviews count
            reviews_text = container.find(text=re.compile(r'\d+.*review', re.I))
            reviews = self.extract_number(str(reviews_text)) if reviews_text else 0
            
            # Product URL
            link_elem = container.find('a', href=True)
            product_url = link_elem['href'] if link_elem else ''
            if product_url and not product_url.startswith('http'):
                product_url = self.base_url + product_url
            
            if title and len(title) > 10:  # Valid product found
                return {
                    'name': title.strip()[:100],  # Limit length
                    'orders': orders,
                    'price': price,
                    'rating': rating,
                    'reviews': reviews,
                    'url': product_url,
                    'source': 'aliexpress',
                    'search_query': query
                }
        
        except Exception as e:
            logger.debug(f"Error extracting product info: {e}")
        
        return None
    
    def extract_from_scripts(self, soup, query):
        """Try to extract data from JavaScript objects in page"""
        products = []
        scripts = soup.find_all('script', string=re.compile(r'window\.runParams|__INITIAL_STATE__'))
        
        for script in scripts:
            try:
                script_text = script.string
                # Look for product data patterns
                if 'productId' in script_text and 'title' in script_text:
                    # Try to extract JSON-like structures
                    json_matches = re.findall(r'\{[^{}]*"title"[^{}]*\}', script_text)
                    for match in json_matches[:10]:  # Limit results
                        try:
                            # Clean up the match to make it valid JSON
                            clean_match = re.sub(r'(\w+):', r'"\1":', match)
                            data = json.loads(clean_match)
                            
                            if 'title' in data:
                                product = {
                                    'name': data.get('title', '')[:100],
                                    'orders': self.extract_number(str(data.get('orders', 0))),
                                    'price': self.extract_price(str(data.get('price', ''))),
                                    'rating': self.extract_rating(str(data.get('rating', ''))),
                                    'reviews': self.extract_number(str(data.get('reviews', 0))),
                                    'url': data.get('url', ''),
                                    'source': 'aliexpress',
                                    'search_query': query
                                }
                                products.append(product)
                        except:
                            continue
            except Exception as e:
                logger.debug(f"Error parsing script: {e}")
                continue
        
        return products
    
    def extract_number(self, text):
        """Extract number from text (handles K, M suffixes)"""
        if not text:
            return 0
        
        # Handle formats like "1.2K", "5M", "234"
        match = re.search(r'([\d.,]+)\s*([KMkm]?)', str(text))
        if match:
            number = float(match.group(1).replace(',', ''))
            suffix = match.group(2).upper()
            
            if suffix == 'K':
                return int(number * 1000)
            elif suffix == 'M':
                return int(number * 1000000)
            else:
                return int(number)
        
        return 0
    
    def extract_price(self, text):
        """Extract price from text"""
        if not text:
            return 0.0
        
        match = re.search(r'\$?([\d.,]+)', str(text))
        if match:
            return float(match.group(1).replace(',', ''))
        return 0.0
    
    def extract_rating(self, text):
        """Extract rating from text"""
        if not text:
            return 0.0
        
        match = re.search(r'([\d.]+)', str(text))
        if match:
            rating = float(match.group(1))
            return min(5.0, rating)  # Cap at 5.0
        return 0.0
    
    def calculate_sales_velocity_score(self, product):
        """Calculate normalized sales velocity score"""
        orders = product.get('orders', 0)
        reviews = product.get('reviews', 0)
        rating = product.get('rating', 0)
        
        # Normalize orders (assume 10000+ is excellent)
        orders_score = min(1.0, orders / 10000)
        
        # Reviews indicate ongoing sales
        reviews_score = min(1.0, reviews / 1000)
        
        # Rating quality factor
        rating_factor = rating / 5.0 if rating > 0 else 0.5
        
        # Combined velocity score
        velocity = (orders_score * 0.6 + reviews_score * 0.4) * rating_factor
        return velocity

if __name__ == "__main__":
    # Test scraper
    scraper = AliExpressScraper()
    test_queries = ["phone holder", "led lights"]
    
    for query in test_queries:
        print(f"\nSearching for: {query}")
        products = scraper.search_products(query, max_pages=1)
        
        for product in products[:3]:  # Show top 3
            score = scraper.calculate_sales_velocity_score(product)
            print(f"  {product['name'][:50]}...")
            print(f"  Orders: {product['orders']}, Reviews: {product['reviews']}")
            print(f"  Score: {score:.3f}")