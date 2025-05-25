"""
Amazon scraper focusing on search results with retry/backoff and simplified headers
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AmazonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.amazon.com"
        self.max_retries = 5

    def get_headers(self):
        """Simplified headers to mimic a real browser minimally"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                          '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': self.base_url,
        }

    def fetch_with_retries(self, url, params=None):
        """Fetch a URL with retries on 429 status with exponential backoff"""
        delay = 10
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Requesting URL: {url} (Attempt {attempt})")
                response = self.session.get(url, headers=self.get_headers(), params=params, timeout=15)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:
                    logger.warning(f"Received 429 Too Many Requests. Backing off for {delay} seconds.")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.warning(f"Unexpected status code {response.status_code} on attempt {attempt}")
                    break
            except requests.RequestException as e:
                logger.error(f"Request exception on attempt {attempt}: {e}")
                time.sleep(delay)
                delay *= 2
        return None

    def search_products(self, query, max_pages=1):
        """Search Amazon for products with retries and delays"""
        products = []

        for page in range(1, max_pages + 1):
            params = {
                'k': query,
                'page': page,
                'ref': f'sr_pg_{page}'
            }
            html = self.fetch_with_retries(f"{self.base_url}/s", params=params)
            if not html:
                logger.warning(f"Failed to retrieve search page {page} for query '{query}'. Stopping.")
                break
            
            products_on_page = self.parse_search_results(html)
            logger.info(f"Scraped {len(products_on_page)} products from page {page}")
            products.extend(products_on_page)

            # Delay 10-15 seconds before next request
            time.sleep(random.uniform(10, 15))

        return products

    def parse_search_results(self, html):
        """Parse search results from HTML"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        containers = soup.find_all('div', {'data-component-type': 's-search-result'})

        for container in containers:
            product = self.extract_product_from_container(container)
            if product:
                products.append(product)

        return products

    def extract_product_from_container(self, container):
        """Extract product info from container"""
        try:
            title_elem = container.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else ''

            link_elem = container.find('a', href=re.compile(r'/dp/'))
            url = ''
            asin = ''
            if link_elem:
                href = link_elem.get('href')
                url = self.base_url + href if href.startswith('/') else href
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                if asin_match:
                    asin = asin_match.group(1)

            price_whole = container.find('span', class_='a-price-whole')
            price_fraction = container.find('span', class_='a-price-fraction')
            price = 0.0
            if price_whole:
                price_text = price_whole.get_text(strip=True)
                if price_fraction:
                    price_text += '.' + price_fraction.get_text(strip=True)
                price = self.extract_price(price_text)

            rating_elem = container.find('span', class_='a-icon-alt')
            rating = 0.0
            if rating_elem:
                rating = self.extract_rating(rating_elem.get_text(strip=True))

            reviews_elem = container.find('span', {'aria-label': re.compile(r'\d+.*reviews?', re.I)})
            reviews = 0
            if reviews_elem:
                reviews = self.extract_number(reviews_elem.get('aria-label', '')) or \
                          self.extract_number(reviews_elem.get_text())

            prime = container.find('i', {'aria-label': 'Amazon Prime'}) is not None

            if title and asin:
                return {
                    'name': title[:150],
                    'price': price,
                    'rating': rating,
                    'reviews': reviews,
                    'url': url,
                    'asin': asin,
                    'is_prime': prime,
                    'source': 'amazon'
                }

        except Exception as e:
            logger.debug(f"Error extracting product: {e}")
        return None

    def extract_price(self, text):
        try:
            cleaned = text.replace(',', '').replace('$', '').strip()
            return float(cleaned)
        except Exception:
            return 0.0

    def extract_rating(self, text):
        try:
            match = re.search(r'(\d+\.?\d*)', text)
            return float(match.group(1)) if match else 0.0
        except Exception:
            return 0.0

    def extract_number(self, text):
        try:
            text = text.lower().replace(',', '').strip()
            if 'k' in text:
                return int(float(text.replace('k', '')) * 1000)
            elif 'm' in text:
                return int(float(text.replace('m', '')) * 1000000)
            else:
                return int(re.search(r'\d+', text).group())
        except Exception:
            return 0

if __name__ == '__main__':
    scraper = AmazonScraper()
    print("Searching for 'phone holder' products on Amazon.com ...")
    results = scraper.search_products('phone holder', max_pages=1)
    for product in results[:10]:
        print(product)
