"""
Basic tests for the Lead Platform MVP
"""
import pytest
from app.utils.helpers import (
    validate_phone,
    format_phone_whatsapp,
    generate_slug,
    parse_utm_params
)


def test_validate_phone():
    """Test phone validation"""
    # Valid phones
    assert validate_phone('11999999999') == True
    assert validate_phone('(11) 99999-9999') == True
    assert validate_phone('+5511999999999') == True
    
    # Invalid phones
    assert validate_phone('123') == False
    assert validate_phone('abc') == False


def test_format_phone_whatsapp():
    """Test phone formatting for WhatsApp"""
    assert format_phone_whatsapp('11999999999') == '+5511999999999'
    assert format_phone_whatsapp('(11) 99999-9999') == '+5511999999999'
    assert format_phone_whatsapp('+5511999999999') == '+5511999999999'


def test_generate_slug():
    """Test slug generation"""
    assert generate_slug('Jardim Paulista') == 'jardim-paulista'
    assert generate_slug('São Paulo - Centro') == 'so-paulo-centro'
    assert generate_slug('  Multiple   Spaces  ') == 'multiple-spaces'


def test_parse_utm_params():
    """Test UTM parameter parsing"""
    params = {
        'utm_source': 'google',
        'utm_medium': 'cpc',
        'utm_campaign': 'summer_sale',
        'invalid_param': 'test'
    }
    
    result = parse_utm_params(params)
    
    assert 'utm_source' in result
    assert 'utm_medium' in result
    assert 'utm_campaign' in result
    assert 'invalid_param' not in result
    assert result['utm_source'] == 'google'
