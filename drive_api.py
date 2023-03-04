from __future__ import print_function

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import io
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

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


def export_pdf(real_file_id, name):
    try:
        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        filename = 'resumes/' + name + '.pdf'
        file = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return


# Specify the path of the folder
folder_path = '/Resume Drive/Resume Drive'

# Split the path into individual folder names
folder_names = folder_path.strip('/').split('/')

# Initialize variables
folder_id = 'root'
found = False

try:
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

    # Replace the values with your credentials and folder ID
    FOLDER_ID = folder_id

    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false", fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found in the folder.')
    else:
        print('Files:')
        for item in items:
            print(f'{item["name"]} ({item["id"]})')
            export_pdf(item["id"], item["name"])


except HttpError as e:
    print(e)
