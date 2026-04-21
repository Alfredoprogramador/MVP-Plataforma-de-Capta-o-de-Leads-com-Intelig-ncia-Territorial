import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

_twilio_client: Optional[Client] = None


def _get_client() -> Optional[Client]:
    global _twilio_client
    if _twilio_client is None:
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            _twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return _twilio_client


def normalize_whatsapp_number(number: str) -> str:
    """Ensure number has whatsapp: prefix."""
    number = number.strip()
    if not number.startswith("whatsapp:"):
        return f"whatsapp:{number}"
    return number


def send_message(to_number: str, body: str) -> dict:
    """Send a WhatsApp message via Twilio. Returns status dict."""
    client = _get_client()
    if not client:
        return {
            "success": False,
            "message_sid": None,
            "error": "Twilio não configurado. Defina TWILIO_ACCOUNT_SID e TWILIO_AUTH_TOKEN.",
        }
    try:
        to = normalize_whatsapp_number(to_number)
        msg = client.messages.create(
            body=body,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to,
        )
        return {"success": True, "message_sid": msg.sid, "error": None}
    except TwilioRestException as e:
        return {"success": False, "message_sid": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "message_sid": None, "error": str(e)}


def parse_webhook(form_data: dict) -> dict:
    """Parse Twilio webhook POST form data into a clean dict."""
    return {
        "from_number": form_data.get("From", ""),
        "to_number": form_data.get("To", ""),
        "body": form_data.get("Body", ""),
        "message_sid": form_data.get("MessageSid", ""),
        "profile_name": form_data.get("ProfileName", ""),
        "num_media": int(form_data.get("NumMedia", 0)),
    }
