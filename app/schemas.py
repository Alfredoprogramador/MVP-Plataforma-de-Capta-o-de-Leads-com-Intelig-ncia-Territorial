from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models import LeadStatus, LeadTemperature, MessageType


# Lead Schemas
class LeadBase(BaseModel):
    name: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class LeadCreate(LeadBase):
    source: str = "manual"
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    landing_page_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    status: Optional[LeadStatus] = None
    temperature: Optional[LeadTemperature] = None
    score: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Lead(LeadBase):
    id: int
    source: str
    status: LeadStatus
    temperature: LeadTemperature
    score: int
    created_at: datetime
    updated_at: datetime
    last_interaction_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Landing Page Schemas
class LandingPageBase(BaseModel):
    slug: str
    title: str
    neighborhood: str
    city: str
    state: str
    template_name: str = "default"
    template_data: Optional[Dict[str, Any]] = None


class LandingPageCreate(LandingPageBase):
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class LandingPageUpdate(BaseModel):
    title: Optional[str] = None
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    is_active: Optional[bool] = None


class LandingPage(LandingPageBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None


class MessageCreate(MessageBase):
    lead_id: int
    is_from_lead: bool = False


class Message(MessageBase):
    id: int
    lead_id: int
    is_from_lead: bool
    sent: bool
    delivered: bool
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Proposal Schemas
class ProposalBase(BaseModel):
    title: str
    description: str
    amount: float


class ProposalCreate(ProposalBase):
    lead_id: int


class Proposal(ProposalBase):
    id: int
    lead_id: int
    pdf_path: Optional[str] = None
    proposal_link: Optional[str] = None
    is_accepted: bool
    accepted_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Follow Up Schemas
class FollowUpBase(BaseModel):
    message_template: str
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None
    include_timer: bool = False
    timer_hours: int = 24


class FollowUpCreate(FollowUpBase):
    lead_id: int
    scheduled_at: datetime
    trigger_event: Optional[str] = None


class FollowUp(FollowUpBase):
    id: int
    lead_id: int
    scheduled_at: datetime
    executed_at: Optional[datetime] = None
    is_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Message Template Schemas
class MessageTemplateBase(BaseModel):
    name: str
    content: str
    message_type: MessageType = MessageType.TEXT
    category: str
    variables: Optional[List[str]] = None


class MessageTemplateCreate(MessageTemplateBase):
    pass


class MessageTemplate(MessageTemplateBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Business Rule Schemas
class BusinessRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int = 0


class BusinessRuleCreate(BusinessRuleBase):
    pass


class BusinessRule(BusinessRuleBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# WhatsApp Schemas
class WhatsAppMessage(BaseModel):
    phone: str
    message: str
    message_type: str = "text"
    media_url: Optional[str] = None


# Analytics Schemas
class LeadStats(BaseModel):
    total_leads: int
    new_leads: int
    qualified_leads: int
    converted_leads: int
    leads_by_status: Dict[str, int]
    leads_by_temperature: Dict[str, int]
    leads_by_neighborhood: Dict[str, int]
    leads_by_source: Dict[str, int]


# Landing Page Form Submission
class LandingPageSubmission(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    message: Optional[str] = None
