"""
Database models for the Lead Capture Platform
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Lead(db.Model):
    """Lead model with territorial intelligence"""
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=True)
    
    # Territorial Intelligence
    neighborhood = db.Column(db.String(100), nullable=True, index=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Lead Qualification
    status = db.Column(
        db.String(20), 
        default='new',
        index=True
    )  # new, contacted, qualified, proposal_sent, accepted, rejected, lost
    score = db.Column(db.Integer, default=0)  # 0-100
    temperature = db.Column(
        db.String(10), 
        default='cold'
    )  # hot, warm, cold
    
    # Source Tracking
    source = db.Column(db.String(50), nullable=True, index=True)  # landing_page, instagram, google, whatsapp
    utm_source = db.Column(db.String(100), nullable=True)
    utm_medium = db.Column(db.String(100), nullable=True)
    utm_campaign = db.Column(db.String(100), nullable=True)
    utm_content = db.Column(db.String(100), nullable=True)
    utm_term = db.Column(db.String(100), nullable=True)
    landing_page_id = db.Column(db.Integer, db.ForeignKey('landing_pages.id'), nullable=True)
    
    # Additional Info
    notes = db.Column(db.Text, nullable=True)
    assigned_to = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    conversations = db.relationship('Conversation', back_populates='lead', cascade='all, delete-orphan')
    proposals = db.relationship('Proposal', back_populates='lead', cascade='all, delete-orphan')
    follow_ups = db.relationship('FollowUp', back_populates='lead', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lead {self.name} - {self.phone}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'neighborhood': self.neighborhood,
            'city': self.city,
            'state': self.state,
            'status': self.status,
            'score': self.score,
            'temperature': self.temperature,
            'source': self.source,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_contact_at': self.last_contact_at.isoformat() if self.last_contact_at else None
        }


class LandingPage(db.Model):
    """Landing page templates for neighborhood-specific campaigns"""
    __tablename__ = 'landing_pages'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    neighborhood = db.Column(db.String(100), nullable=True, index=True)
    
    # Template Configuration
    template_name = db.Column(db.String(50), default='default')
    hero_title = db.Column(db.String(300), nullable=True)
    hero_subtitle = db.Column(db.Text, nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    
    # Content Blocks
    content_sections = db.Column(db.JSON, nullable=True)  # Array of content sections
    cta_text = db.Column(db.String(100), default='Solicitar Orçamento')
    cta_button_color = db.Column(db.String(20), default='#0066cc')
    
    # SEO
    meta_description = db.Column(db.Text, nullable=True)
    meta_keywords = db.Column(db.Text, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leads = db.relationship('Lead', backref='landing_page', lazy=True)
    
    def __repr__(self):
        return f'<LandingPage {self.slug}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'neighborhood': self.neighborhood,
            'template_name': self.template_name,
            'hero_title': self.hero_title,
            'hero_subtitle': self.hero_subtitle,
            'hero_image_url': self.hero_image_url,
            'content_sections': self.content_sections,
            'cta_text': self.cta_text,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Conversation(db.Model):
    """WhatsApp conversation messages"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    
    # Message Details
    message_id = db.Column(db.String(200), unique=True, nullable=True)  # WhatsApp message ID
    direction = db.Column(db.String(10), nullable=False)  # inbound, outbound
    message_type = db.Column(db.String(20), default='text')  # text, audio, image, video, document
    content = db.Column(db.Text, nullable=True)
    media_url = db.Column(db.String(500), nullable=True)
    
    # AI Processing
    ai_processed = db.Column(db.Boolean, default=False)
    ai_intent = db.Column(db.String(100), nullable=True)
    ai_sentiment = db.Column(db.String(20), nullable=True)  # positive, neutral, negative
    
    # Status
    status = db.Column(db.String(20), default='sent')  # sent, delivered, read, failed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    lead = db.relationship('Lead', back_populates='conversations')
    
    def __repr__(self):
        return f'<Conversation {self.id} - Lead {self.lead_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'direction': self.direction,
            'message_type': self.message_type,
            'content': self.content,
            'media_url': self.media_url,
            'ai_processed': self.ai_processed,
            'ai_intent': self.ai_intent,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Proposal(db.Model):
    """Proposal documents for leads"""
    __tablename__ = 'proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    
    # Proposal Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    service_items = db.Column(db.JSON, nullable=True)  # Array of service items
    total_value = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Files
    pdf_url = db.Column(db.String(500), nullable=True)
    view_url = db.Column(db.String(500), nullable=True)  # Web view URL
    
    # Acceptance
    status = db.Column(
        db.String(20), 
        default='pending'
    )  # pending, accepted, rejected, expired
    accepted_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Validity
    valid_until = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lead = db.relationship('Lead', back_populates='proposals')
    
    def __repr__(self):
        return f'<Proposal {self.id} - Lead {self.lead_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'title': self.title,
            'description': self.description,
            'service_items': self.service_items,
            'total_value': float(self.total_value) if self.total_value else 0,
            'pdf_url': self.pdf_url,
            'view_url': self.view_url,
            'status': self.status,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FollowUp(db.Model):
    """Scheduled follow-up messages with multimedia support"""
    __tablename__ = 'follow_ups'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    
    # Schedule
    scheduled_for = db.Column(db.DateTime, nullable=False, index=True)
    
    # Message Content
    message_type = db.Column(db.String(20), default='text')  # text, image, audio, video
    message_content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500), nullable=True)
    
    # Urgency Features
    include_timer = db.Column(db.Boolean, default=False)
    timer_hours = db.Column(db.Integer, default=24)  # Hours for countdown
    
    # Trigger Conditions
    trigger_type = db.Column(db.String(50), nullable=True)  # scheduled, behavior, event
    trigger_condition = db.Column(db.JSON, nullable=True)
    
    # Status
    status = db.Column(
        db.String(20), 
        default='pending'
    )  # pending, sent, failed, cancelled
    sent_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = db.relationship('Lead', back_populates='follow_ups')
    
    def __repr__(self):
        return f'<FollowUp {self.id} - Lead {self.lead_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'message_type': self.message_type,
            'message_content': self.message_content,
            'media_url': self.media_url,
            'include_timer': self.include_timer,
            'timer_hours': self.timer_hours,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MessageTemplate(db.Model):
    """Reusable message templates"""
    __tablename__ = 'message_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=True)  # greeting, followup, proposal, urgency
    
    # Template Content
    message_type = db.Column(db.String(20), default='text')
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500), nullable=True)
    
    # Variables
    variables = db.Column(db.JSON, nullable=True)  # List of variable names
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MessageTemplate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'message_type': self.message_type,
            'content': self.content,
            'media_url': self.media_url,
            'variables': self.variables,
            'is_active': self.is_active
        }
