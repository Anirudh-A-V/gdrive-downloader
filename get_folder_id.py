from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# Authenticate and build the Drive API client
# creds = Credentials.from_authorized_user_file('token.json', SCOPES)
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
service = build('drive', 'v3', credentials=creds)

# Specify the path of the folder
folder_path = '/Resume Drive/Resume Drive'

# Split the path into individual folder names
folder_names = folder_path.strip('/').split('/')

# Initialize variables
folder_id = 'root'
found = False

# Traverse the folder structure to find the target folder
for folder_name in folder_names:
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + \
        folder_name + "' and '" + folder_id + "' in parents"
    results = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if len(items) == 0:
        print('Folder not found: ' + folder_path)
        break
    else:
        for item in items:
            if item['name'] == folder_name:
                folder_id = item['id']
                found = True
                break
        if not found:
            print('Folder not found: ' + folder_path)
            break

print('Folder ID: ' + folder_id)
