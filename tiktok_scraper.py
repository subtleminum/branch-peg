"""
TikTok scraper for viral product discovery
"""
import time
import re
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.viral_hashtags = [
            "tiktokmademebuyit",
            "amazonfinds", 
            "musthave",
            "viral",
            "productreview",
            "gadgets",
            "shopwithme",
            "trending"
        ]
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Install and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome driver setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def scrape_hashtag(self, hashtag, max_videos=20):
        """Scrape videos from a specific hashtag"""
        if not self.driver:
            if not self.setup_driver():
                return []
        
        videos = []
        
        try:
            # Navigate to hashtag page
            hashtag_url = f"https://www.tiktok.com/tag/{hashtag}"
            self.driver.get(hashtag_url)
            
            # Wait for page load
            time.sleep(random.uniform(3, 5))
            
            # Scroll and collect video data
            videos = self.scroll_and_extract_videos(max_videos, hashtag)
            
            logger.info(f"Scraped {len(videos)} videos from #{hashtag}")
            
        except Exception as e:
            logger.error(f"Error scraping hashtag #{hashtag}: {e}")
        
        return videos
    
    def search_products(self, query, max_videos=15):
        """Search for product-related videos"""
        if not self.driver:
            if not self.setup_driver():
                return []
        
        videos = []
        
        try:
            # Navigate to search page
            search_url = f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}"
            self.driver.get(search_url)
            
            # Wait for results to load
            time.sleep(random.uniform(3, 5))
            
            # Extract video data
            videos = self.scroll_and_extract_videos(max_videos, query)
            
            logger.info(f"Found {len(videos)} videos for query: {query}")
            
        except Exception as e:
            logger.error(f"Error searching for {query}: {e}")
        
        return videos
    
    def scroll_and_extract_videos(self, max_videos, source):
        """Scroll page and extract video data"""
        videos = []
        last_height = 0
        scroll_attempts = 0
        max_scrolls = 10
        
        while len(videos) < max_videos and scroll_attempts < max_scrolls:
            try:
                # Extract current videos on page
                current_videos = self.extract_video_elements()
                
                for video_elem in current_videos:
                    if len(videos) >= max_videos:
                        break
                    
                    video_data = self.extract_video_data(video_elem, source)
                    if video_data and video_data not in videos:
                        videos.append(video_data)
                
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                    
                last_height = new_height
                
            except Exception as e:
                logger.debug(f"Error during scroll: {e}")
                scroll_attempts += 1
        
        return videos
    
    def extract_video_elements(self):
        """Extract video elements from current page"""
        try:
            # Try different selectors for video containers
            selectors = [
                '[data-e2e="recommend-list-item"]',
                '[data-e2e="search-card-item"]',
                'div[class*="DivItemContainer"]',
                'div[class*="video-feed-item"]'
            ]
            
            video_elements = []
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    video_elements = elements
                    break
            
            return video_elements[:50]  # Limit to avoid memory issues
            
        except Exception as e:
            logger.debug(f"Error extracting video elements: {e}")
            return []
    
    def extract_video_data(self, element, source):
        """Extract data from a single video element"""
        try:
            video_data = {
                'source_query': source,
                'url': '',
                'title': '',
                'author': '',
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'hashtags': [],
                'product_mentions': []
            }
            
            # Extract video URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, 'a[href*="/video/"]')
                video_data['url'] = link_elem.get_attribute('href')
            except:
                pass
            
            # Extract title/description
            try:
                title_selectors = [
                    '[data-e2e="browse-video-desc"]',
                    'div[class*="video-meta-caption"]',
                    'span[class*="SpanText"]'
                ]
                
                for selector in title_selectors:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, selector)
                        video_data['title'] = title_elem.text.strip()
                        break
                    except:
                        continue
            except:
                pass
            
            # Extract author
            try:
                author_selectors = [
                    '[data-e2e="browse-username"]',
                    'span[class*="author-uniqueId"]',
                    'p[class*="author-uniqueId"]'
                ]
                
                for selector in author_selectors:
                    try:
                        author_elem = element.find_element(By.CSS_SELECTOR, selector)
                        video_data['author'] = author_elem.text.strip().replace('@', '')
                        break
                    except:
                        continue
            except:
                pass
            
            # Extract engagement metrics
            engagement_data = self.extract_engagement_metrics(element)
            video_data.update(engagement_data)
            
            # Extract hashtags from title
            if video_data['title']:
                hashtags = re.findall(r'#(\w+)', video_data['title'])
                video_data['hashtags'] = hashtags
            
            # Identify potential product mentions
            video_data['product_mentions'] = self.identify_product_mentions(video_data['title'])
            
            # Only return if we have meaningful data
            if video_data['title'] or video_data['url']:
                return video_data
                
        except Exception as e:
            logger.debug(f"Error extracting video data: {e}")
        
        return None
    
    def extract_engagement_metrics(self, element):
        """Extract likes, comments, shares, views from video element"""
        metrics = {'views': 0, 'likes': 0, 'comments': 0, 'shares': 0}
        
        try:
            # Try to find engagement buttons/counts
            metric_selectors = {
                'likes': ['[data-e2e="browse-like-count"]', '[data-e2e="like-count"]'],
                'comments': ['[data-e2e="browse-comment-count"]', '[data-e2e="comment-count"]'],
                'shares': ['[data-e2e="browse-share-count"]', '[data-e2e="share-count"]'],
                'views': ['[data-e2e="video-views"]', 'strong[class*="video-count"]']
            }
            
            for metric, selectors in metric_selectors.items():
                for selector in selectors:
                    try:
                        elem = element.find_element(By.CSS_SELECTOR, selector)
                        count_text = elem.text.strip()
                        metrics[metric] = self.parse_count(count_text)
                        break
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Error extracting engagement metrics: {e}")
        
        return metrics
    
    def parse_count(self, count_text):
        """Parse count text like '1.2M', '500K', '1234' to integer"""
        if not count_text:
            return 0
        
        # Remove any non-numeric characters except K, M, B, .
        clean_text = re.sub(r'[^\d.KMB]', '', count_text.upper())
        
        if not clean_text:
            return 0
        
        try:
            if 'B' in clean_text:
                number = float(clean_text.replace('B', '')) * 1000000000
            elif 'M' in clean_text:
                number = float(clean_text.replace('M', '')) * 1000000
            elif 'K' in clean_text:
                number = float(clean_text.replace('K', '')) * 1000
            else:
                number = float(clean_text)
            
            return int(number)
        except:
            return 0
    
    def identify_product_mentions(self, text):
        """Identify potential product mentions in video text"""
        if not text:
            return []
        
        # Common product keywords
        product_keywords = [
            'buy', 'purchase', 'order', 'shop', 'link', 'amazon', 'store',
            'product', 'item', 'gadget', 'tool', 'device', 'accessory',
            'must have', 'game changer', 'life hack', 'viral', 'trending'
        ]
        
        mentions = []
        text_lower = text.lower()
        
        for keyword in product_keywords:
            if keyword in text_lower:
                mentions.append(keyword)
        
        return mentions
    
    def calculate_virality_score(self, video):
        """Calculate normalized virality score"""
        views = video.get('views', 0)
        likes = video.get('likes', 0)
        comments = video.get('comments', 0)
        shares = video.get('shares', 0)
        
        # Engagement rate calculation
        total_engagement = likes + comments + (shares * 2)  # Weight shares more
        engagement_rate = total_engagement / max(views, 1)
        
        # Normalize views (1M+ views = highly viral)
        views_score = min(1.0, views / 1000000)
        
        # Normalize engagement rate (10% = excellent)
        engagement_score = min(1.0, engagement_rate / 0.1)
        
        # Product mention bonus
        product_bonus = 0.2 if len(video.get('product_mentions', [])) > 2 else 0
        
        # Combined virality score
        virality = (views_score * 0.6 + engagement_score * 0.4) + product_bonus
        return min(1.0, virality)
    
    def scrape_viral_products(self, max_videos_per_hashtag=10):
        """Scrape viral products from multiple hashtags"""
        all_videos = []
        
        for hashtag in self.viral_hashtags:
            try:
                logger.info(f"Scraping hashtag: #{hashtag}")
                videos = self.scrape_hashtag(hashtag, max_videos_per_hashtag)
                all_videos.extend(videos)
                
                # Small delay between hashtags
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error scraping hashtag #{hashtag}: {e}")
                continue
        
        return all_videos
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser driver closed")
            except:
                pass

if __name__ == "__main__":
    # Test TikTok scraper
    scraper = TikTokScraper(headless=True)
    
    try:
        # Test search functionality
        print("Testing TikTok search...")
        videos = scraper.search_products("phone accessories", max_videos=5)
        
        for video in videos:
            if video:
                virality = scraper.calculate_virality_score(video)
                print(f"\nTitle: {video['title'][:60]}...")
                print(f"Author: @{video['author']}")
                print(f"Views: {video['views']:,}, Likes: {video['likes']:,}")
                print(f"Virality Score: {virality:.3f}")
                print(f"Product mentions: {video['product_mentions']}")
        
        # Test hashtag scraping
        print("\nTesting hashtag scraping...")
        hashtag_videos = scraper.scrape_hashtag("amazonfinds", max_videos=3)
        
        for video in hashtag_videos:
            if video:
                print(f"\nHashtag video: {video['title'][:50]}...")
                print(f"Engagement: {video['likes']} likes, {video['comments']} comments")
    
    finally:
        scraper.close()