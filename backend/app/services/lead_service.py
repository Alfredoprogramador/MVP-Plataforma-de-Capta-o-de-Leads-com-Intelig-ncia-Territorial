from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from ..models import Lead, Territory
from ..schemas import LeadCreate, LeadUpdate
from ..utils.geo_utils import geocode_address, find_territory


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    territory_id: Optional[int] = None,
    source: Optional[str] = None,
) -> List[Lead]:
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    if territory_id is not None:
        query = query.filter(Lead.territory_id == territory_id)
    if source:
        query = query.filter(Lead.source == source)
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


def create_lead(db: Session, data: LeadCreate) -> Lead:
    lead = Lead(**data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Try to geocode and auto-assign territory
    _enrich_lead(db, lead)
    return lead


def update_lead(db: Session, lead_id: int, data: LeadUpdate) -> Optional[Lead]:
    lead = get_lead(db, lead_id)
    if not lead:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int) -> bool:
    lead = get_lead(db, lead_id)
    if not lead:
        return False
    db.delete(lead)
    db.commit()
    return True


def _enrich_lead(db: Session, lead: Lead) -> None:
    """Geocode the lead address and assign a territory if possible."""
    if lead.address or lead.city:
        lat, lng = geocode_address(
            lead.address or "",
            lead.city or "",
            lead.state or "",
        )
        if lat and lng:
            lead.latitude = lat
            lead.longitude = lng
            territories = db.query(Territory).all()
            territory_id = find_territory(lat, lng, territories)
            if territory_id:
                lead.territory_id = territory_id
            lead.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(lead)


def assign_territory(db: Session, lead: Lead) -> None:
    """(Re)assign territory based on lead coordinates."""
    if lead.latitude and lead.longitude:
        territories = db.query(Territory).all()
        territory_id = find_territory(lead.latitude, lead.longitude, territories)
        lead.territory_id = territory_id
        lead.updated_at = datetime.utcnow()
        db.commit()
