import zipfile
import os
import pandas as pd

# Define paths
zip_path = "../dataset/archive.zip"  # Make sure this matches your zip filename
extract_path = "../dataset/"
csv_filename = "AviationData.csv" # The specific file inside the zip we want

def inspect_dataset():
    # --- STEP 1: UNZIP THE DATA ---
    print(f"📦 Attempting to unzip: {zip_path}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List files inside to confirm we have the right one
            files_inside = zip_ref.namelist()
            print(f"   Files found inside zip: {files_inside}")
            
            # Extract only if not already extracted
            if not os.path.exists(os.path.join(extract_path, csv_filename)):
                zip_ref.extractall(extract_path)
                print(f"✅ Extracted files to {extract_path}")
            else:
                print(f"ℹ️ File already extracted.")
    except FileNotFoundError:
        print(f"❌ Error: Could not find {zip_path}. Check the filename.")
        return

    # --- STEP 2: LOAD AND INSPECT ---
    csv_path = os.path.join(extract_path, csv_filename)
    print(f"\nExample: Loading {csv_filename} to understand structure...")
    
    # 'latin-1' or 'ISO-8859-1' is often needed for NTSB data due to special characters
    try:
        df = pd.read_csv(csv_path, encoding='latin-1', low_memory=False)
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return

    # --- STEP 3: THE REPORT ---
    print("\n" + "="*40)
    print("📊 DATASET AUDIT REPORT")
    print("="*40)
    
    # Basic Stats
    print(f"Total Rows (Accidents): {df.shape[0]}")
    print(f"Total Columns: {df.shape[1]}")
    
    print("\n🔍 COLUMN CHECK (First 10 Columns):")
    print(df.columns[:10].tolist())
    
    print("\n⚠️ MISSING DATA CHECK (Top 5 emptiest columns):")
    # Show which columns are mostly empty (Critical for knowing what to drop)
    missing_counts = df.isnull().sum().sort_values(ascending=False).head(5)
    print(missing_counts)
    
    print("\n👀 SNEAK PEEK (First row):")
    # Transpose the first row so it's easier to read vertically
    print(df.head(1).T)
    
    print("\n✅ VITAL STATS:")
    # Check specific columns we plan to use
    print(f"Unique Aircraft Makes: {df['Make'].nunique()}")
    print(f"Accidents with Location Data (Lat/Lon): {df['Latitude'].notnull().sum()}")
    
    # Check unique values in the 'Injury.Severity' column to understand the targets
    if 'Injury.Severity' in df.columns:
        print("\n🏥 INJURY TYPES FOUND:")
        print(df['Injury.Severity'].unique()[:5]) # Show first 5 unique values

if __name__ == "__main__":
    inspect_dataset()