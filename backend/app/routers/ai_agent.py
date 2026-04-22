from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    QualifyRequest, QualifyResult,
    GenerateMessageRequest, GenerateMessageResult,
    TerritoryInsightRequest, TerritoryInsightResult,
)
from ..services import ai_service, lead_service, territory_service
from ..models import Lead, LeadStatus
from ..schemas import LeadUpdate

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/qualify-lead", response_model=QualifyResult)
def qualify_lead(payload: QualifyRequest, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead_data = {
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "city": lead.city,
        "state": lead.state,
        "source": lead.source.value if lead.source else None,
        "notes": lead.notes,
        "whatsapp_conversation": lead.whatsapp_conversation,
    }
    result = ai_service.qualify_lead(lead_data)

    lead_service.update_lead(db, payload.lead_id, LeadUpdate(
        ai_score=result["score"],
        ai_notes=result["notes"],
        status=LeadStatus.qualified if result["score"] >= 60 else None,
    ))
    return QualifyResult(lead_id=payload.lead_id, score=result["score"], notes=result["notes"])


@router.post("/generate-message", response_model=GenerateMessageResult)
def generate_message(payload: GenerateMessageRequest, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead_data = {
        "name": lead.name,
        "city": lead.city,
        "state": lead.state,
        "status": lead.status.value if lead.status else None,
        "ai_score": lead.ai_score,
    }
    message = ai_service.generate_whatsapp_message(lead_data, context=payload.context or "")
    return GenerateMessageResult(message=message)


@router.post("/analyze-territory", response_model=TerritoryInsightResult)
def analyze_territory(payload: TerritoryInsightRequest, db: Session = Depends(get_db)):
    territory = territory_service.get_territory(db, payload.territory_id)
    if not territory:
        raise HTTPException(status_code=404, detail="Território não encontrado")

    leads = db.query(Lead).filter(Lead.territory_id == payload.territory_id).all()
    territory_data = {
        "name": territory.name,
        "description": territory.description,
        "responsible_agent": territory.responsible_agent,
    }
    leads_data = [
        {"name": l.name, "status": l.status.value, "ai_score": l.ai_score, "city": l.city}
        for l in leads
    ]
    insights = ai_service.analyze_territory(territory_data, leads_data)
    return TerritoryInsightResult(insights=insights)
