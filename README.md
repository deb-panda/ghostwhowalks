# Google Drive CSV Reader

A Python script that reads CSV files from Google Drive and displays them as pandas DataFrames.

## Features

- Authenticate with Google Drive API
- Search for CSV files by name or use direct file ID
- Read CSV content into pandas DataFrame
- Display DataFrame information and preview
- Optional: Save to local CSV file

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Google Drive API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click on it and press "Enable"

4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Give it a name (e.g., "Drive CSV Reader")
   - Download the JSON file

5. Rename the downloaded JSON file to `credentials.json` and place it in the same directory as the script

### 3. Run the Script

```bash
python google_drive_csv_reader.py
```

On first run, it will:
- Open your browser for Google authentication
- Ask for permission to read your Google Drive files
- Save authentication tokens for future use

## Usage Examples

### Method 1: Using File Name (Recommended)
```python
from google_drive_csv_reader import read_csv_from_google_drive

# Search by file name
df = read_csv_from_google_drive(file_name="my_data.csv")
print(df.head())
```

### Method 2: Using File ID
```python
from google_drive_csv_reader import read_csv_from_google_drive

# If you know the file ID
file_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
df = read_csv_from_google_drive(file_id=file_id)
print(df.head())
```

### Method 3: Interactive Mode
Simply run the script and follow the prompts:
```bash
python google_drive_csv_reader.py
```

## Functions

- `authenticate_google_drive()`: Handles Google Drive API authentication
- `get_file_id_by_name(service, file_name)`: Searches for a file by name and returns its ID
- `read_csv_from_google_drive(file_id=None, file_name=None)`: Main function to read CSV from Google Drive

## Security Notes

- The `credentials.json` file contains sensitive information. Do not share it or commit it to version control.
- The script only requests read-only access to your Google Drive.
- Authentication tokens are stored locally in `token.pickle` for convenience.

## Troubleshooting

### Common Issues

1. **"File not found" error**: Make sure the CSV file exists in your Google Drive and the name is correct.

2. **Authentication errors**: Delete `token.pickle` and run the script again to re-authenticate.

3. **Permission denied**: Ensure the Google Drive API is enabled in your Google Cloud project.

4. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`.

## File Structure

```
.
├── google_drive_csv_reader.py  # Main script
├── requirements.txt            # Python dependencies
├── credentials.json           # Google API credentials (you need to add this)
├── token.pickle              # Auto-generated authentication token
└── README.md                 # This file
```

## Requirements

- Python 3.7+
- Google account with access to Google Drive
- Google Cloud project with Drive API enabled