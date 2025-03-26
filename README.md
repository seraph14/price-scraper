# Price Comparison Scraper

A robust web scraper that compares product prices across multiple Canadian retailers including Amazon, Best Buy, Costco, London Drugs, Samsung, Staples, and Visions.

## Overview

This tool allows you to search for products across multiple retailers and compare prices to find the best deals. It handles JavaScript-rendered content, anti-scraping measures, and automatically formats the results.

## Setup

### Prerequisites

- Python 3.8 or higher
- Chrome or Firefox browser installed
- ChromeDriver or GeckoDriver (automatically managed)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/price-comparison-scraper.git
   cd price-comparison-scraper
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Update retailer URLs in `src/config/settings.py`:
   ```python
   WEBSITES = {
       'amazon': 'https://www.amazon.ca',
       'bestbuy': 'https://www.bestbuy.ca',
       'costco': 'https://www.costco.ca',
       'staples': 'https://www.staples.ca',
       'visions': 'https://www.visions.ca',
       'londondrugs': 'https://www.londondrugs.com',
       'samsung': 'https://www.samsung.com',
   }
   ```

## Usage

Run the scraper:
```bash
cd src
python main.py
```

Results will be saved to a timestamped JSON file (`results_YYYYMMDD_HHMMSS.json`).

### Sample Output

```json
[
  {
    "Brand": "Samsung",
    "Products": [
      {
        "Website": "Amazon",
        "Title": "SAMSUNG 75-Inch Class Crystal UHD AU8000 Series - 4K UHD HDR Smart TV",
        "Price": 997.99,
        "PriceValidTill": ""
      },
      {
        "Website": "BestBuy",
        "Title": "Samsung 75\" 4K UHD Smart Tizen TV (UN75DU7100FXZC) - 2023",
        "Price": 999.99,
        "PriceValidTill": ""
      }
    ]
  }
]
```
