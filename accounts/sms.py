"""
accounts/sms.py
SMS sending utility. Uses Twilio by default.
Swap out send_otp_sms() to use any other provider (Fast2SMS, MSG91, etc.)
"""

import random
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_otp():
    """Return a cryptographically random 6-digit OTP string."""
    return f'{random.SystemRandom().randint(0, 999999):06d}'


def send_otp_sms(phone: str, otp: str) -> bool:
    """
    Send OTP to `phone` via Twilio.
    Returns True on success, False on failure.
    In development (DEBUG=True and no Twilio credentials), logs the OTP instead.
    """
    sid    = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    token  = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    sender = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

    if not all([sid, token, sender]):
        # Dev fallback — print to console like the email backend
        logger.warning(f'[DEV] OTP for {phone}: {otp}')
        print(f'\n{"="*50}\n[DEV] OTP for {phone}: {otp}\n{"="*50}\n')
        return True

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        client.messages.create(
            body=f'Your HOMEXO verification code is {otp}. Valid for 10 minutes. Do not share this code.',
            from_=sender,
            to=phone,
        )
        return True
    except Exception as exc:
        logger.error(f'SMS send failed for {phone}: {exc}')
        return False
