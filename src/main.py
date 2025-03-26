import asyncio
import json
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

from scrapers.amazon_scraper import AmazonScraper
from scrapers.bestbuy_scraper import BestBuyScraper
from scrapers.costco_scraper import CostcoScraper
from scrapers.staples_scraper import StaplesScraper
from scrapers.visions_scraper import VisionsScraper
from scrapers.londondrugs_scraper import LondonDrugsScraper
from scrapers.samsung_scraper import SamsungScraper

from config.settings import WEBSITES

class PriceScraper:
    def __init__(self):
        # Initialize scrapers
        self.scrapers = [
            AmazonScraper(WEBSITES['amazon']),
            BestBuyScraper(WEBSITES['bestbuy']),
            CostcoScraper(WEBSITES['costco']),
            StaplesScraper(WEBSITES['staples']),
            VisionsScraper(WEBSITES['visions']),
            LondonDrugsScraper(WEBSITES['londondrugs']),
            SamsungScraper(WEBSITES['samsung']),
        ]
        # List of known brands for verification
        self.known_brands = ['Samsung', 'LG', 'Hisense', 'SONY', 'TCL', 'Philips']

    async def process_product(self, product: Dict) -> Dict:
        """Process a single product across all scrapers"""
        brand = self.extract_brand(product['name'])
        results = []
        
        # Run all scrapers concurrently for this product
        tasks = [scraper.search_product(product) for scraper in self.scrapers]
        scraped_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(scraped_results):
            if isinstance(result, Dict):
                # Include all results, even if they don't have a price
                if result.get('Title'):
                    results.append(result)
                    print(f"Got result from {self.scrapers[i].website}: {result.get('Title')[:30]}...")
            elif isinstance(result, Exception):
                print(f"Error with {self.scrapers[i].website}: {str(result)}")

        return {
            "Brand": brand,
            "Product": results
        }

    def extract_brand(self, product_name: str) -> str:
        """Extract brand from product name"""
        brands = ['Samsung', 'LG', 'Hisense', 'SONY']
        for brand in brands:
            if brand.lower() in product_name.lower():
                return brand
        return "Unknown"

    def extract_brand_from_title(self, title: str) -> str:
        """Extract the actual brand from a product title"""
        if not title:
            return "Unknown"
            
        title_lower = title.lower()
        for brand in self.known_brands:
            if brand.lower() in title_lower:
                return brand
        return "Unknown"

    async def process_all_products(self, products: List[Dict]) -> List[Dict]:
        """Process all products concurrently and merge by brand"""
        tasks = [self.process_product(product) for product in products]
        all_results = await asyncio.gather(*tasks)
        
        # Close all scraper sessions
        close_tasks = [scraper.close() for scraper in self.scrapers]
        await asyncio.gather(*close_tasks)
        
        # Merge results by brand
        brand_results = defaultdict(list)
        for result in all_results:
            query_brand = result.get("Brand")
            
            for product in result.get("Product", []):
                product_title = product.get('Title', '')
                website = product.get('Website', '')
                
                # Special case: Force Samsung scraper results to be Samsung brand
                if website == 'Samsung':
                    print(f"Assigning Samsung scraped product to Samsung brand: '{product_title[:30]}...'")
                    brand_results['Samsung'].append(product)
                    continue
                    
                # For other scrapers, verify the brand in the title
                actual_brand = self.extract_brand_from_title(product_title)
                
                # Only add product if its title contains a brand
                if actual_brand != "Unknown":
                    # Add to the correct brand category
                    print(f"Assigning product '{product_title[:30]}...' to brand {actual_brand}")
                    brand_results[actual_brand].append(product)
                    
                elif query_brand and query_brand != "Unknown":
                    # If we can't detect a brand but have the query brand, use that
                    print(f"Using query brand {query_brand} for '{product_title[:30]}...'")
                    brand_results[query_brand].append(product)
        
        # Convert to final format
        final_results = []
        for brand, products in brand_results.items():
            if products:  # Only include brands with products
                final_results.append({
                    "Brand": brand,
                    "Products": products
                })
        
        return final_results

async def main():
    # Load input products
    products = [
        {"name": "Hisense 50\" 4K Smart Google AI Upscaler LED TV - 50A68N"},
        {"name": "Hisense 55\" 4K Smart Google AI Upscaler LED TV - 55A68N"},
        {"name": "Samsung 75\" 4K Tizen Smart CUHD TV - UN75DU7100FXZC"},
        {"name": "LG 50\" UHD 4K Smart LED TV - 50UT7570PUB"},
        {"name": "Samsung 65\" 4K Tizen Smart QLED TV - QN65Q60DAFXZC"},
        {"name": "Hisense 32\" HD Smart VIDAA LED TV - 32A4KV"},
        {"name": "Samsung 43\" 4K Tizen Smart CUHD TV-UN43DU7100FXZC"},
        {"name": "LG 65\" UHD 4K Smart LED TV - 65UT7570PUB"},
        {"name": "Samsung 75\" 4K Tizen Smart QLED TV - QN75Q60DAFXZC"},
        {"name": "Samsung 65\" Neo QLED 4K Tizen Smart TV QN85D - QN65QN85DBFXZC"},
        {"name": "LG 65\" 4K Smart evo C4 OLED TV - OLED65C4PUA"},
        {"name": "LG 86\" UHD 4K Smart LED TV - 86UT7590PUA"},
        {"name": "SONY 75\" X77L 4K HDR LED TV Google TV - KD75X77L"},
        {"name": "LG 55\" QNED80 4K Smart QLED TV - 55QNED80TUC"},
        {"name": "Samsung 65\" OLED 4K Tizen Smart TV S90D - QN65S90DAFXZC"},
        {"name": "Samsung 75\" 4K Tizen Smart QLED TV - QN75Q80DAFXZC"},
        {"name": "Samsung 65\" 4K Tizen Smart QLED TV - QN65Q80DAFXZC"},
        {"name": "Samsung 65\" 4K Tizen Smart CUHD TV - UN65DU7100FXZC"},
        {"name": "Samsung 75\" 4K Tizen Smart CUHD TV - UN75DU8000FXZC"},
        {"name": "Hisense 50\" 4K Smart Google AI Upscaler LED TV - 50A68N"}
    ]

    scraper = PriceScraper()
    results = await scraper.process_all_products(products)
    
    print(results)

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 