import httpx
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for WhatsApp Cloud API integration"""
    
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        
    async def send_text_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Send text message via WhatsApp"""
        # Format phone number (remove + and spaces)
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            raise
    
    async def send_media_message(
        self,
        phone: str,
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send media message (image, audio, document) via WhatsApp"""
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        media_data = {"link": media_url}
        if caption and media_type == "image":
            media_data["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": media_type,
            media_type: media_data
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error sending WhatsApp media: {e}")
            raise
    
    async def send_template_message(
        self,
        phone: str,
        template_name: str,
        language_code: str = "pt_BR",
        components: Optional[list] = None
    ) -> Dict[str, Any]:
        """Send template message via WhatsApp"""
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error sending WhatsApp template: {e}")
            raise
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook for WhatsApp"""
        if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
            logger.info("Webhook verified successfully")
            return challenge
        else:
            logger.warning("Webhook verification failed")
            return None
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            raise


# Singleton instance
whatsapp_service = WhatsAppService()
