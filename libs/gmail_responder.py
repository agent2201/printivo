import time
import base64
import sys
import os
from email.mime.text import MIMEText
from googleapiclient.discovery import build

# Ensure current and parent dirs are in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.google_tasks import get_google_creds

# Trusted customers to auto-respond to
TRUSTED_EMAILS = [
    "yurarulev@gmail.com",
    "eugenetarget8@gmail.com",
    "larichevaanya@gmail.com"
]

def check_and_respond():
    """Poll Gmail for unread messages from trusted emails and send auto-replies."""
    try:
        creds = get_google_creds()
        service = build('gmail', 'v1', credentials=creds)
        
        # Search query: Unread messages from trusted emails
        query = "is:unread (" + " OR ".join([f"from:{email}" for email in TRUSTED_EMAILS]) + ")"
        
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print(f"[{time.strftime('%H:%M:%S')}] No new messages found.")
            return

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data['payload']['headers']
            
            # Extract basic info
            sender = next(h['value'] for h in headers if h['name'] == 'From')
            subject = next(h['value'] for h in headers if h['name'] == 'Subject')
            
            print(f"[{time.strftime('%H:%M:%S')}] New message from {sender}: {subject}")
            
            # 1. Create Reply
            reply_text = f"<b>NEXUS Printivo Auto-Reply:</b><br><br>Здравствуйте! Ваше сообщение по заказу \"{subject}\" получено и передано в систему управления производством.<br>Мы свяжемся с вами в ближайшее время."
            
            reply_headers = {
                'to': sender,
                'subject': f"Re: {subject}",
                'threadId': msg['threadId'] # Keep it in the same thread!
            }
            
            message = MIMEText(reply_text, 'html')
            message['to'] = reply_headers['to']
            message['subject'] = reply_headers['subject']
            
            raw_msg = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode(), 'threadId': msg['threadId']}
            
            # 2. Send Reply
            service.users().messages().send(userId='me', body=raw_msg).execute()
            print(f"Auto-Reply sent to {sender}.")
            
            # 3. Mark as READ (Remove 'UNREAD' label)
            service.users().messages().batchModify(
                userId='me', 
                body={'ids': [msg['id']], 'removeLabelIds': ['UNREAD']}
            ).execute()
            
    except Exception as e:
        print(f"An error occurred in Gmail Responder: {e}")

if __name__ == '__main__':
    # Force UTF-8 for all console output
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("NEXUS Auto-Responder: Active Monitor Running...")
    while True:
        check_and_respond()
        time.sleep(10) # Speeding up check to 10s for the test
