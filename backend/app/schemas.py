from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from .models import LeadStatus, LeadSource, MessageDirection


# ── Territory ──────────────────────────────────────────────────────────────────

class TerritoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    polygon: Optional[str] = None  # JSON string
    color: Optional[str] = "#3B82F6"
    responsible_agent: Optional[str] = None


class TerritoryCreate(TerritoryBase):
    pass


class TerritoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    polygon: Optional[str] = None
    color: Optional[str] = None
    responsible_agent: Optional[str] = None


class TerritoryOut(TerritoryBase):
    id: int
    created_at: datetime
    lead_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# ── Lead ───────────────────────────────────────────────────────────────────────

class LeadBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[LeadSource] = LeadSource.web_form


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[LeadStatus] = None
    territory_id: Optional[int] = None
    ai_score: Optional[int] = None
    ai_notes: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("ai_score")
    @classmethod
    def score_range(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError("ai_score must be between 0 and 100")
        return v


class LeadOut(LeadBase):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    territory_id: Optional[int] = None
    territory: Optional[TerritoryOut] = None
    status: LeadStatus
    ai_score: Optional[int] = None
    ai_notes: Optional[str] = None
    whatsapp_conversation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── WhatsApp ───────────────────────────────────────────────────────────────────

class WhatsAppSend(BaseModel):
    to_number: str
    message: str
    lead_id: Optional[int] = None


class WhatsAppMessageOut(BaseModel):
    id: int
    lead_id: Optional[int] = None
    from_number: str
    to_number: str
    message_body: str
    direction: MessageDirection
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── AI ─────────────────────────────────────────────────────────────────────────

class QualifyRequest(BaseModel):
    lead_id: int


class QualifyResult(BaseModel):
    lead_id: int
    score: int
    notes: str


class GenerateMessageRequest(BaseModel):
    lead_id: int
    context: Optional[str] = None


class GenerateMessageResult(BaseModel):
    message: str


class TerritoryInsightRequest(BaseModel):
    territory_id: int


class TerritoryInsightResult(BaseModel):
    insights: str


# ── Dashboard ──────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_leads: int
    new_today: int
    qualified: int
    converted: int
    total_territories: int


class LeadsByStatus(BaseModel):
    status: str
    count: int


class LeadsByTerritory(BaseModel):
    territory_id: Optional[int]
    territory_name: str
    count: int


class RecentActivity(BaseModel):
    leads: List[LeadOut]
    messages: List[WhatsAppMessageOut]
