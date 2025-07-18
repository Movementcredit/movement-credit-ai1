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
    attachment_paths=None
):
    """
    Send an email with optional attachments.
    
    Args:
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP server port
        smtp_user (str): SMTP username
        smtp_password (str): SMTP password
        sender_email (str): Sender's email address
        recipient_email (str): Recipient's email address
        subject (str): Email subject
        body (str): Email body
        attachment_paths (list): List of file paths to attach
    """
    try:
        # Create message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content(body)
        
        # Add attachments if provided
        if attachment_paths:
            for attachment_path in attachment_paths:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        file_data = f.read()
                        file_name = os.path.basename(attachment_path)
                        msg.add_attachment(
                            file_data,
                            maintype='application',
                            subtype='octet-stream',
                            filename=file_name
                        )
        
        # Send email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            
        print(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise e
