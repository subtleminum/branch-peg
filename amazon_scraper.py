"""
Amazon scraper for bestseller and product data
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from fake_useragent import UserAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AmazonScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.base_url = "https://www.amazon.com"
        
        # Common Amazon categories for dropshipping
        self.categories = {
            'electronics': 'zgbs_electronics',
            'home_kitchen': 'zgbs_home-garden',
            'sports': 'zgbs_sporting-goods',
            'beauty': 'zgbs_beauty',
            'automotive': 'zgbs_automotive',
            'tools': 'zgbs_hi'
        }
    
    def get_headers(self):
        """Get headers that work with Amazon"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def scrape_bestsellers(self, category='electronics', max_products=50):
        """Scrape Amazon bestsellers from a category"""
        products = []
        
        try:
            category_id = self.categories.get(category, 'zgbs_electronics')
            url = f"{self.base_url}/gp/bestsellers/{category_id}"
            
            response = self.session.get(url, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                products = self.parse_bestsellers_page(response.text, category)
                logger.info(f"Scraped {len(products)} products from {category} bestsellers")
            else:
                logger.warning(f"Failed to fetch bestsellers for {category}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error scraping bestsellers for {category}: {e}")
        
        return products[:max_products]
    
    def search_products(self, query, max_pages=2):
        """Search for specific products"""
        products = []
        
        for page in range(1, max_pages + 1):
            try:
                search_url = f"{self.base_url}/s"
                params = {
                    'k': query,
                    'page': page,
                    'ref': 'sr_pg_' + str(page)
                }
                
                response = self.session.get(
                    search_url, 
                    params=params, 
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    page_products = self.parse_search_results(response.text, query)
                    products.extend(page_products)
                    logger.info(f"Scraped page {page} for '{query}': {len(page_products)} products")
                else:
                    logger.warning(f"Failed to fetch page {page} for '{query}': {response.status_code}")
                
                time.sleep(random.uniform(2, 4))  # Amazon requires longer delays
                
            except Exception as e:
                logger.error(f"Error scraping page {page} for '{query}': {e}")
                continue
        
        return products
    
    def parse_bestsellers_page(self, html, category):
        """Parse bestsellers page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product containers in bestsellers
        containers = soup.find_all('div', {'id': re.compile(r'gridItemRoot')}) or \
                    soup.find_all('div', class_=re.compile(r'zg-item-immersion')) or \
                    soup.find_all('div', class_=re.compile(r'p13n-sc-uncoverable-faceout'))
        
        for i, container in enumerate(containers[:50], 1):
            try:
                product = self.extract_product_from_container(container, category)
                if product:
                    product['bsr'] = i  # Best seller rank
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error parsing bestseller container: {e}")
                continue
        
        return products
    
    def parse_search_results(self, html, query):
        """Parse search results page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product containers in search results
        containers = soup.find_all('div', {'data-component-type': 's-search-result'}) or \
                    soup.find_all('div', class_=re.compile(r's-result-item')) or \
                    soup.find_all('div', {'data-asin': True})
        
        for container in containers:
            try:
                product = self.extract_product_from_container(container, query)
                if product:
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error parsing search container: {e}")
                continue
        
        return products
    
    def extract_product_from_container(self, container, source):
        """Extract product data from container"""
        try:
            # Product title
            title_elem = container.find('h2', class_=re.compile(r's-size.*text')) or \
                        container.find('span', class_=re.compile(r'zg-text-center-align')) or \
                        container.find('a', {'href': re.compile(r'/dp/')})
            
            title = ''
            if title_elem:
                title = title_elem.get_text(strip=True)
                if not title and title_elem.find('span'):
                    title = title_elem.find('span').get_text(strip=True)
            
            # Product URL and ASIN
            link_elem = container.find('a', href=re.compile(r'/dp/'))
            product_url = ''
            asin = ''
            
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    product_url = self.base_url + href
                else:
                    product_url = href
                
                # Extract ASIN from URL
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                if asin_match:
                    asin = asin_match.group(1)
            
            # Price
            price_elem = container.find('span', class_=re.compile(r'price.*offscreen')) or \
                        container.find('span', class_=re.compile(r'a-price-whole'))
            price = 0.0
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self.extract_price(price_text)
            
            # Rating
            rating_elem = container.find('span', class_=re.compile(r'a-icon-alt')) or \
                         container.find('span', {'aria-label': re.compile(r'\d+\.?\d* out of')})
            rating = 0.0
            
            if rating_elem:
                rating_text = rating_elem.get('aria-label', '') or rating_elem.get_text()
                rating = self.extract_rating(rating_text)
            
            # Reviews count
            reviews_elem = container.find('a', href=re.compile(r'#customerReviews')) or \
                          container.find('span', {'aria-label': re.compile(r'\d+.*reviews?', re.I)})
            reviews = 0
            
            if reviews_elem:
                reviews_text = reviews_elem.get('aria-label', '') or reviews_elem.get_text()
                reviews = self.extract_number(reviews_text)
            
            # Prime eligibility
            prime_elem = container.find('span', {'aria-label': 'Amazon Prime'})
            is_prime = prime_elem is not None
            
            if title and len(title) > 5:
                return {
                    'name': title.strip()[:150],
                    'price': price,
                    'rating': rating,
                    'reviews': reviews,
                    'url': product_url,
                    'asin': asin,
                    'is_prime': is_prime,
                    'source': 'amazon',
                    'category': source,
                    'bsr': 0  # Will be set by caller for bestsellers
                }
        
        except Exception as e:
            logger.debug(f"Error extracting Amazon product: {e}")
        
        return None
    
    def extract_price(self, text):
        """Extract price from text"""
        if not text:
            return 0.0
        
        # Remove currency symbols and extract number
        price_match = re.search(r'[\$]?([\d,]+\.?\d*)', text.replace(',', ''))
        if price_match:
            return float(price_match.group(1))
        return 0.0
    
    def extract_rating(self, text):
        """Extract rating from text"""
        if not text:
            return 0.0
        
        # Look for "X.X out of 5" or just "X.X"
        rating_match = re.search(r'(\d+\.?\d*)', text)
        if rating_match:
            rating = float(rating_match.group(1))
            return min(5.0, rating)
        return 0.0
    
    def extract_number(self, text):
        """Extract number from text (handles commas and K/M)"""
        if not text:
            return 0
        
        # Remove commas and extract number
        number_match = re.search(r'([\d,]+)', text.replace(',', ''))
        if number_match:
            return int(number_match.group(1))
        return 0
    
    def calculate_popularity_score(self, product):
        """Calculate normalized popularity score"""
        reviews = product.get('reviews', 0)
        rating = product.get('rating', 0)
        bsr = product.get('bsr', 999)  # Best seller rank (lower is better)
        is_prime = product.get('is_prime', False)
        
        # Normalize reviews (10000+ reviews = high popularity)
        reviews_score = min(1.0, reviews / 10000)
        
        # Rating score
        rating_score = rating / 5.0 if rating > 0 else 0
        
        # BSR score (lower rank = higher score)
        bsr_score = max(0, 1 - (bsr / 100)) if bsr < 100 else 0
        
        # Prime bonus
        prime_bonus = 0.1 if is_prime else 0
        
        # Combined popularity score
        popularity = (reviews_score * 0.4 + rating_score * 0.3 + bsr_score * 0.3) + prime_bonus
        return min(1.0, popularity)
    
    def get_saturation_indicator(self, product):
        """Higher reviews/ratings might indicate market saturation"""
        reviews = product.get('reviews', 0)
        
        # Very high review counts might indicate saturated market
        if reviews > 50000:
            return 0.9  # High saturation
        elif reviews > 10000:
            return 0.6  # Medium saturation
        elif reviews > 1000:
            return 0.3  # Low saturation
        else:
            return 0.1  # Very low saturation
        
if __name__ == "__main__":
    # Test scraper
    scraper = AmazonScraper()
    
    # Test bestsellers
    print("Testing bestsellers scraping...")
    bestsellers = scraper.scrape_bestsellers('electronics', max_products=5)
    
    for product in bestsellers:
        popularity = scraper.calculate_popularity_score(product)
        saturation = scraper.get_saturation_indicator(product)
        print(f"\n{product['name'][:50]}...")
        print(f"BSR: #{product['bsr']}, Reviews: {product['reviews']}")
        print(f"Popularity: {popularity:.3f}, Saturation: {saturation:.3f}")
    
    # Test search
    print("\nTesting search...")
    search_results = scraper.search_products("phone holder", max_pages=1)
    
    for product in search_results[:3]:
        popularity = scraper.calculate_popularity_score(product)
        print(f"\n{product['name'][:50]}...")
        print(f"Price: ${product['price']}, Reviews: {product['reviews']}")
        print(f"Popularity: {popularity:.3f}")