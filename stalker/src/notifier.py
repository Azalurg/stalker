import logging
import os
import email
import smtplib

logger = logging.getLogger(__name__)


class Notifier:

    def __init__(self):
        self._from = os.getenv("EMAIL_FROM")
        self._to = os.getenv("EMAIL_TO")
        self._password = os.getenv("EMAIL_PASSWORD")
        self._smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self._smtp_port = int(os.getenv("SMTP_PORT", 587))



    def start_server(self):
        self._server = smtplib.SMTP(self._smtp_server, self._smtp_port)
        self._server.starttls()
        self._server.login(self._from, self._password)
        logger.info("SMTP server started and logged in")

    def quit_server(self):
        self._server.quit()
        logger.info("SMTP server connection closed")

    def send_email(self, subject: str, body: str):
        """Send an email notification."""
        if not self._from or not self._to or not self._password:
            logger.error("Email configuration is incomplete. Cannot send email.")
            return

        try:
            msg = email.message.EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self._from
            msg["To"] = self._to
            msg.set_content(body)

            self._server.send_message(msg)
            logger.info(f"Email sent to {self._to} with subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
        finally:
            self.quit_server()
