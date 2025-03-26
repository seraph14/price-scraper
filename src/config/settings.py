import os
from dotenv import load_dotenv

load_dotenv()

# Websites to scrape
WEBSITES = {
    'costco': 'https://www.costco.ca',
    'staples': 'https://www.staples.ca',
    'bestbuy': 'https://www.bestbuy.ca',
    'amazon': 'https://www.amazon.ca',
    'visions': 'https://www.visions.ca',
    'londondrugs': 'https://www.londondrugs.com',
    'canadiantire': 'https://www.canadiantire.ca',
    'dufresne': 'https://www.dufresne.ca',
    'tanguay': 'https://www.tanguay.ca',
    'teppermans': 'https://www.teppermans.com',
    'lg': 'https://www.lg.com/ca_en',
    'samsung': 'https://www.samsung.com/ca'
}

# Headers for requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Timeouts
REQUEST_TIMEOUT = 30
SELENIUM_TIMEOUT = 20

# Rate limiting (in seconds)
REQUEST_DELAY = 6 