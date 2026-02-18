"""
Celery tasks for background processing
"""
from celery import Celery
from datetime import datetime
import os

celery = Celery('tasks')
celery.config_from_object({
    'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    'result_backend': os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'America/Sao_Paulo',
    'enable_utc': True,
})


@celery.task(name='tasks.send_scheduled_followup')
def send_scheduled_followup(followup_id):
    """Send scheduled follow-up message"""
    from app.models import db, FollowUp, Lead
    from app.services import WhatsAppService
    from config import config
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get follow-up
        followup = FollowUp.query.get(followup_id)
        if not followup:
            logger.error(f"Follow-up {followup_id} not found")
            return
        
        if followup.status != 'pending':
            logger.info(f"Follow-up {followup_id} already processed: {followup.status}")
            return
        
        # Get lead
        lead = followup.lead
        if not lead:
            logger.error(f"Lead not found for follow-up {followup_id}")
            followup.status = 'failed'
            followup.error_message = 'Lead not found'
            db.session.commit()
            return
        
        # Initialize WhatsApp service
        whatsapp_service = WhatsAppService(config['production'])
        
        # Prepare message with timer if needed
        message = followup.message_content
        if followup.include_timer:
            timer_text = f"\n\n⏰ ATENÇÃO: Esta oferta expira em {followup.timer_hours} horas!"
            message = message + timer_text
        
        # Send message
        if followup.message_type == 'text':
            result = whatsapp_service.send_text_message(lead.phone, message)
        else:
            result = whatsapp_service.send_media_message(
                lead.phone,
                followup.message_type,
                followup.media_url,
                message
            )
        
        # Update follow-up status
        if result['success']:
            followup.status = 'sent'
            followup.sent_at = datetime.utcnow()
            lead.last_contact_at = datetime.utcnow()
            logger.info(f"Follow-up {followup_id} sent successfully")
        else:
            followup.status = 'failed'
            followup.error_message = result.get('error', 'Unknown error')
            logger.error(f"Failed to send follow-up {followup_id}: {followup.error_message}")
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error sending follow-up {followup_id}: {str(e)}")
        try:
            followup.status = 'failed'
            followup.error_message = str(e)
            db.session.commit()
        except:
            pass


@celery.task(name='tasks.process_pending_followups')
def process_pending_followups():
    """Process all pending follow-ups that are due"""
    from app.models import FollowUp
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get all pending follow-ups that are due
        now = datetime.utcnow()
        pending_followups = FollowUp.query.filter(
            FollowUp.status == 'pending',
            FollowUp.scheduled_for <= now
        ).all()
        
        logger.info(f"Found {len(pending_followups)} pending follow-ups to process")
        
        for followup in pending_followups:
            send_scheduled_followup.delay(followup.id)
        
        return len(pending_followups)
        
    except Exception as e:
        logger.error(f"Error processing pending follow-ups: {str(e)}")
        return 0


# Schedule periodic task to check for pending follow-ups every 5 minutes
celery.conf.beat_schedule = {
    'process-pending-followups': {
        'task': 'tasks.process_pending_followups',
        'schedule': 300.0,  # Every 5 minutes
    },
}
