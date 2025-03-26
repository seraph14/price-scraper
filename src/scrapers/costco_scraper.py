from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import Dict

class CostcoScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Costco', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            # Format search query
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/s?dept=All&keyword={'%20'.join(search_query.split())}"
            
            print(f"Searching Costco: {search_url}")
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", None)

            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find first product result using Costco's specific structure
            product_div = soup.select_one('div[data-testid^="ProductTile_"]')
            
            if not product_div:
                return self.format_result(product, "", None)
                
            # Extract title - using specific data-testid attribute
            title_element = product_div.select_one('h3[data-testid^="Text_ProductTile_"]')
            title = title_element.text.strip() if title_element else ""
            
            # Extract price - using specific price element with data-testid
            price_element = product_div.select_one('div[data-testid^="Text_Price_"]')
            price = None
            if price_element:
                price_text = price_element.text.strip()
                price_match = re.search(r'[\d,]+\.\d+', price_text)
                if price_match:
                    price = float(price_match.group().replace(',', ''))
            
            print(f"Costco result: {title}, {price}")
            return self.format_result(product, title, price, "")

        except Exception as e:
            print(f"Error scraping Costco: {str(e)}")
            return self.format_result(product, "", None)
