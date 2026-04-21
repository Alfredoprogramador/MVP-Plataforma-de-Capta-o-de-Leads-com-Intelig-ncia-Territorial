from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.orm import relationship
import enum

from .database import Base


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    converted = "converted"
    lost = "lost"


class LeadSource(str, enum.Enum):
    web_form = "web_form"
    whatsapp = "whatsapp"
    manual = "manual"


class MessageDirection(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=True)
    full_name = Column(String(150), nullable=True)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LeadNote(Base):
    __tablename__ = "lead_notes"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    author = Column(String(150), default="admin")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="timeline")


class Territory(Base):
    __tablename__ = "territories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    polygon = Column(Text, nullable=True)  # JSON string: [[lat, lng], ...]
    color = Column(String(7), default="#3B82F6")
    responsible_agent = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    leads = relationship("Lead", back_populates="territory")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(200), nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(250), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(15), nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    territory_id = Column(Integer, ForeignKey("territories.id"), nullable=True)
    territory = relationship("Territory", back_populates="leads")

    status = Column(SAEnum(LeadStatus), default=LeadStatus.new, nullable=False)
    source = Column(SAEnum(LeadSource), default=LeadSource.web_form, nullable=False)

    ai_score = Column(Integer, nullable=True)  # 0-100
    ai_notes = Column(Text, nullable=True)
    whatsapp_conversation = Column(Text, nullable=True)  # JSON string

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("WhatsAppMessage", back_populates="lead")
    timeline = relationship("LeadNote", back_populates="lead", order_by="LeadNote.created_at")


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    lead = relationship("Lead", back_populates="messages")

    from_number = Column(String(30), nullable=False)
    to_number = Column(String(30), nullable=False)
    message_body = Column(Text, nullable=False)
    direction = Column(SAEnum(MessageDirection), nullable=False)
    status = Column(String(30), default="sent")

    created_at = Column(DateTime, default=datetime.utcnow)
