import re
from typing import Optional

def clean_price(price_str: str) -> Optional[float]:
    """Convert price string to float"""
    try:
        # Remove currency symbols and non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return float(cleaned) if cleaned else None
    except ValueError:
        return None

def normalize_model_number(model: str) -> str:
    """Normalize model number for comparison"""
    return re.sub(r'[^A-Z0-9]', '', model.upper())

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings"""
    str1 = str1.lower()
    str2 = str2.lower()
    
    # Simple word matching similarity
    words1 = set(str1.split())
    words2 = set(str2.split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0 