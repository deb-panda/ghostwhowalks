# 🚀 How to Run the Google Drive CSV Reader

## ✅ Prerequisites (COMPLETED)
- ✅ Python 3.7+ installed
- ✅ Virtual environment created 
- ✅ Dependencies installed

## 📋 Step-by-Step Instructions

### Step 1: Set Up Google Drive API Credentials

**IMPORTANT**: You need to create a `credentials.json` file before running the script.

1. **Go to Google Cloud Console**: https://console.cloud.google.com/

2. **Create or Select Project**:
   - Click "Select a project" → "New Project"
   - Give it a name like "Drive CSV Reader"
   - Click "Create"

3. **Enable Google Drive API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click on it and press "Enable"

4. **Create Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - If prompted, configure OAuth consent screen first:
     - Choose "External"
     - Fill in Application name: "Drive CSV Reader"
     - Add your email in developer contact
     - Save and continue through all steps
   - Back to Credentials:
     - Choose "Desktop application"
     - Name: "Drive CSV Reader"
     - Click "Create"

5. **Download Credentials**:
   - Click the download button (⬇️) next to your OAuth 2.0 Client
   - Save the file as `credentials.json` in this directory

### Step 2: Run the Script

**Option A: Interactive Mode (Recommended for first-time users)**
```bash
source venv/bin/activate
python google_drive_csv_reader.py
```

**Option B: Programmatic Usage**
```bash
source venv/bin/activate
python example_usage.py
```

**Option C: Direct Function Call**
```bash
source venv/bin/activate
python -c "
from google_drive_csv_reader import read_csv_from_google_drive
df = read_csv_from_google_drive(file_name='your_file.csv')
print(df.head())
"
```

### Step 3: First-Time Authentication

When you run the script for the first time:

1. **Browser Opens**: Your browser will open automatically
2. **Sign In**: Sign in to your Google account
3. **Grant Permission**: Click "Allow" to grant access to Google Drive
4. **Success**: You'll see "The authentication flow has completed"
5. **Token Saved**: Authentication is saved in `token.pickle` for future use

### Step 4: Using the Script

**Method 1: Search by Filename**
- The script will ask: "Enter the CSV file name"
- Type the exact filename (e.g., "data.csv")
- The script searches your Google Drive

**Method 2: Use File ID**
- Get the file ID from the Google Drive URL
- Example URL: `https://drive.google.com/file/d/1ABC123xyz/view`
- File ID is: `1ABC123xyz`

## 🎯 What You'll See

```
Google Drive CSV Reader
==============================
Enter the CSV file name (including .csv extension): my_data.csv
Found file: my_data.csv (ID: 1ABC123xyz)
Successfully loaded CSV file with shape: (100, 5)

DataFrame Info:
--------------------
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 100 entries, 0 to 99
Data columns (total 5 columns):
 #   Column  Non-Null Count  Dtype  
---  ------  --------------  -----  
 0   Name    100 non-null    object 
 1   Age     100 non-null    int64  
 2   City    100 non-null    object 
 3   Score   100 non-null    float64
 4   Date    100 non-null    object 
dtypes: float64(1), int64(1), object(3)
memory usage: 4.0+ KB

First 5 rows:
--------------------
    Name  Age      City  Score        Date
0   John   25  New York   85.5  2023-01-01
1   Jane   30    London   92.0  2023-01-02
2    Bob   35     Paris   78.3  2023-01-03
3  Alice   28     Tokyo   91.7  2023-01-04
4  Charlie 22   Sydney   87.2  2023-01-05

DataFrame shape: (100, 5)
Columns: ['Name', 'Age', 'City', 'Score', 'Date']
```

## 🛠️ Troubleshooting

### Error: "credentials.json not found"
- Make sure you downloaded the credentials file from Google Cloud Console
- Rename it to exactly `credentials.json`
- Place it in the same directory as the script

### Error: "File not found in Google Drive"
- Check the filename is exact (case-sensitive)
- Ensure the file is actually in your Google Drive
- Try using the file ID instead

### Error: "Permission denied"
- Make sure Google Drive API is enabled in your project
- Re-authenticate by deleting `token.pickle` and running again

### Error: "Import errors"
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## 📁 Current Directory Structure
```
workspace/
├── venv/                          # Virtual environment
├── google_drive_csv_reader.py     # Main script
├── example_usage.py               # Usage examples
├── requirements.txt               # Dependencies
├── README.md                      # Detailed documentation
├── setup_guide.md                 # This file
└── credentials.json               # ← YOU NEED TO CREATE THIS
```

## 🎉 Ready to Go!

Once you have the `credentials.json` file, you can run:

```bash
source venv/bin/activate
python google_drive_csv_reader.py
```