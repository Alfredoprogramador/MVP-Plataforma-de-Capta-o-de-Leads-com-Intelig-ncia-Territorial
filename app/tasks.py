from celery import Celery
from celery.schedules import crontab
from app.config import settings
from app.database import SessionLocal
from app import models
from app.services import whatsapp_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "leads_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task
def process_scheduled_follow_ups():
    """Process scheduled follow-ups"""
    db = SessionLocal()
    
    try:
        # Get follow-ups that should be executed
        now = datetime.utcnow()
        follow_ups = db.query(models.FollowUp).filter(
            models.FollowUp.scheduled_at <= now,
            models.FollowUp.is_completed == False
        ).all()
        
        for follow_up in follow_ups:
            try:
                lead = db.query(models.Lead).filter(
                    models.Lead.id == follow_up.lead_id
                ).first()
                
                if not lead:
                    continue
                
                # Prepare message
                message = follow_up.message_template
                
                # Replace variables
                message = message.replace("{name}", lead.name or "Cliente")
                message = message.replace("{neighborhood}", lead.neighborhood or "")
                
                # Add timer if needed
                if follow_up.include_timer:
                    timer_text = f"\n\n⏰ ATENÇÃO: Apenas {follow_up.timer_hours}h restantes!"
                    message += timer_text
                
                # Send message
                if follow_up.message_type == models.MessageType.TEXT:
                    result = whatsapp_service.send_text_message(lead.phone, message)
                else:
                    result = whatsapp_service.send_media_message(
                        lead.phone,
                        follow_up.media_url,
                        follow_up.message_type.value,
                        message
                    )
                
                # Mark as completed
                follow_up.is_completed = True
                follow_up.executed_at = datetime.utcnow()
                
                # Save message
                db_message = models.Message(
                    lead_id=lead.id,
                    content=message,
                    message_type=follow_up.message_type,
                    media_url=follow_up.media_url,
                    is_from_lead=False,
                    sent=True
                )
                db.add(db_message)
                
                db.commit()
                logger.info(f"Follow-up {follow_up.id} executed for lead {lead.id}")
                
            except Exception as e:
                logger.error(f"Error executing follow-up {follow_up.id}: {e}")
                continue
                
    finally:
        db.close()


@celery_app.task
def apply_business_rules():
    """Apply business rules to leads"""
    db = SessionLocal()
    
    try:
        # Get active business rules
        rules = db.query(models.BusinessRule).filter(
            models.BusinessRule.is_active == True
        ).order_by(models.BusinessRule.priority.desc()).all()
        
        # Get leads to process
        leads = db.query(models.Lead).filter(
            models.Lead.status.in_([
                models.LeadStatus.NEW,
                models.LeadStatus.CONTACTED,
                models.LeadStatus.QUALIFIED
            ])
        ).all()
        
        for lead in leads:
            for rule in rules:
                try:
                    # Check conditions
                    conditions = rule.conditions
                    match = True
                    
                    for key, value in conditions.items():
                        if key == "temperature":
                            if lead.temperature.value != value:
                                match = False
                                break
                        elif key == "score":
                            # Handle score comparisons like ">80"
                            if isinstance(value, str) and value.startswith(">"):
                                threshold = int(value[1:])
                                if lead.score <= threshold:
                                    match = False
                                    break
                            elif isinstance(value, str) and value.startswith("<"):
                                threshold = int(value[1:])
                                if lead.score >= threshold:
                                    match = False
                                    break
                    
                    if match:
                        # Execute actions
                        actions = rule.actions
                        
                        if actions.get("notify_sales"):
                            logger.info(f"Notifying sales team about lead {lead.id}")
                            # TODO: Implement sales notification
                        
                        if actions.get("send_template"):
                            template_name = actions["send_template"]
                            # TODO: Send template message
                            
                        logger.info(f"Applied rule {rule.name} to lead {lead.id}")
                        
                except Exception as e:
                    logger.error(f"Error applying rule {rule.id} to lead {lead.id}: {e}")
                    continue
                    
    finally:
        db.close()


@celery_app.task
def check_expired_proposals():
    """Check for expired proposals and send reminders"""
    db = SessionLocal()
    
    try:
        # Get proposals expiring in 24 hours
        tomorrow = datetime.utcnow() + timedelta(days=1)
        today = datetime.utcnow()
        
        expiring_proposals = db.query(models.Proposal).filter(
            models.Proposal.is_accepted == False,
            models.Proposal.expires_at <= tomorrow,
            models.Proposal.expires_at >= today
        ).all()
        
        for proposal in expiring_proposals:
            try:
                lead = db.query(models.Lead).filter(
                    models.Lead.id == proposal.lead_id
                ).first()
                
                if not lead:
                    continue
                
                message = f"""⏰ *LEMBRETE IMPORTANTE*

Olá {lead.name or 'Cliente'}!

Sua proposta está prestes a expirar em 24 horas!

💰 Valor: R$ {proposal.amount:,.2f}

Não perca esta oportunidade! Acesse o link e aceite agora:
{proposal.proposal_link}

Dúvidas? Estamos à disposição!"""
                
                whatsapp_service.send_text_message(lead.phone, message)
                logger.info(f"Sent expiration reminder for proposal {proposal.id}")
                
            except Exception as e:
                logger.error(f"Error sending reminder for proposal {proposal.id}: {e}")
                continue
                
    finally:
        db.close()


# Schedule tasks
celery_app.conf.beat_schedule = {
    "process-follow-ups-every-5-minutes": {
        "task": "app.tasks.process_scheduled_follow_ups",
        "schedule": 300.0,  # 5 minutes
    },
    "apply-business-rules-every-15-minutes": {
        "task": "app.tasks.apply_business_rules",
        "schedule": 900.0,  # 15 minutes
    },
    "check-expired-proposals-daily": {
        "task": "app.tasks.check_expired_proposals",
        "schedule": crontab(hour=10, minute=0),  # 10 AM daily
    },
}
