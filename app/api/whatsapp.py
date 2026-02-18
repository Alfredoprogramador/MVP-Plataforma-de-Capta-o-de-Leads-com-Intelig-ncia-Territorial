from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app import models, schemas
from app.services import whatsapp_service, ai_agent_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verify WhatsApp webhook"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    result = whatsapp_service.verify_webhook(mode, token, challenge)
    if result:
        return Response(content=result, media_type="text/plain")
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming WhatsApp messages"""
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Parse WhatsApp webhook payload
        if "entry" not in body:
            return {"status": "ok"}
        
        for entry in body["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Handle messages
                if "messages" in value:
                    for message in value["messages"]:
                        await process_incoming_message(message, value, db)
                
                # Handle status updates
                if "statuses" in value:
                    for status in value["statuses"]:
                        await process_status_update(status, db)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


async def process_incoming_message(message: Dict[str, Any], value: Dict[str, Any], db: Session):
    """Process incoming WhatsApp message"""
    phone = message.get("from")
    message_id = message.get("id")
    message_type = message.get("type", "text")
    
    # Extract message content
    content = ""
    media_url = None
    
    if message_type == "text":
        content = message.get("text", {}).get("body", "")
    elif message_type == "audio":
        audio_data = message.get("audio", {})
        media_url = audio_data.get("id")  # Will need to download from WhatsApp
        content = "[Audio message]"
    elif message_type == "image":
        image_data = message.get("image", {})
        media_url = image_data.get("id")
        content = image_data.get("caption", "[Image]")
    
    # Find or create lead
    lead = db.query(models.Lead).filter(models.Lead.phone == phone).first()
    if not lead:
        # Create new lead from WhatsApp
        lead = models.Lead(
            phone=phone,
            source="whatsapp",
            status=models.LeadStatus.NEW
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
    
    # Save incoming message
    db_message = models.Message(
        lead_id=lead.id,
        content=content,
        message_type=models.MessageType(message_type) if message_type in ["text", "audio", "image"] else models.MessageType.TEXT,
        media_url=media_url,
        is_from_lead=True,
        whatsapp_message_id=message_id
    )
    db.add(db_message)
    
    # Update lead's last interaction
    lead.last_interaction_at = datetime.utcnow()
    db.commit()
    
    # Mark message as read
    try:
        await whatsapp_service.mark_as_read(message_id)
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
    
    # Get conversation history
    conversation_history = []
    messages = db.query(models.Message).filter(
        models.Message.lead_id == lead.id
    ).order_by(models.Message.created_at.desc()).limit(10).all()
    
    for msg in reversed(messages):
        conversation_history.append({
            "role": "user" if msg.is_from_lead else "assistant",
            "content": msg.content
        })
    
    # Generate AI response
    lead_info = {
        "name": lead.name or "Cliente",
        "neighborhood": lead.neighborhood,
        "city": lead.city,
        "source": lead.source
    }
    
    ai_response = await ai_agent_service.generate_response(
        content,
        conversation_history,
        lead_info
    )
    
    # Send AI response
    try:
        result = await whatsapp_service.send_text_message(phone, ai_response)
        
        # Save AI response
        response_message = models.Message(
            lead_id=lead.id,
            content=ai_response,
            message_type=models.MessageType.TEXT,
            is_from_lead=False,
            sent=True,
            whatsapp_message_id=result.get("messages", [{}])[0].get("id")
        )
        db.add(response_message)
        db.commit()
        
    except Exception as e:
        logger.error(f"Error sending AI response: {e}")
    
    # Check if should qualify lead
    if len(conversation_history) >= 3:  # After at least 3 messages
        qualification = await ai_agent_service.qualify_lead(conversation_history, lead_info)
        
        # Update lead
        lead.temperature = models.LeadTemperature(qualification.get("temperature", "cold"))
        lead.score = qualification.get("score", 0)
        lead.notes = qualification.get("summary", "")
        
        # Update status based on temperature
        if lead.temperature == models.LeadTemperature.HOT:
            lead.status = models.LeadStatus.QUALIFIED
        
        db.commit()


async def process_status_update(status: Dict[str, Any], db: Session):
    """Process message status update"""
    message_id = status.get("id")
    status_type = status.get("status")
    
    message = db.query(models.Message).filter(
        models.Message.whatsapp_message_id == message_id
    ).first()
    
    if message:
        if status_type == "sent":
            message.sent = True
        elif status_type == "delivered":
            message.delivered = True
        elif status_type == "read":
            message.read = True
        
        db.commit()


@router.post("/send")
async def send_whatsapp_message(
    message_data: schemas.WhatsAppMessage,
    db: Session = Depends(get_db)
):
    """Send WhatsApp message manually"""
    # Find lead
    lead = db.query(models.Lead).filter(models.Lead.phone == message_data.phone).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Send message
    try:
        if message_data.message_type == "text":
            result = await whatsapp_service.send_text_message(
                message_data.phone,
                message_data.message
            )
        else:
            result = await whatsapp_service.send_media_message(
                message_data.phone,
                message_data.media_url,
                message_data.message_type,
                message_data.message
            )
        
        # Save message
        db_message = models.Message(
            lead_id=lead.id,
            content=message_data.message,
            message_type=models.MessageType(message_data.message_type),
            media_url=message_data.media_url,
            is_from_lead=False,
            sent=True,
            whatsapp_message_id=result.get("messages", [{}])[0].get("id")
        )
        db.add(db_message)
        db.commit()
        
        return {"message": "Message sent successfully", "result": result}
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
