from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import LeadCreate, LeadUpdate, LeadOut, QualifyResult
from ..services import lead_service
from ..services import ai_service
from ..models import LeadStatus

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("/stats/summary")
def lead_stats(db: Session = Depends(get_db)):
    from datetime import datetime, date
    from ..models import Lead
    total = db.query(Lead).count()
    today = db.query(Lead).filter(
        Lead.created_at >= datetime.combine(date.today(), datetime.min.time())
    ).count()
    qualified = db.query(Lead).filter(Lead.status == LeadStatus.qualified).count()
    converted = db.query(Lead).filter(Lead.status == LeadStatus.converted).count()
    return {"total": total, "new_today": today, "qualified": qualified, "converted": converted}


@router.get("/", response_model=List[LeadOut])
def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    territory_id: Optional[int] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return lead_service.get_leads(db, skip=skip, limit=limit, status=status,
                                   territory_id=territory_id, source=source)


@router.post("/", response_model=LeadOut, status_code=201)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    return lead_service.create_lead(db, data)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db)):
    lead = lead_service.update_lead(db, lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.delete("/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    if not lead_service.delete_lead(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead não encontrado")


@router.post("/{lead_id}/qualify", response_model=QualifyResult)
def qualify_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
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
    }
    result = ai_service.qualify_lead(lead_data)

    from ..schemas import LeadUpdate
    lead_service.update_lead(db, lead_id, LeadUpdate(
        ai_score=result["score"],
        ai_notes=result["notes"],
        status=LeadStatus.qualified if result["score"] >= 60 else None,
    ))

    return QualifyResult(lead_id=lead_id, score=result["score"], notes=result["notes"])
