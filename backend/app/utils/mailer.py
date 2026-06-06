import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app
from jinja2 import Environment, FileSystemLoader

class Mailer:
    @staticmethod
    def send_email(to_email, subject, template_name, context, attachment_path=None, attachment_name=None):
        """
        Sends an HTML email with optional attachment using configuration values.
        """
        try:
            # Load config from current_app
            host = current_app.config.get("SMTP_SERVER_HOST", "localhost")
            port = int(current_app.config.get("SMTP_SERVER_PORT", 1025))
            username = current_app.config.get("SMTP_USERNAME")
            password = current_app.config.get("SENDER_PASSWORD")
            sender = current_app.config.get("SENDER_ADDRESS", "no-reply@mediflow.hms.org")
            
            # Setup templates path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            templates_dir = os.path.join(base_dir, "templates", "emails")
            
            # Ensure templates directory exists
            if not os.path.exists(templates_dir):
                os.makedirs(templates_dir, exist_ok=True)
                
            env = Environment(loader=FileSystemLoader(templates_dir))
            template = env.get_template(template_name)
            html_content = template.render(context)
            
            # Create message container
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = to_email
            
            # Attach HTML body
            part_html = MIMEText(html_content, 'html')
            msg.attach(part_html)
            
            # Handle attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part_attach = MIMEBase('application', 'octet-stream')
                    part_attach.set_payload(attachment.read())
                    encoders.encode_base64(part_attach)
                    
                    filename = attachment_name or os.path.basename(attachment_path)
                    part_attach.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    msg.attach(part_attach)
            
            # Send email
            with smtplib.SMTP(host, port) as server:
                if username and password:
                    server.login(username, password)
                server.sendmail(sender, to_email, msg.as_string())
                
            current_app.logger.info(f"Successfully sent email to {to_email} with subject '{subject}'")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
