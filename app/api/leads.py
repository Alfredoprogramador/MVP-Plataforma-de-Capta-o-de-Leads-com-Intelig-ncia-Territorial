from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from datetime import datetime

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.post("/", response_model=schemas.Lead)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead"""
    # Check if lead already exists with this phone
    existing_lead = db.query(models.Lead).filter(models.Lead.phone == lead.phone).first()
    if existing_lead:
        raise HTTPException(status_code=400, detail="Lead with this phone already exists")
    
    db_lead = models.Lead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/", response_model=List[schemas.Lead])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.LeadStatus] = None,
    temperature: Optional[models.LeadTemperature] = None,
    neighborhood: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List leads with filters"""
    query = db.query(models.Lead)
    
    if status:
        query = query.filter(models.Lead.status == status)
    if temperature:
        query = query.filter(models.Lead.temperature == temperature)
    if neighborhood:
        query = query.filter(models.Lead.neighborhood == neighborhood)
    if source:
        query = query.filter(models.Lead.source == source)
    
    leads = query.offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=schemas.Lead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get lead by ID"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=schemas.Lead)
def update_lead(lead_id: int, lead_update: schemas.LeadUpdate, db: Session = Depends(get_db)):
    """Update lead"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete lead"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    return {"message": "Lead deleted successfully"}


@router.get("/{lead_id}/messages", response_model=List[schemas.Message])
def get_lead_messages(lead_id: int, db: Session = Depends(get_db)):
    """Get all messages for a lead"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    messages = db.query(models.Message).filter(
        models.Message.lead_id == lead_id
    ).order_by(models.Message.created_at).all()
    
    return messages


@router.get("/stats/analytics", response_model=schemas.LeadStats)
def get_lead_stats(db: Session = Depends(get_db)):
    """Get lead analytics and statistics"""
    total_leads = db.query(models.Lead).count()
    
    # Count by status
    leads_by_status = {}
    for status in models.LeadStatus:
        count = db.query(models.Lead).filter(models.Lead.status == status).count()
        leads_by_status[status.value] = count
    
    # Count by temperature
    leads_by_temperature = {}
    for temp in models.LeadTemperature:
        count = db.query(models.Lead).filter(models.Lead.temperature == temp).count()
        leads_by_temperature[temp.value] = count
    
    # Count by neighborhood
    neighborhoods = db.query(
        models.Lead.neighborhood, 
        db.func.count(models.Lead.id)
    ).group_by(models.Lead.neighborhood).all()
    leads_by_neighborhood = {n[0] or "Unknown": n[1] for n in neighborhoods}
    
    # Count by source
    sources = db.query(
        models.Lead.source,
        db.func.count(models.Lead.id)
    ).group_by(models.Lead.source).all()
    leads_by_source = {s[0] or "Unknown": s[1] for s in sources}
    
    return {
        "total_leads": total_leads,
        "new_leads": leads_by_status.get("new", 0),
        "qualified_leads": leads_by_status.get("qualified", 0),
        "converted_leads": leads_by_status.get("converted", 0),
        "leads_by_status": leads_by_status,
        "leads_by_temperature": leads_by_temperature,
        "leads_by_neighborhood": leads_by_neighborhood,
        "leads_by_source": leads_by_source
    }
