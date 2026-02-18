"""
Utility functions for the application
"""
import re
from datetime import datetime
from typing import Optional


def validate_phone(phone: str) -> bool:
    """
    Validate Brazilian phone number
    Accepts formats: (11) 99999-9999, 11999999999, +5511999999999
    """
    # Remove non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Brazilian phone (with or without country code)
    if len(digits) == 11:  # Without country code
        return True
    elif len(digits) == 13 and digits.startswith('55'):  # With country code
        return True
    
    return False


def format_phone_whatsapp(phone: str) -> str:
    """
    Format phone number for WhatsApp API
    Returns: +5511999999999
    """
    # Remove non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Add country code if not present
    if not digits.startswith('55'):
        digits = '55' + digits
    
    return '+' + digits


def calculate_lead_score(
    conversation_count: int,
    has_budget: bool,
    has_urgency: bool,
    response_time_avg: float,
    engagement_level: str
) -> int:
    """
    Calculate lead score based on multiple factors
    Returns: 0-100
    """
    score = 0
    
    # Conversation engagement (max 30 points)
    if conversation_count > 10:
        score += 30
    elif conversation_count > 5:
        score += 20
    elif conversation_count > 2:
        score += 10
    
    # Budget indication (20 points)
    if has_budget:
        score += 20
    
    # Urgency (25 points)
    if has_urgency:
        score += 25
    
    # Response time (15 points)
    if response_time_avg < 300:  # Less than 5 minutes
        score += 15
    elif response_time_avg < 3600:  # Less than 1 hour
        score += 10
    elif response_time_avg < 86400:  # Less than 1 day
        score += 5
    
    # Engagement level (10 points)
    engagement_scores = {
        'high': 10,
        'medium': 5,
        'low': 0
    }
    score += engagement_scores.get(engagement_level, 0)
    
    return min(100, score)


def parse_utm_params(utm_dict: dict) -> dict:
    """
    Parse and validate UTM parameters
    """
    valid_params = {}
    
    utm_keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
    
    for key in utm_keys:
        value = utm_dict.get(key)
        if value and isinstance(value, str):
            # Clean and validate
            cleaned = value.strip()[:100]  # Max 100 chars
            if cleaned:
                valid_params[key] = cleaned
    
    return valid_params


def format_currency_brl(value: float) -> str:
    """
    Format value as Brazilian Real currency
    """
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def time_ago(dt: datetime) -> str:
    """
    Convert datetime to human-readable "time ago" format
    """
    if not dt:
        return 'Nunca'
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'Agora mesmo'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minuto{"s" if minutes > 1 else ""} atrás'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hora{"s" if hours > 1 else ""} atrás'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} dia{"s" if days > 1 else ""} atrás'
    else:
        return dt.strftime('%d/%m/%Y')


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from text (basic sanitization)
    """
    return re.sub(r'<[^>]+>', '', text)
