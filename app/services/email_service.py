import resend

from app.core.config import RESEND_API_KEY

import logging

logger = logging.getLogger(__name__)

class EmailService:

    def __init__(self):
        resend.api_key = RESEND_API_KEY

    def send_reminder_email(
        self,
        to_email: str,
        company_name: str,
        role: str
    ):
        try:
            resend.Emails.send(
                {
                    "from": "onboarding@resend.dev",
                    "to": to_email,
                    "subject": f"Reminder: Follow up with {company_name}",
                    "html": f"""
                    <h2>Job Application Reminder</h2>

                    <p>
                        Don't forget to follow up on your
                        <strong>{role}</strong>
                        application at
                        <strong>{company_name}</strong>.
                    </p>
                    """
                }
            )

            logger.info(
                "EMAIL_SENT | recipient=%s | company=%s | role=%s",
                to_email,
                company_name,
                role,
            )

        except Exception:
            logger.exception(
                "EMAIL_SEND_FAILED | recipient=%s | company=%s",
                to_email,
                company_name,
            )
            raise