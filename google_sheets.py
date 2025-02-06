from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd
import numpy as np
import os.path
import pickle
from chip_config import ChipConfig


class GoogleSheetsUpload():
    def __init__(self):
        self.folder_id = ChipConfig().query('SETTINGS','google_sheets_folder_id') # Store folder ID when initializing the class
        
    def get_credentials(self):
        SCOPES = ['https://www.googleapis.com/auth/drive.file',
                  'https://www.googleapis.com/auth/spreadsheets']
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json',
                    SCOPES)
                creds = flow.run_local_server(port=0)
                
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def clean_data_for_sheets(self, data):
        if isinstance(data, (pd.DataFrame, pd.Series)):
            data = data.replace({np.nan: '', np.inf: '', -np.inf: ''})
            data = data.where(pd.notnull(data), '')
        return data

    def create_and_upload_spreadsheet(self, name_string):
        # Set up credentials
        credentials = self.get_credentials()
        
        # Create Drive and Sheets API services
        drive_service = build('drive', 'v3', credentials=credentials)
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        # Generate current timestamp for filename
        timestamp = datetime.now().strftime('%Y-%m-%d__%I:%M:%S_%p')
        spreadsheet_name = f'{name_string}__{timestamp}'
        
        # Create new spreadsheet
        spreadsheet = {
            'properties': {
                'title': spreadsheet_name
            }
        }
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        # Move the spreadsheet to the specified folder
        file = drive_service.files().get(fileId=spreadsheet_id,
                                    fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))
        
        # Move the file to the new folder
        drive_service.files().update(fileId=spreadsheet_id,
                                   addParents=self.folder_id,
                                   removeParents=previous_parents,
                                   fields='id, parents').execute()
        
        # Read CSV data
        df = self.clean_data_for_sheets(pd.read_csv("exports/"+name_string))
        
        # Prepare data for upload
        values = [df.columns.tolist()] + df.values.tolist()
        
        # Update spreadsheet with CSV data
        body = {
            'values': values
        }
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Spreadsheet created: {spreadsheet_name}")
        print(f"Spreadsheet ID: {spreadsheet_id}")
        print(f"Updated {result.get('updatedCells')} cells")
        print(f"File moved to specified folder successfully")
        return spreadsheet_id