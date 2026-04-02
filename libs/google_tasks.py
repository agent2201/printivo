import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Unified SCOPES for all project features
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify', # NEW: GMAIL MODIFY (READ/WRITE)
    'https://www.googleapis.com/auth/tasks'  # NEW: GOOGLE TASKS
]

def get_google_creds():
    """Unified handler for all Google API credentials."""
    creds = None
    token_path = 'token.pickle'
    creds_path = 'credentials.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    # Check if we need to expand scopes
    if not creds or not creds.valid or not all(scope in creds.scopes for scope in SCOPES):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Missing {creds_path} in project root.")
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def create_task(title, notes=None):
    """Create a task in the default My Tasks list."""
    try:
        creds = get_google_creds()
        service = build('tasks', 'v1', credentials=creds)
        
        task = {
            'title': title,
            'notes': notes
        }
        
        result = service.tasks().insert(tasklist='@default', body=task).execute()
        print(f"Task created: {result.get('title')} (ID: {result.get('id')})")
        return result.get('id')
    except Exception as e:
        print(f"An error occurred during task creation: {e}")
        return None

if __name__ == '__main__':
    print("Testing Printivo Task Management System...")
    create_task("--PRINTIVO: SETUP PROJECT START", "Check for WooCommerce readiness.")
