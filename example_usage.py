#!/usr/bin/env python3
"""
Example usage of the Google Drive CSV Reader
"""

from google_drive_csv_reader import read_csv_from_google_drive

def example_1_by_filename():
    """Example: Read CSV by filename"""
    print("Example 1: Reading CSV by filename")
    print("-" * 40)
    
    # Replace with your actual CSV filename
    filename = "sample_data.csv"  # Change this to your CSV file name
    
    df = read_csv_from_google_drive(file_name=filename)
    
    if df is not None:
        print(f"Successfully loaded '{filename}'")
        print(f"Shape: {df.shape}")
        print("\nFirst 3 rows:")
        print(df.head(3))
        print("\nColumn names:")
        print(list(df.columns))
    else:
        print(f"Failed to load '{filename}'")
    
    print("\n" + "="*50 + "\n")

def example_2_by_file_id():
    """Example: Read CSV by file ID"""
    print("Example 2: Reading CSV by file ID")
    print("-" * 40)
    
    # Replace with your actual file ID
    # You can get this from the Google Drive URL or by searching first
    file_id = "your_file_id_here"  # Change this to your actual file ID
    
    # Uncomment the next line and comment out the return to test
    # df = read_csv_from_google_drive(file_id=file_id)
    
    print("Note: Replace 'your_file_id_here' with actual file ID to test this example")
    return
    
    if df is not None:
        print(f"Successfully loaded file with ID: {file_id}")
        print(f"Shape: {df.shape}")
        print("\nDataFrame info:")
        df.info()
    else:
        print(f"Failed to load file with ID: {file_id}")
    
    print("\n" + "="*50 + "\n")

def example_3_data_analysis():
    """Example: Basic data analysis after loading"""
    print("Example 3: Basic data analysis")
    print("-" * 40)
    
    # Replace with your actual CSV filename
    filename = "sample_data.csv"  # Change this to your CSV file name
    
    df = read_csv_from_google_drive(file_name=filename)
    
    if df is not None:
        print("Basic Data Analysis:")
        print(f"• Dataset shape: {df.shape}")
        print(f"• Column count: {len(df.columns)}")
        print(f"• Row count: {len(df)}")
        
        print("\nColumn types:")
        print(df.dtypes)
        
        print("\nBasic statistics for numeric columns:")
        print(df.describe())
        
        print("\nMissing values:")
        print(df.isnull().sum())
        
        # Example: Filter data (modify based on your CSV structure)
        print("\nSample operations:")
        print("- First 2 rows:", df.head(2).to_dict('records'))
        
    else:
        print(f"Failed to load '{filename}' for analysis")

if __name__ == "__main__":
    print("Google Drive CSV Reader - Usage Examples")
    print("=" * 50)
    
    # Run examples
    try:
        example_1_by_filename()
        # example_2_by_file_id()  # Uncomment to test
        # example_3_data_analysis()  # Uncomment to test
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("\nMake sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Set up credentials.json file")
        print("3. Updated the filename/file_id in the examples")