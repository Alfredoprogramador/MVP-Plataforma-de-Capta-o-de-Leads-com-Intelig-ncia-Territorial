"""
API Routes for WhatsApp Integration
"""
from flask import Blueprint, request, jsonify, current_app
from app.models import db, Lead, Conversation
from app.services import WhatsAppService, AILeadAgent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/api/whatsapp')


@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify WhatsApp webhook"""
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        whatsapp_service = WhatsAppService(current_app.config)
        result = whatsapp_service.verify_webhook(mode, token, challenge)
        
        if result:
            return result, 200
        else:
            return 'Verification failed', 403
            
    except Exception as e:
        logger.error(f"Webhook verification error: {str(e)}")
        return 'Error', 500


@whatsapp_bp.route('/webhook', methods=['POST'])
def receive_message():
    """Receive incoming WhatsApp messages"""
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        
        whatsapp_service = WhatsAppService(current_app.config)
        ai_service = AILeadAgent(current_app.config)
        
        # Parse message
        parsed_message = whatsapp_service.parse_webhook_message(data)
        if not parsed_message:
            return jsonify({'status': 'no_message'}), 200
        
        # Find or create lead
        phone = parsed_message['from_phone']
        lead = Lead.query.filter_by(phone=phone).first()
        
        if not lead:
            # Create new lead from WhatsApp
            lead = Lead(
                name=f"Lead {phone[-4:]}",  # Temporary name
                phone=phone,
                source='whatsapp',
                status='new'
            )
            db.session.add(lead)
            db.session.flush()
        
        # Save incoming message
        conversation = Conversation(
            lead_id=lead.id,
            message_id=parsed_message['message_id'],
            direction='inbound',
            message_type=parsed_message['type'],
            content=parsed_message['content'],
            media_url=parsed_message['media_url'],
            status='received'
        )
        db.session.add(conversation)
        
        # Mark as read
        whatsapp_service.mark_as_read(parsed_message['message_id'])
        
        # Get conversation history
        conversations = Conversation.query.filter_by(
            lead_id=lead.id
        ).order_by(Conversation.created_at.asc()).all()
        
        conversation_history = []
        for conv in conversations:
            role = 'user' if conv.direction == 'inbound' else 'assistant'
            conversation_history.append({
                'role': role,
                'content': conv.content or ''
            })
        
        # Generate AI response
        ai_response = ai_service.generate_response(
            conversation_history,
            lead_data=lead.to_dict()
        )
        
        # Send AI response
        send_result = whatsapp_service.send_text_message(phone, ai_response)
        
        if send_result['success']:
            # Save outbound message
            outbound_conv = Conversation(
                lead_id=lead.id,
                direction='outbound',
                message_type='text',
                content=ai_response,
                status='sent',
                ai_processed=True
            )
            db.session.add(outbound_conv)
            
            # Update lead
            lead.last_contact_at = datetime.utcnow()
            lead.status = 'contacted'
            
            # Add new message to history for classification
            conversation_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            
            # Classify lead
            classification = ai_service.classify_lead(
                conversation_history,
                lead.to_dict()
            )
            
            lead.score = classification['score']
            lead.temperature = classification['temperature']
            
            # Check if should escalate
            escalation = ai_service.should_escalate_to_human(
                conversation_history,
                lead.score
            )
            
            if escalation['should_escalate']:
                lead.notes = (lead.notes or '') + f"\n[AUTO] Escalation needed: {escalation['reason']}"
                logger.info(f"Lead {lead.id} flagged for escalation: {escalation['reason']}")
        
        db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500


@whatsapp_bp.route('/send', methods=['POST'])
def send_message():
    """Send WhatsApp message (manual)"""
    try:
        data = request.get_json()
        
        whatsapp_service = WhatsAppService(current_app.config)
        
        phone = data['phone']
        message_type = data.get('type', 'text')
        
        # Send message based on type
        if message_type == 'text':
            result = whatsapp_service.send_text_message(
                phone,
                data['message']
            )
        else:
            result = whatsapp_service.send_media_message(
                phone,
                message_type,
                data['media_url'],
                data.get('caption')
            )
        
        if result['success']:
            # Save to conversation if lead_id provided
            if 'lead_id' in data:
                conversation = Conversation(
                    lead_id=data['lead_id'],
                    direction='outbound',
                    message_type=message_type,
                    content=data.get('message') or data.get('caption'),
                    media_url=data.get('media_url'),
                    status='sent'
                )
                db.session.add(conversation)
                
                # Update lead
                lead = Lead.query.get(data['lead_id'])
                if lead:
                    lead.last_contact_at = datetime.utcnow()
                
                db.session.commit()
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500
