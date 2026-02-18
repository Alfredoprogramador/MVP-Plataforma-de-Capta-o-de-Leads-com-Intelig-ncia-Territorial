from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    PROPOSAL_ACCEPTED = "proposal_accepted"
    CONVERTED = "converted"
    LOST = "lost"


class LeadTemperature(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    UNQUALIFIED = "unqualified"


class MessageType(str, enum.Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    phone = Column(String(50), unique=True, index=True)
    email = Column(String(255), nullable=True)
    
    # Territorial intelligence
    neighborhood = Column(String(255), index=True)
    city = Column(String(255))
    state = Column(String(50))
    
    # Origin tracking
    source = Column(String(100), index=True)  # instagram, google, landing_page, etc.
    utm_source = Column(String(255), nullable=True)
    utm_medium = Column(String(255), nullable=True)
    utm_campaign = Column(String(255), nullable=True)
    utm_content = Column(String(255), nullable=True)
    utm_term = Column(String(255), nullable=True)
    landing_page_id = Column(Integer, ForeignKey("landing_pages.id"), nullable=True)
    
    # Lead qualification
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    temperature = Column(Enum(LeadTemperature), default=LeadTemperature.UNQUALIFIED)
    score = Column(Integer, default=0)
    
    # Additional info
    notes = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Changed from 'metadata' to avoid SQLAlchemy conflict
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction_at = Column(DateTime, nullable=True)
    
    # Relationships
    landing_page = relationship("LandingPage", back_populates="leads")
    messages = relationship("Message", back_populates="lead", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="lead", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="lead", cascade="all, delete-orphan")


class LandingPage(Base):
    __tablename__ = "landing_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, index=True)
    title = Column(String(255))
    
    # Territorial segmentation
    neighborhood = Column(String(255), index=True)
    city = Column(String(255))
    state = Column(String(50))
    
    # Template configuration
    template_name = Column(String(100), default="default")
    template_data = Column(JSON, nullable=True)  # Dynamic content
    
    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leads = relationship("Lead", back_populates="landing_page")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    
    # Message content
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    content = Column(Text)
    media_url = Column(String(500), nullable=True)
    
    # Direction
    is_from_lead = Column(Boolean, default=True)
    
    # WhatsApp specific
    whatsapp_message_id = Column(String(255), nullable=True, unique=True)
    
    # Status
    sent = Column(Boolean, default=False)
    delivered = Column(Boolean, default=False)
    read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="messages")


class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    
    # Proposal details
    title = Column(String(255))
    description = Column(Text)
    amount = Column(Float)
    
    # PDF and link
    pdf_path = Column(String(500), nullable=True)
    proposal_link = Column(String(500), nullable=True)
    
    # Acceptance
    is_accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    lead = relationship("Lead", back_populates="proposals")


class FollowUp(Base):
    __tablename__ = "follow_ups"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    
    # Schedule
    scheduled_at = Column(DateTime)
    executed_at = Column(DateTime, nullable=True)
    
    # Content
    message_template = Column(Text)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    media_url = Column(String(500), nullable=True)
    
    # Urgency features
    include_timer = Column(Boolean, default=False)
    timer_hours = Column(Integer, default=24)
    
    # Trigger rules
    trigger_event = Column(String(100), nullable=True)  # e.g., "proposal_sent", "no_response_24h"
    
    # Status
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="follow_ups")


class MessageTemplate(Base):
    __tablename__ = "message_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    
    # Template content
    content = Column(Text)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    
    # Variables that can be replaced
    variables = Column(JSON, nullable=True)  # e.g., ["name", "neighborhood", "amount"]
    
    # Category
    category = Column(String(100))  # e.g., "welcome", "follow_up", "proposal"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BusinessRule(Base):
    __tablename__ = "business_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    description = Column(Text, nullable=True)
    
    # Conditions (JSON format)
    conditions = Column(JSON)  # e.g., {"temperature": "hot", "score": ">80"}
    
    # Actions (JSON format)
    actions = Column(JSON)  # e.g., {"notify_sales": true, "send_template": "hot_lead_welcome"}
    
    # Priority
    priority = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
