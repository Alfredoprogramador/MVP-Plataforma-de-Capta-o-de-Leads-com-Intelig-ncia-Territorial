import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import WhatsAppSend, WhatsAppMessageOut
from ..services import whatsapp_service, ai_service
from ..models import WhatsAppMessage, Lead, MessageDirection, LeadSource
from ..services import lead_service

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    """Receive incoming WhatsApp messages from Twilio."""
    form_data = await request.form()
    data = whatsapp_service.parse_webhook(dict(form_data))

    from_number = data["from_number"]
    body = data["body"]

    if not from_number or not body:
        return {"status": "ignored"}

    # Find or create lead by phone number
    clean_number = from_number.replace("whatsapp:", "")
    lead = db.query(Lead).filter(Lead.phone == clean_number).first()

    if not lead:
        profile_name = data.get("profile_name", "")
        lead_data_schema = __import__(
            "app.schemas", fromlist=["LeadCreate"]
        ).LeadCreate(
            name=profile_name or clean_number,
            phone=clean_number,
            source=LeadSource.whatsapp,
        )
        lead = lead_service.create_lead(db, lead_data_schema)

    # Save inbound message
    msg = WhatsAppMessage(
        lead_id=lead.id,
        from_number=from_number,
        to_number=data["to_number"],
        message_body=body,
        direction=MessageDirection.inbound,
        status="received",
    )
    db.add(msg)

    # Update conversation log on lead
    conversation = []
    if lead.whatsapp_conversation:
        try:
            conversation = json.loads(lead.whatsapp_conversation)
        except (json.JSONDecodeError, TypeError):
            conversation = []
    conversation.append({"role": "user", "content": body})
    lead.whatsapp_conversation = json.dumps(conversation, ensure_ascii=False)
    db.commit()

    # Generate and send AI reply
    lead_data = {"name": lead.name, "city": lead.city, "state": lead.state}
    reply_text = ai_service.generate_whatsapp_message(lead_data, context=f"Mensagem recebida: {body}")
    send_result = whatsapp_service.send_message(from_number, reply_text)

    if send_result["success"]:
        out_msg = WhatsAppMessage(
            lead_id=lead.id,
            from_number=data["to_number"],
            to_number=from_number,
            message_body=reply_text,
            direction=MessageDirection.outbound,
            status="sent",
        )
        db.add(out_msg)
        conversation.append({"role": "assistant", "content": reply_text})
        lead.whatsapp_conversation = json.dumps(conversation, ensure_ascii=False)
        db.commit()

    return {"status": "ok"}


@router.post("/send", response_model=dict)
def send_message(payload: WhatsAppSend, db: Session = Depends(get_db)):
    result = whatsapp_service.send_message(payload.to_number, payload.message)
    if not result["success"]:
        raise HTTPException(status_code=502, detail=result["error"])

    lead_id = payload.lead_id
    msg = WhatsAppMessage(
        lead_id=lead_id,
        from_number=whatsapp_service.TWILIO_WHATSAPP_NUMBER,
        to_number=whatsapp_service.normalize_whatsapp_number(payload.to_number),
        message_body=payload.message,
        direction=MessageDirection.outbound,
        status="sent",
    )
    db.add(msg)
    db.commit()
    return {"success": True, "message_sid": result["message_sid"]}


@router.get("/conversations/{lead_id}", response_model=List[WhatsAppMessageOut])
def get_conversation(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return (
        db.query(WhatsAppMessage)
        .filter(WhatsAppMessage.lead_id == lead_id)
        .order_by(WhatsAppMessage.created_at.asc())
        .all()
    )
