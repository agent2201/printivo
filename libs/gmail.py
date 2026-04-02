import base64
import os
import pickle
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Expanded Scopes: Add GMAIL SEND
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/gmail.send' 
]

def get_google_creds():
    """Unified helper for Google Auth."""
    creds = None
    token_path = 'token.pickle'
    creds_path = 'credentials.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    # Check if we need to refresh or re-auth with new scopes
    if not creds or not creds.valid or not all(scope in creds.scopes for scope in SCOPES):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Missing {creds_path} in project root.")
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def create_message(to, subject, message_text):
    """Create an email message."""
    message = MIMEText(message_text, 'html')
    message['to'] = to
    # message['from'] = sender  # Gmail API uses 'me' automatically
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw.decode()}

def create_message_with_attachment(to, subject, message_text, file_path):
    """Create a message with an attachment."""
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject

    msg = MIMEText(message_text, 'html')
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file_path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    with open(file_path, 'rb') as fp:
        attachment = MIMEBase(main_type, sub_type)
        attachment.set_payload(fp.read())
        fp.close()

    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
    message.attach(attachment)

    raw = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw.decode()}

def send_email(to, subject, body, file_path=None):
    """Send an email using Gmail API, optionally with attachment."""
    try:
        creds = get_google_creds()
        service = build('gmail', 'v1', credentials=creds)
        
        if file_path:
            message = create_message_with_attachment(to, subject, body, file_path)
        else:
            message = create_message(to, subject, body)
            
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        
        print(f"Message Id: {sent_message['id']} successfully sent to {to}")
        return True
    except Exception as e:
        print(f"An error occurred during email sending: {e}")
        return False

if __name__ == '__main__':
    print("Testing Printivo Mail Delivery System...")
    # You can test it by running with your email
    # send_email("your-email@example.com", "NEXUS Test", "<b>Connected to Printivo server!</b>")
