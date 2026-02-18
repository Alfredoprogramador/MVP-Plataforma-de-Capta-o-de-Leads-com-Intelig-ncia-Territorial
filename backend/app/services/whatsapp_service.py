"""
WhatsApp Cloud API Service for bidirectional communication
"""
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for WhatsApp Cloud API integration"""
    
    def __init__(self, config):
        self.api_token = config.WHATSAPP_API_TOKEN
        self.phone_number_id = config.WHATSAPP_PHONE_NUMBER_ID
        self.verify_token = config.WHATSAPP_VERIFY_TOKEN
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        
    def send_text_message(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Send a text message via WhatsApp"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "text",
                "text": {
                    "preview_url": True,
                    "body": message
                }
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Message sent successfully to {to_phone}")
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_media_message(
        self, 
        to_phone: str, 
        media_type: str, 
        media_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send media message (image, audio, video, document)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            media_object = {
                "link": media_url
            }
            
            if caption and media_type in ['image', 'video', 'document']:
                media_object["caption"] = caption
            
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": media_type,
                media_type: media_object
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Media message sent successfully to {to_phone}")
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Failed to send media message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_template_message(
        self, 
        to_phone: str, 
        template_name: str,
        language_code: str = "pt_BR",
        components: Optional[list] = None
    ) -> Dict[str, Any]:
        """Send a WhatsApp template message"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            template = {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
            
            if components:
                template["components"] = components
            
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "template",
                "template": template
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Template message sent successfully to {to_phone}")
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Failed to send template message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to mark message as read: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook subscription"""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook verified successfully")
            return challenge
        logger.warning("Webhook verification failed")
        return None
    
    def parse_webhook_message(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse incoming webhook message"""
        try:
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            messages = value.get('messages', [])
            if not messages:
                return None
            
            message = messages[0]
            
            parsed = {
                'message_id': message.get('id'),
                'from_phone': message.get('from'),
                'timestamp': message.get('timestamp'),
                'type': message.get('type', 'text'),
                'content': None,
                'media_url': None
            }
            
            # Extract content based on type
            if parsed['type'] == 'text':
                parsed['content'] = message.get('text', {}).get('body')
            elif parsed['type'] in ['image', 'audio', 'video', 'document']:
                media_data = message.get(parsed['type'], {})
                parsed['media_url'] = media_data.get('id')  # Media ID to download
                parsed['content'] = media_data.get('caption', '')
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse webhook message: {str(e)}")
            return None
