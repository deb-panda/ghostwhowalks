import pandas as pd
import io
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_google_drive():
    """
    Authenticate and return Google Drive API service object.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def get_file_id_by_name(service, file_name):
    """
    Get file ID by searching for file name in Google Drive.
    
    Args:
        service: Google Drive API service object
        file_name: Name of the CSV file to search for
    
    Returns:
        File ID if found, None otherwise
    """
    try:
        # Search for files with the given name
        results = service.files().list(
            q=f"name='{file_name}' and mimeType='text/csv'",
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            print(f"No CSV file found with name: {file_name}")
            return None
        else:
            # Return the first match
            file_id = items[0]['id']
            print(f"Found file: {items[0]['name']} (ID: {file_id})")
            return file_id
            
    except Exception as error:
        print(f"An error occurred while searching for file: {error}")
        return None

def read_csv_from_google_drive(file_id=None, file_name=None):
    """
    Read a CSV file from Google Drive and return as pandas DataFrame.
    
    Args:
        file_id: Google Drive file ID (optional)
        file_name: Name of the CSV file to search for (optional)
        
    Returns:
        pandas DataFrame containing the CSV data
    """
    try:
        # Authenticate and get service
        service = authenticate_google_drive()
        
        # If file_name is provided but not file_id, search for the file
        if file_name and not file_id:
            file_id = get_file_id_by_name(service, file_name)
            if not file_id:
                return None
        
        if not file_id:
            raise ValueError("Either file_id or file_name must be provided")
        
        # Download the file content
        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        
        # Execute the request and get the file content
        downloader = request.execute()
        file_content.write(downloader)
        file_content.seek(0)
        
        # Read CSV content into pandas DataFrame
        df = pd.read_csv(file_content)
        
        print(f"Successfully loaded CSV file with shape: {df.shape}")
        return df
        
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def main():
    """
    Main function to demonstrate usage.
    """
    print("Google Drive CSV Reader")
    print("=" * 30)
    
    # Method 1: Using file ID (if you know it)
    # file_id = "your_file_id_here"
    # df = read_csv_from_google_drive(file_id=file_id)
    
    # Method 2: Using file name (searches Google Drive)
    file_name = input("Enter the CSV file name (including .csv extension): ")
    df = read_csv_from_google_drive(file_name=file_name)
    
    if df is not None:
        print("\nDataFrame Info:")
        print("-" * 20)
        print(df.info())
        
        print(f"\nFirst 5 rows:")
        print("-" * 20)
        print(df.head())
        
        print(f"\nDataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Optional: Save to local CSV
        save_local = input("\nSave to local CSV file? (y/n): ").lower().strip()
        if save_local == 'y':
            local_filename = input("Enter local filename (with .csv extension): ")
            df.to_csv(local_filename, index=False)
            print(f"Saved to {local_filename}")
    else:
        print("Failed to load the CSV file.")

if __name__ == "__main__":
    main()