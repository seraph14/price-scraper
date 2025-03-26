from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import Dict
import time
from urllib.parse import quote_plus
import asyncio

class StaplesScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Staples', base_url)


    async def search_product(self, product: Dict) -> Dict:
        """Search for a product on Staples and return the first result"""
        try:
            search_url = f"{self.base_url}/search?query={quote_plus(product['name'])}"
            print(f"Searching Staples: {search_url}")
            
            # Get the page content using Selenium
            page_content = await self.get_page(search_url)
            if not page_content:
                print("Failed to retrieve Staples search page")
                return self.format_result(product, "", None)
            
            # Parse the HTML content
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find the first product in the search results
            product_div = soup.select_one('.product-thumbnail.h-100.ais-hit')
            
            if not product_div:
                print("No product found on Staples")
                return self.format_result(product, "", None)

            # Extract title
            title_element = product_div.select_one('.product-thumbnail__title.product-link')
            title = title_element.text.strip() if title_element else ""

            # Extract price
            price_element = product_div.select_one('.money.pre-money')
            price = None
            if price_element:
                price_text = price_element.text.strip()
                price_match = re.search(r'[\d,]+\.\d+', price_text)
                if price_match:
                    price = float(price_match.group().replace(',', ''))
            
            print(f"Staples result: {title}, {price}")
            return self.format_result(product, title, price, "")

        except Exception as e:
            print(f"Error scraping Staples: {str(e)}")
            return self.format_result(product, "", None) 