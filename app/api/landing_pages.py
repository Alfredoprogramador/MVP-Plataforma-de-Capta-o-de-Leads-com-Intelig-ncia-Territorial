from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from jinja2 import Template
import os

router = APIRouter(prefix="/api/landing-pages", tags=["landing-pages"])


@router.post("/", response_model=schemas.LandingPage)
def create_landing_page(page: schemas.LandingPageCreate, db: Session = Depends(get_db)):
    """Create a new landing page"""
    # Check if slug already exists
    existing = db.query(models.LandingPage).filter(
        models.LandingPage.slug == page.slug
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Landing page with this slug already exists")
    
    db_page = models.LandingPage(**page.dict())
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page


@router.get("/", response_model=List[schemas.LandingPage])
def list_landing_pages(
    skip: int = 0,
    limit: int = 100,
    neighborhood: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """List landing pages"""
    query = db.query(models.LandingPage)
    
    if neighborhood:
        query = query.filter(models.LandingPage.neighborhood == neighborhood)
    if is_active is not None:
        query = query.filter(models.LandingPage.is_active == is_active)
    
    pages = query.offset(skip).limit(limit).all()
    return pages


@router.get("/{page_id}", response_model=schemas.LandingPage)
def get_landing_page(page_id: int, db: Session = Depends(get_db)):
    """Get landing page by ID"""
    page = db.query(models.LandingPage).filter(models.LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    return page


@router.put("/{page_id}", response_model=schemas.LandingPage)
def update_landing_page(
    page_id: int,
    page_update: schemas.LandingPageUpdate,
    db: Session = Depends(get_db)
):
    """Update landing page"""
    page = db.query(models.LandingPage).filter(models.LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    
    update_data = page_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(page, field, value)
    
    db.commit()
    db.refresh(page)
    return page


@router.delete("/{page_id}")
def delete_landing_page(page_id: int, db: Session = Depends(get_db)):
    """Delete landing page"""
    page = db.query(models.LandingPage).filter(models.LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    
    db.delete(page)
    db.commit()
    return {"message": "Landing page deleted successfully"}


@router.post("/{page_id}/submit")
async def submit_landing_page_form(
    page_id: int,
    submission: schemas.LandingPageSubmission,
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit lead form from landing page"""
    page = db.query(models.LandingPage).filter(models.LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    
    # Extract UTM parameters from request
    utm_params = request.query_params
    
    # Create lead
    lead_data = {
        "name": submission.name,
        "phone": submission.phone,
        "email": submission.email,
        "neighborhood": page.neighborhood,
        "city": page.city,
        "state": page.state,
        "source": "landing_page",
        "landing_page_id": page_id,
        "utm_source": utm_params.get("utm_source"),
        "utm_medium": utm_params.get("utm_medium"),
        "utm_campaign": utm_params.get("utm_campaign"),
        "utm_content": utm_params.get("utm_content"),
        "utm_term": utm_params.get("utm_term"),
        "extra_data": {"message": submission.message} if submission.message else None
    }
    
    # Check if lead exists
    existing_lead = db.query(models.Lead).filter(models.Lead.phone == submission.phone).first()
    if existing_lead:
        # Update existing lead
        for field, value in lead_data.items():
            if value is not None:
                setattr(existing_lead, field, value)
        db.commit()
        lead = existing_lead
    else:
        # Create new lead
        lead = models.Lead(**lead_data)
        db.add(lead)
        db.commit()
        db.refresh(lead)
    
    return {
        "message": "Lead submitted successfully",
        "lead_id": lead.id
    }
