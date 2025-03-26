from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import Dict
from urllib.parse import quote_plus

class BestBuyScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('BestBuy', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            # Format search query
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/en-ca/search?search={quote_plus(search_query)}"
            print(f"[BestBuy] Searching: {search_url}")
            
            # Get the page content using get_page method from BaseScraper
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", None)

            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find all products in search results
            product_items = soup.select('li.productLine_2N9kG')
            print(f"[BestBuy] Found {len(product_items)} product items")
            
            if not product_items:
                # Try alternative selectors if the main one doesn't work
                for selector in ['div[role="region"] li', '.productList li']:
                    product_items = soup.select(selector)
                    if product_items:
                        print(f"[BestBuy] Found {len(product_items)} products with alternate selector: {selector}")
                        break
            
            if not product_items:
                print("[BestBuy] No products found on page")
                return self.format_result(product, "", None)

            # Process the first few products
            for product_item in product_items[:5]:
                # Get product title
                title_element = product_item.select_one('h3.productItemName_3IZ3c')
                if not title_element:
                    title_element = product_item.select_one('[itemprop="name"]')
                
                if not title_element:
                    continue
                    
                title = title_element.text.strip()
                print(f"[BestBuy] Found product: {title}")
                
                # Skip if title doesn't match well enough with the search query
                if not self.is_match(product['name'], title):
                    print(f"[BestBuy] Title doesn't match search query well enough: {title}")
                    continue
                
                # Get price
                price = None
                price_element = product_item.select_one('div[data-automation="product-price"]')
                
                if price_element:
                    price_text = price_element.text.strip()
                    price_match = re.search(r'[\d,]+\.\d+', price_text)
                    if price_match:
                        price_str = price_match.group().replace('$', '').replace(',', '')
                        try:
                            price = float(price_str)
                            print(f"[BestBuy] Found price: ${price}")
                        except ValueError:
                            pass
                
                if not price:
                    print("[BestBuy] No valid price found")
                    continue
                
                
                return self.format_result(product, title, price, "")
            
            return self.format_result(product, "", None)
            
        except Exception as e:
            return self.format_result(product, "", None) 