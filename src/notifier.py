"""Email notifications via Resend."""

import os
import logging
import resend

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Failed to send notification."""
    pass


class EmailNotifier:
    """Send email alerts via Resend."""

    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.sender_email = os.environ.get('SENDER_EMAIL')
        raw_recipients = os.environ.get('RECIPIENT_EMAIL')

        if not self.api_key:
            raise NotificationError("RESEND_API_KEY must be set")

        if not self.sender_email:
            raise NotificationError("SENDER_EMAIL must be set (your verified Resend domain email)")

        if not raw_recipients:
            raise NotificationError("RECIPIENT_EMAIL must be set")
        self.recipient_emails = [
            email.strip()
            for email in raw_recipients.replace(';', ',').split(',')
            if email.strip()
        ]
        if not self.recipient_emails:
            raise NotificationError("RECIPIENT_EMAIL must include at least one address")

        resend.api_key = self.api_key

    def send_alert(self, message, subject="Wyze Doorbell Alert"):
        """
        Send email alert via Resend.

        Args:
            message: Message body
            subject: Email subject

        Returns:
            bool: True if sent successfully

        Raises:
            NotificationError: If sending fails
        """
        try:
            params = {
                "from": self.sender_email,
                "to": self.recipient_emails,
                "subject": subject,
                "text": message,
            }

            email = resend.Emails.send(params)
            logger.info(f"Email sent to {', '.join(self.recipient_emails)} (id: {email['id']})")
            return True

        except Exception as e:
            raise NotificationError(f"Failed to send email via Resend: {e}")

    def send_battery_alert(self, battery_level, doorbell_name):
        """
        Send low battery alert.

        Args:
            battery_level: Current battery percentage
            doorbell_name: Name of the doorbell

        Returns:
            bool: True if sent successfully
        """
        message = (
            f"Your Wyze doorbell battery is low!\n\n"
            f"Device: {doorbell_name}\n"
            f"Battery: {battery_level}%\n\n"
            f"Please charge it soon."
        )
        return self.send_alert(message, f"Low Battery: {doorbell_name} ({battery_level}%)")
