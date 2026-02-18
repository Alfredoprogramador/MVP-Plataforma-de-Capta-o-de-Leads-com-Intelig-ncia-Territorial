from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services import proposal_service, whatsapp_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/proposals", tags=["proposals"])


@router.post("/", response_model=schemas.Proposal)
async def create_proposal(
    proposal: schemas.ProposalCreate,
    db: Session = Depends(get_db)
):
    """Create a new proposal"""
    # Verify lead exists
    lead = db.query(models.Lead).filter(models.Lead.id == proposal.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Create proposal
    db_proposal = models.Proposal(
        lead_id=proposal.lead_id,
        title=proposal.title,
        description=proposal.description,
        amount=proposal.amount,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    
    # Generate PDF
    try:
        pdf_path = proposal_service.generate_proposal_pdf(
            proposal_id=db_proposal.id,
            lead_name=lead.name or "Cliente",
            lead_neighborhood=lead.neighborhood or "N/A",
            title=proposal.title,
            description=proposal.description,
            amount=proposal.amount
        )
        db_proposal.pdf_path = pdf_path
        
        # Generate link
        proposal_link = proposal_service.generate_proposal_link(db_proposal.id)
        db_proposal.proposal_link = proposal_link
        
        db.commit()
        db.refresh(db_proposal)
        
    except Exception as e:
        logger.error(f"Error generating proposal: {e}")
    
    # Update lead status
    lead.status = models.LeadStatus.PROPOSAL_SENT
    db.commit()
    
    # Send WhatsApp notification
    try:
        message = f"""🎉 *Proposta Comercial*

Olá {lead.name or 'Cliente'}!

Preparamos uma proposta especial para você:
*{proposal.title}*

💰 Valor: R$ {proposal.amount:,.2f}

Acesse o link abaixo para visualizar e aceitar:
{proposal_link}

⏰ Válida por 7 dias!

Dúvidas? Estamos à disposição!"""
        
        await whatsapp_service.send_text_message(lead.phone, message)
        
    except Exception as e:
        logger.error(f"Error sending proposal notification: {e}")
    
    return db_proposal


@router.get("/", response_model=List[schemas.Proposal])
def list_proposals(
    skip: int = 0,
    limit: int = 100,
    lead_id: int = None,
    is_accepted: bool = None,
    db: Session = Depends(get_db)
):
    """List proposals"""
    query = db.query(models.Proposal)
    
    if lead_id:
        query = query.filter(models.Proposal.lead_id == lead_id)
    if is_accepted is not None:
        query = query.filter(models.Proposal.is_accepted == is_accepted)
    
    proposals = query.offset(skip).limit(limit).all()
    return proposals


@router.get("/{proposal_id}", response_model=schemas.Proposal)
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    """Get proposal by ID"""
    proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.get("/{proposal_id}/pdf")
def download_proposal_pdf(proposal_id: int, db: Session = Depends(get_db)):
    """Download proposal PDF"""
    proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if not proposal.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not generated")
    
    return FileResponse(
        proposal.pdf_path,
        media_type="application/pdf",
        filename=f"proposta_{proposal_id}.pdf"
    )


@router.post("/{proposal_id}/accept")
async def accept_proposal(proposal_id: int, db: Session = Depends(get_db)):
    """Accept proposal"""
    proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.is_accepted:
        return {"message": "Proposal already accepted"}
    
    # Mark as accepted
    proposal.is_accepted = True
    proposal.accepted_at = datetime.utcnow()
    
    # Update lead status
    lead = db.query(models.Lead).filter(models.Lead.id == proposal.lead_id).first()
    if lead:
        lead.status = models.LeadStatus.PROPOSAL_ACCEPTED
        lead.temperature = models.LeadTemperature.HOT
        lead.score = 100
    
    db.commit()
    
    # Send notification to lead
    try:
        message = f"""✅ *Proposta Aceita!*

Obrigado por aceitar nossa proposta!

Em breve nossa equipe entrará em contato para dar continuidade.

Estamos ansiosos para trabalhar com você! 🎉"""
        
        await whatsapp_service.send_text_message(lead.phone, message)
        
    except Exception as e:
        logger.error(f"Error sending acceptance notification: {e}")
    
    return {"message": "Proposal accepted successfully"}


# Web page for proposal acceptance
@router.get("/{proposal_id}/view", response_class=HTMLResponse)
def view_proposal_page(proposal_id: int, db: Session = Depends(get_db)):
    """View proposal acceptance page"""
    proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    lead = db.query(models.Lead).filter(models.Lead.id == proposal.lead_id).first()
    
    html = proposal_service.generate_acceptance_page(
        proposal_id=proposal.id,
        lead_name=lead.name or "Cliente",
        title=proposal.title,
        amount=proposal.amount
    )
    
    return HTMLResponse(content=html)
