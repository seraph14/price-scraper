from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import Dict
from urllib.parse import quote_plus
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SamsungScraper(BaseScraper):
    def __init__(self, base_url: str = None):
        super().__init__('Samsung', base_url)
    
    async def get_page_with_consent(self, url):
        """Get page content and handle cookie consent"""
        try:
            # Access the driver through base_scraper's get_driver method
            driver = await self.get_selenium_driver()
                
            # Load the URL
            driver.get(url)
            
            # Wait for initial page load
            await asyncio.sleep(5)
            
            # Handle cookie consent dialog if it appears
            try:
                # Check if the consent dialog is present
                consent_dialog = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "truste-consent-track"))
                )
                
                if consent_dialog.is_displayed():
                    print("[Samsung] Cookie consent dialog found, accepting...")
                    # Try to find and click the "Accept All" button
                    accept_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "truste-consent-button"))
                    )
                    accept_button.click()
                    # Wait for the dialog to disappear
                    await asyncio.sleep(3)
            except (TimeoutException, NoSuchElementException) as e:
                print(f"[Samsung] No cookie consent dialog found or error handling it: {str(e)}")
            
            # Wait for the page to load fully after handling consent
            await asyncio.sleep(5)
            
            # Get the page content
            page_content = driver.page_source
            return page_content
            
        except Exception as e:
            print(f"[Samsung] Error getting page with consent handling: {str(e)}")
            return None

    async def search_product(self, product: Dict) -> Dict:
        try:
            # Format search query
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/ca/search/?searchvalue={quote_plus(search_query)}"
            
            print(f"[Samsung] Searching URL: {search_url}")
            
            # Get page with custom method that handles consent
            page_content = await self.get_page_with_consent(search_url)
            
            if not page_content:
                print("[Samsung] No page content returned")
                return self.format_result(product, "", None)
            
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Look for Samsung search results
            product_items = soup.select('.aisearch__item')
            print(f"[Samsung] Found {len(product_items)} products in search results")
            
            if not product_items:
                print("[Samsung] No products found in search results")
                return self.format_result(product, "", None)

            # Process the found products
            for product_item in product_items[:5]:
                try:
                    # Extract product name
                    name_element = product_item.select_one('.aisearch-product__name')
                    if not name_element:
                        continue
                    title = name_element.text.strip()
                    print(f"[Samsung] Found product: {title}")
                    
                    # Extract price
                    price = None
                    price_element = product_item.select_one('.aisearch-product__price-save')
                    if price_element:
                        price_text = price_element.text.strip()
                        price_match = re.search(r'\$?[\d,]+\.\d+', price_text)
                        if price_match:
                            price_str = price_match.group().replace('$', '').replace(',', '')
                            try:
                                price = float(price_str)
                                print(f"[Samsung] Found price: ${price}")
                            except ValueError:
                                pass
                    
                    if not price:
                        print(f"[Samsung] No price found for: {title}")
                        continue
                    
                    print(f"[Samsung] Returning result: {title}, ${price}")
                    return self.format_result(product, title, price, "")
                    
                except Exception as e:
                    print(f"[Samsung] Error processing product: {str(e)}")
                    continue
            
            print("[Samsung] No valid products found after processing")
            return self.format_result(product, "", None)

        except Exception as e:
            print(f"[Samsung] Error: {str(e)}")
            return self.format_result(product, "", None) 