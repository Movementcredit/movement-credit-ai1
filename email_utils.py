
import smtplib
import os
from email.message import EmailMessage

def send_email_with_attachments(
    smtp_server,
    smtp_port,
    smtp_user,
    smtp_password,
    sender_email,
    recipient_email,
    subject,
    body,
    attachment_paths
):
    """Send email with attachments and return success status"""
    try:
        # Check if password is provided
        if not smtp_password:
            return False, "Gmail app password not configured. Please set GMAIL_APP_PASSWORD environment variable."
        
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.set_content(body)

        # Attach files
        attached_count = 0
        for file_path in attachment_paths:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                msg.add_attachment(
