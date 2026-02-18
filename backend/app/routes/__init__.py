"""
Routes initialization
"""
from .leads import leads_bp
from .whatsapp import whatsapp_bp
from .landing import landing_bp
from .proposals import proposals_bp

__all__ = ['leads_bp', 'whatsapp_bp', 'landing_bp', 'proposals_bp']
