from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import Dict
from urllib.parse import quote_plus

class VisionsScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Visions', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            # Format search query
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/catalogsearch/result?q={quote_plus(search_query)}"
            
            # Get the page content using Selenium
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", None)

            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find all products in search results
            product_items = soup.select('.ais-Hits-item')
            
            if not product_items:
                return self.format_result(product, "", None)

            # Process the first few products
            for product_item in product_items[:5]:
                # Get title
                title_element = product_item.select_one('h3.result-title')
                if not title_element:
                    continue
                title = title_element.text.strip()
                
                # Get price - first try using the meta tag (most reliable)
                price = None
                meta_price = product_item.select_one('meta[itemprop="price"]')
                if meta_price and meta_price.get('content'):
                    try:
                        price = float(meta_price.get('content'))
                    except ValueError:
                        pass
                
                # If meta price failed, try the sale price
                if price is None:
                    price_element = product_item.select_one('.after-special.special-price .price-wrapper')
                    if price_element:
                        price_text = price_element.get('data-price-amount', '') or price_element.text.strip()
                        price_match = re.search(r'[\d,]+\.\d+|\$[\d,]+\.\d+', price_text)
                        if price_match:
                            price_str = price_match.group().replace('$', '').replace(',', '')
                            try:
                                price = float(price_str)
                            except ValueError:
                                pass
                
                # If still no price, try any price element
                if price is None:
                    price_element = product_item.select_one('.price-wrapper')
                    if price_element:
                        price_text = price_element.get('data-price-amount', '') or price_element.text.strip()
                        price_match = re.search(r'[\d,]+\.\d+|\$[\d,]+\.\d+', price_text)
                        if price_match:
                            price_str = price_match.group().replace('$', '').replace(',', '')
                            try:
                                price = float(price_str)
                            except ValueError:
                                pass
                
                if not price:
                    continue
                
                return self.format_result(product, title, price, "")
            
            return self.format_result(product, "", None)
            
        except Exception as e:
            return self.format_result(product, "", None)
