from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import Dict
from urllib.parse import quote_plus

class LondonDrugsScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('LondonDrugs', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            # Format search query
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/search?q={quote_plus(search_query)}"
            print(f"[LondonDrugs] Searching: {search_url}")
            
            # Get the page content using get_page method from BaseScraper
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", None)

            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find all products in search results
            product_items = soup.select('section.product-card')
            print(f"[LondonDrugs] Found {len(product_items)} product items")
            
            if not product_items:
                # Try alternative selectors if the main one doesn't work
                for selector in ['div.grid section', '.product-listing div']:
                    product_items = soup.select(selector)
                    if product_items:
                        print(f"[LondonDrugs] Found {len(product_items)} products with alternate selector: {selector}")
                        break
            
            if not product_items:
                print("[LondonDrugs] No products found on page")
                return self.format_result(product, "", None)

            # Process the first few products
            for product_item in product_items[:5]:
                # Get product title
                title_element = product_item.select_one('h3.product-name')
                if not title_element:
                    title_element = product_item.select_one('.product-name, h3, [class*="title"]')
                
                if not title_element:
                    continue
                    
                title = title_element.text.strip()
                print(f"[LondonDrugs] Found product: {title}")
                
                # Skip if title doesn't match well enough with the search query
                if not self.is_match(product['name'], title):
                    print(f"[LondonDrugs] Title doesn't match search query well enough: {title}")
                    continue
                
                # Get price - try sale price first, then regular price
                price = None
                price_elements = product_item.select('section.product-card-price small, .price, [class*="price"]')
                
                for price_element in price_elements:
                    price_text = price_element.text.strip()
                    price_match = re.search(r'[\d,]+\.\d+', price_text)
                    if price_match:
                        price_str = price_match.group().replace('$', '').replace(',', '')
                        try:
                            price = float(price_str)
                            print(f"[LondonDrugs] Found price: ${price}")
                            break
                        except ValueError:
                            continue
                
                if not price:
                    print("[LondonDrugs] No valid price found")
                    continue
                
                print(f"[LondonDrugs] Returning result: {title}, ${price}")
                return self.format_result(product, title, price, "")
            
            print("[LondonDrugs] No matching products found")
            return self.format_result(product, "", None)
            
        except Exception as e:
            print(f"[LondonDrugs] Error: {str(e)}")
            return self.format_result(product, "", None)

