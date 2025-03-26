class CostcoScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Costco', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/en-ca/search?q={'%20'.join(search_query.split())}"
            
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", "", "")

            soup = BeautifulSoup(page_content, 'html.parser')
            
            product_div = soup.find('div', {'class': 'product-tile-set'})
            if not product_div:
                return self.format_result(product, "", "", "")

            title_element = product_div.find('span', {'class': 'description'})
            title = title_element.text.strip() if title_element else ""

            price_element = product_div.find('div', {'class': 'price'})
            price = ''
            if price_element:
                price_text = price_element.text.strip()
                price = ''.join(filter(str.isdigit, price_text))

            return self.format_result(product, title, price)

        except Exception as e:
            print(f"Error scraping Costco: {str(e)}")
            return self.format_result(product, "", "", "")

class StaplesScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Staples', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/search?query={'%20'.join(search_query.split())}"
            
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", "", "")

            soup = BeautifulSoup(page_content, 'html.parser')
            
            product_div = soup.find('div', {'class': 'product-tile'})
            if not product_div:
                return self.format_result(product, "", "", "")

            title_element = product_div.find('a', {'class': 'product-title'})
            title = title_element.text.strip() if title_element else ""

            price_element = product_div.find('span', {'class': 'current-price'})
            price = ''
            if price_element:
                price_text = price_element.text.strip()
                price = ''.join(filter(str.isdigit, price_text))

            return self.format_result(product, title, price)

        except Exception as e:
            print(f"Error scraping Staples: {str(e)}")
            return self.format_result(product, "", "", "")

class VisionsScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Visions', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/search/{'%20'.join(search_query.split())}"
            
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", "", "")

            soup = BeautifulSoup(page_content, 'html.parser')
            
            product_div = soup.find('div', {'class': 'product-item'})
            if not product_div:
                return self.format_result(product, "", "", "")

            title_element = product_div.find('h2', {'class': 'product-name'})
            title = title_element.text.strip() if title_element else ""

            price_element = product_div.find('span', {'class': 'price'})
            price = ''
            if price_element:
                price_text = price_element.text.strip()
                price = ''.join(filter(str.isdigit, price_text))

            return self.format_result(product, title, price)

        except Exception as e:
            print(f"Error scraping Visions: {str(e)}")
            return self.format_result(product, "", "", "")

class CanadianTireScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__('Canadian Tire', base_url)

    async def search_product(self, product: Dict) -> Dict:
        try:
            search_query = product['name'].replace('"', '').replace('"', '')
            search_url = f"{self.base_url}/search?q={'%20'.join(search_query.split())}"
            
            page_content = await self.get_page(search_url)
            if not page_content:
                return self.format_result(product, "", "", "")

            soup = BeautifulSoup(page_content, 'html.parser')
            
            product_div = soup.find('div', {'class': 'product-tile'})
            if not product_div:
                return self.format_result(product, "", "", "")

            title_element = product_div.find('div', {'class': 'product-name'})
            title = title_element.text.strip() if title_element else ""

            price_element = product_div.find('span', {'class': 'price-value'})
            price = ''
            if price_element:
                price_text = price_element.text.strip()
                price = ''.join(filter(str.isdigit, price_text))

            return self.format_result(product, title, price)

        except Exception as e:
            print(f"Error scraping Canadian Tire: {str(e)}")
            return self.format_result(product, "", "", "")

# Update the PriceScraper class to include the new scrapers
class PriceScraper:
    def __init__(self):
        self.scrapers = [
            AmazonScraper(WEBSITES['amazon']),
            BestBuyScraper(WEBSITES['bestbuy']),
            CostcoScraper(WEBSITES['costco']),
            StaplesScraper(WEBSITES['staples']),
            VisionsScraper(WEBSITES['visions']),
            CanadianTireScraper(WEBSITES['canadiantire']),
            # Add more scrapers as we implement them
        ]

    # ... (rest of the PriceScraper class remains the same) ... 