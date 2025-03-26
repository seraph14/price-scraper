from abc import ABC, abstractmethod
from typing import Dict, Optional, Union
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import re
import random
import time
import os

# Define fallback user agents
FALLBACK_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
]

class BaseScraper(ABC):
    def __init__(self, website: str, base_url: str):
        self.website = website
        self.base_url = base_url
        self.driver = None
        try:
            from fake_useragent import UserAgent
            self.user_agent = UserAgent().random
        except:
            self.user_agent = random.choice(FALLBACK_USER_AGENTS)

    async def get_selenium_driver(self):
        """Initialize and return a Selenium WebDriver"""
        if self.driver is None:
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(f"user-agent={self.user_agent}")
                
                # Disable images for faster loading
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
                
                # Simple initialization - let Selenium find the driver
                self.driver = webdriver.Chrome(options=options)
                self.driver.set_page_load_timeout(30)  # 30 second timeout
            except Exception as e:
                print(f"Error initializing Chrome for {self.website}: {str(e)}")
                # Try Firefox as fallback
                try:
                    from selenium import webdriver
                    from selenium.webdriver.firefox.options import Options as FirefoxOptions
                    
                    options = FirefoxOptions()
                    options.add_argument("--headless")
                    
                    self.driver = webdriver.Firefox(options=options)
                    self.driver.set_page_load_timeout(30)
                except Exception as e2:
                    print(f"Firefox fallback also failed: {str(e2)}")
                    raise Exception("Could not initialize any browser driver")
                    
        return self.driver

    async def get_page(self, url: str) -> Optional[str]:
        """Get the page content using Selenium"""
        
        try:
            driver = await self.get_selenium_driver()
            if not driver:
                print("No WebDriver available")
                return None
                
            # Define a function to run in a separate thread
            def fetch_with_selenium():
                try:
                    # Add random delay
                    time.sleep(1 + random.random() * 2)
                    
                    # Clear cookies
                    driver.delete_all_cookies()
                    
                    # Visit page
                    driver.get(url)
                    
                    # Wait for page to load
                    time.sleep(5)  # Static wait for elements to load
                    
                    # Scroll down for lazy-loaded content
                    for _ in range(3):
                        driver.execute_script("window.scrollBy(0, 500)")
                        time.sleep(0.5)
                    
                    # Get page source
                    return driver.page_source
                except Exception as e:
                    print(f"Error in Selenium fetch: {str(e)}")
                    return None
            
            # Execute in a thread pool
            loop = asyncio.get_event_loop()
            page_content = await loop.run_in_executor(None, fetch_with_selenium)
            
            return page_content
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
        return None

    @abstractmethod
    async def search_product(self, product: Dict) -> Dict:
        """Search for a product and return its details"""
        pass

    def format_result(self, product: Dict, title: str, price: Union[str, float, None], price_valid_till: str = "") -> Dict:
        """Format the scraping result"""
        # Handle empty or None price
        if price is None or price == "":
            formatted_price = ""
        else:
            # Try to convert to float if it's a string of digits
            if isinstance(price, str):
                try:
                    formatted_price = float(price)
                except ValueError:
                    formatted_price = price
            else:
                formatted_price = price
                
        return {
            "Website": self.website,
            "Title": title,
            "Price": formatted_price,
            "PriceValidTill": price_valid_till
        }
        
    async def close(self):
        """Close the Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing WebDriver: {str(e)}")
            self.driver = None

    def extract_price_valid_till(self, soup: BeautifulSoup) -> str:
        """Extract price validity date from various common patterns"""
        # Common patterns for price validity
        patterns = [
            # Text patterns
            {'selector': 'span, div', 'text_re': r'offer\s+ends|sale\s+ends|valid\s+until|expires'},
            # Class patterns
            {'selector': '.promotion, .deal-end, .offer-expires, .sale-end-date, .promo-end'},
            # ID patterns
            {'selector': '#offerEnd, #dealExpiry, #saleEnd, #promotionEnd'}
        ]
        
        for pattern in patterns:
            selector = pattern.get('selector', '')
            text_re = pattern.get('text_re', '')
            
            if text_re:
                elements = soup.select(selector)
                for element in elements:
                    if re.search(text_re, element.text, re.IGNORECASE):
                        # Try to extract a date pattern from the text
                        date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{1,2},? \d{4}', element.text)
                        if date_match:
                            return date_match.group()
                        return element.text.strip()
            else:
                element = soup.select_one(selector)
                if element:
                    return element.text.strip()
        
        return "" 