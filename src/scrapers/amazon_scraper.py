from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import Dict
from urllib.parse import quote_plus

class AmazonScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Amazon', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            # Format search query
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/s?k={quote_plus(search_query)}"
            
            # Get the page content using Selenium
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", None)

            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Check for products using multiple possible selectors
            product_divs = []
            for selector in ['[data-component-type="s-search-result"]', '.s-result-item', '.sg-col-inner']:
                product_divs = soup.select(selector)
                if product_divs:
                    break
            
            if not product_divs:
                return self.format_result(product, "", None)

            # Process the first valid product
            for product_div in product_divs[:5]:  # Check first 5 results
                # Skip sponsored products
                sponsored = product_div.select_one('.s-sponsored-label-info-icon')
                if sponsored:
                    continue
                    
                # Get title - try multiple selectors
                title = ""
                for title_selector in ['h2 .a-link-normal', '.a-text-normal', '.a-size-base-plus']:
                    title_element = product_div.select_one(title_selector)
                    if title_element:
                        title = title_element.text.strip()
                        if title:
                            break
                
                if not title:
                    continue
                
                # Get price - try multiple selectors
                price = None
                for price_selector in ['.a-price .a-offscreen', '.a-price', '.a-color-price']:
                    price_element = product_div.select_one(price_selector)
                    if price_element:
                        price_text = price_element.text.strip()
                        price_match = re.search(r'[\d,]+\.\d+|\$[\d,]+\.\d+', price_text)
                        if price_match:
                            price_str = price_match.group().replace('$', '').replace(',', '')
                            try:
                                price = float(price_str)
                                break
                            except ValueError:
                                pass
                
                if not price:
                    continue
                
                return self.format_result(product, title, price, "")
                
            # If we got here, we didn't find a suitable product
            return self.format_result(product, "", None)

        except Exception as e:
            print(f"Error scraping Amazon: {str(e)}")
            return self.format_result(product, "", None) 