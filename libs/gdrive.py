import os
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.metadata.readonly']

def get_gdrive_service():
    """Shows basic usage of the Drive v3 API.
    Lists the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = 'token.pickle'
    creds_path = 'credentials.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Missing {creds_path} in project root.")
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def test_connection():
    """Verify Google Drive connection by listing the first 10 files."""
    try:
        service = get_gdrive_service()
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return False
        else:
            print('Files found in your Google Drive:')
            for item in items:
                print(f"{item['name']} ({item['id']})")
            return True
            
    except Exception as e:
        print(f"An error occurred during connection test: {e}")
        return False

def create_folder(folder_name, parent_id=None):
    """Create a folder on Google Drive."""
    try:
        service = get_gdrive_service()
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        file = service.files().create(body=file_metadata, fields='id').execute()
        print(f"Folder created: {folder_name} (ID: {file.get('id')})")
        return file.get('id')
    except Exception as e:
        print(f"An error occurred during folder creation: {e}")
        return None

def share_folder_with_anyone(file_id, role='reader'):
    """Make a folder/file accessible to anyone with the link."""
    try:
        service = get_gdrive_service()
        permission = {
            'type': 'anyone',
            'role': role
        }
        service.permissions().create(fileId=file_id, body=permission).execute()
        print(f"Access granted: Anyone with link can {role} this folder ({file_id})")
        return True
    except Exception as e:
        print(f"An error occurred during sharing: {e}")
        return False

def create_spreadsheet(name, parent_id=None):
    """Create a Google Spreadsheet in a specific folder."""
    try:
        service = get_gdrive_service()
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        file = service.files().create(body=file_metadata, fields='id').execute()
        spreadsheet_id = file.get('id')
        print(f"Spreadsheet created: {name} (ID: {spreadsheet_id})")
        return spreadsheet_id
    except Exception as e:
        print(f"An error occurred during spreadsheet creation: {e}")
        return None

if __name__ == '__main__':
    print("Initializing Google Drive Connection for Printivo...")
    test_connection()
