from datetime import datetime, date
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Lead, Territory, WhatsAppMessage, LeadStatus
from ..schemas import (
    DashboardStats, LeadsByStatus, LeadsByTerritory,
    RecentActivity, LeadOut, WhatsAppMessageOut,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    total_leads = db.query(Lead).count()
    new_today = db.query(Lead).filter(
        Lead.created_at >= datetime.combine(date.today(), datetime.min.time())
    ).count()
    qualified = db.query(Lead).filter(Lead.status == LeadStatus.qualified).count()
    converted = db.query(Lead).filter(Lead.status == LeadStatus.converted).count()
    total_territories = db.query(Territory).count()
    return DashboardStats(
        total_leads=total_leads,
        new_today=new_today,
        qualified=qualified,
        converted=converted,
        total_territories=total_territories,
    )


@router.get("/leads-by-status", response_model=List[LeadsByStatus])
def leads_by_status(db: Session = Depends(get_db)):
    rows = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    return [LeadsByStatus(status=r[0].value, count=r[1]) for r in rows]


@router.get("/leads-by-territory", response_model=List[LeadsByTerritory])
def leads_by_territory(db: Session = Depends(get_db)):
    rows = (
        db.query(Lead.territory_id, func.count(Lead.id))
        .group_by(Lead.territory_id)
        .all()
    )
    result = []
    for territory_id, count in rows:
        if territory_id:
            t = db.query(Territory).filter(Territory.id == territory_id).first()
            name = t.name if t else "Desconhecido"
        else:
            name = "Sem Território"
        result.append(LeadsByTerritory(territory_id=territory_id, territory_name=name, count=count))
    return result


@router.get("/recent-activity", response_model=RecentActivity)
def recent_activity(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).limit(10).all()
    messages = db.query(WhatsAppMessage).order_by(WhatsAppMessage.created_at.desc()).limit(10).all()
    return RecentActivity(
        leads=[LeadOut.model_validate(l) for l in leads],
        messages=[WhatsAppMessageOut.model_validate(m) for m in messages],
    )
