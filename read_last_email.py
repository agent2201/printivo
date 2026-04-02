import sys
import os
import base64
from googleapiclient.discovery import build

# Add libs to path
sys.path.append(os.getcwd())
from libs.gmail import get_google_creds

def get_message_body(payload):
    """Recursively extract message body from payload."""
    if 'parts' in payload:
        for part in payload['parts']:
            body = get_message_body(part)
            if body:
                return body
    if 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    return None

if __name__ == '__main__':
    # Ensure UTF-8 output
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    try:
        creds = get_google_creds()
        service = build('gmail', 'v1', credentials=creds)
        
        # Search query: messages from eugenetarget8@gmail.com
        query = "from:eugenetarget8@gmail.com"
        results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("Писем от Евгения не найдено.")
            sys.exit(0)
            
        msg_id = messages[0]['id']
        msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Без темы')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Неизвестно')
        
        body = get_message_body(msg['payload'])
        
        print(f"--- ПОСЛЕДНЕЕ ПИСЬМО ОТ ЕВГЕНИЯ ---")
        print(f"Дата: {date}")
        print(f"Тема: {subject}")
        print(f"Текст:\n{body}")
        print(f"------------------------------------")
        
    except Exception as e:
        print(f"Ошибка при чтении почты: {e}")
