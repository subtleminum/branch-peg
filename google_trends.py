"""
Google Trends analyzer for product keywords
"""
import time
import pandas as pd
import numpy as np
from pytrends.request import TrendReq
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleTrendsAnalyzer:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    def get_trend_data(self, keyword, timeframe='today 1-m'):
        """Get trend data for a specific keyword"""
        try:
            self.pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
            data = self.pytrends.interest_over_time()
            
            if data.empty:
                return None
                
            # Calculate trend momentum (slope of last 7 days)
            values = data[keyword].values
            if len(values) < 7:
                momentum = 0
            else:
                recent_values = values[-7:]
                x = np.arange(len(recent_values))
                momentum = np.polyfit(x, recent_values, 1)[0]  # Linear regression slope
            
            # Get related queries
            related_queries = self.get_related_queries(keyword)
            
            return {
                'keyword': keyword,
                'trend_data': values.tolist(),
                'momentum': momentum,
                'avg_interest': np.mean(values),
                'max_interest': np.max(values),
                'related_queries': related_queries
            }
            
        except Exception as e:
            logger.error(f"Error getting trends for {keyword}: {e}")
            return None
    
    def get_related_queries(self, keyword):
        """Get related queries for a keyword"""
        try:
            related = self.pytrends.related_queries()
            if keyword in related and related[keyword]['top'] is not None:
                return related[keyword]['top']['query'].head(5).tolist()
            return []
        except:
            return []
    
    def analyze_multiple_keywords(self, keywords, delay=1):
        """Analyze multiple keywords with rate limiting"""
        results = []
        
        for keyword in keywords:
            logger.info(f"Analyzing trends for: {keyword}")
            result = self.get_trend_data(keyword)
            if result:
                results.append(result)
            time.sleep(delay)  # Rate limiting
            
        return results
    
    def calculate_trend_score(self, trend_data):
        """Calculate normalized trend score (0-1)"""
        if not trend_data:
            return 0
        
        momentum = trend_data.get('momentum', 0)
        avg_interest = trend_data.get('avg_interest', 0)
        
        # Normalize momentum (-5 to +5 range typical)
        momentum_score = max(0, min(1, (momentum + 5) / 10))
        
        # Normalize interest (0-100 range)
        interest_score = avg_interest / 100
        
        # Combined score weighted towards momentum
        score = (momentum_score * 0.7) + (interest_score * 0.3)
        return score

if __name__ == "__main__":
    # Test with sample products
    analyzer = GoogleTrendsAnalyzer()
    test_keywords = ["electric lint remover", "phone grip holder", "led strip lights"]
    
    results = analyzer.analyze_multiple_keywords(test_keywords)
    
    for result in results:
        score = analyzer.calculate_trend_score(result)
        print(f"\nProduct: {result['keyword']}")
        print(f"Momentum: {result['momentum']:.3f}")
        print(f"Avg Interest: {result['avg_interest']:.1f}")
        print(f"Trend Score: {score:.3f}")
        print(f"Related: {result['related_queries'][:3]}")