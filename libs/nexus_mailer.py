import os
import sys

# Ensure UTF-8 output for CLI
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from .gmail import send_email

# Absolute path to the template file
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'email', 'standard_template.html')

def send_templated_email(to, subject, title, recipient_name, message_body, cta_text="View Updates", cta_link="https://github.com/agent2201/printivo", attachment_path=None):
    """
    Sends a styled email using the Printivo HTML template.
    """
    try:
        if not os.path.exists(TEMPLATE_PATH):
            raise FileNotFoundError(f"Email template not found at {TEMPLATE_PATH}")

        # Read the template
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Replace placeholders
        # Note: We use .replace() for simplicity, but Jinja2 would be better for complex logic
        replacements = {
            '{{subject}}': subject,
            '{{title}}': title,
            '{{recipient_name}}': recipient_name,
            '{{message_body}}': message_body,
            '{{cta_text}}': cta_text,
            '{{cta_link}}': cta_link
        }

        html_body = template_content
        for key, value in replacements.items():
            html_body = html_body.replace(key, str(value))

        # Send using the existing gmail.py functionality
        success = send_email(to, subject, html_body, file_path=attachment_path)
        
        if success:
            print(f"Templated email '{subject}' sent successfully to {to}")
        return success

    except Exception as e:
        print(f"Error in nexus_mailer: {e}")
        return False

if __name__ == "__main__":
    # Example usage (test mode)
    # To test, uncomment and run: python -m libs.nexus_mailer
    # send_templated_email(
    #     to="your-email@example.com",
    #     subject="NEXUS: New Asset Uploaded",
    #     title="New Media Ready for Review",
    #     recipient_name="Eugene",
    #     message_body="The latest video render (HEVC Alpha) has been successfully uploaded to the MinIO storage. You can access it via the dashboard.",
    #     cta_text="Open Dashboard"
    # )
    pass
