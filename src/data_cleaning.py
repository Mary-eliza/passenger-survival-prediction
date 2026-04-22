import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

def load_and_clean_data(filepath):
    print("⏳ Loading Dataset...")
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=False)
    
    # --- FIX: Standardize Column Names ---
    # This turns "Broad.phase.of.flight" into "Broad.Phase.of.Flight" 
    # so the rest of the script works perfectly.
    df.columns = df.columns.str.strip() # Remove spaces
    
    # Map specifically to the names we expect, just in case
    column_mapping = {
        'Broad.phase.of.flight': 'Broad.Phase.of.Flight',
        'Weather.condition': 'Weather.Condition'
    }
    df = df.rename(columns=column_mapping)
    
    # -------------------------------------

    # 1. Filter by Year (Modern Era Only)
    df['Event.Date'] = pd.to_datetime(df['Event.Date'], errors='coerce')
    df = df[df['Event.Date'].dt.year >= 1990]
    print(f"📉 Filtered to post-1990 data. Remaining rows: {len(df)}")

    # 2. Fix the "Numbers" (Fill NaNs with 0)
    injury_cols = ['Total.Fatal.Injuries', 'Total.Serious.Injuries', 'Total.Minor.Injuries', 'Total.Uninjured']
    # Check if columns exist before filling
    for col in injury_cols:
        if col not in df.columns:
            df[col] = 0
            
    df[injury_cols] = df[injury_cols].fillna(0)
    
    # 3. Calculate Target: Survival Rate
    df['Total_Aboard'] = df[injury_cols].sum(axis=1)
    df = df[df['Total_Aboard'] > 0] # Drop empty planes
    
    df['Survival_Rate'] = (df['Total.Uninjured'] + df['Total.Minor.Injuries']) / df['Total_Aboard']
    
    # 4. Standardize Critical Text Columns
    # We use the corrected column name here
    if 'Broad.Phase.of.Flight' in df.columns:
        df['Broad.Phase.of.Flight'] = df['Broad.Phase.of.Flight'].str.upper().fillna('UNKNOWN')
    else:
        # Fallback if the column name is still weird
        print(f"⚠️ Warning: Could not find 'Broad.Phase.of.Flight'. Available columns: {df.columns.tolist()[:10]}")
        return

    df['Make'] = df['Make'].str.upper().str.strip()
    df['Model'] = df['Model'].str.upper().str.strip()
    df['Weather.Condition'] = df['Weather.Condition'].str.upper().fillna('UNK')
    
    # 5. Save "Map Data" (Only rows with Lat/Lon)
    # Ensure Lat/Lon are numeric
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    
    map_cols = ['Event.Date', 'Make', 'Model', 'Latitude', 'Longitude', 'Survival_Rate', 'Location']
    map_df = df.dropna(subset=['Latitude', 'Longitude'])[map_cols]
    map_df.to_csv("../dataset/clean_map_data.csv", index=False)
    print(f"🗺️  Saved {len(map_df)} rows for the Interactive Map.")

    # 6. Save "Model Data" (Rows with good Predictive Features)
    model_cols = [
        'Make', 'Model', 'Number.of.Engines', 'Engine.Type',
        'Broad.Phase.of.Flight', 'Weather.Condition', 
        'Total_Aboard', 'Survival_Rate', 'Event.Date'
    ]
    
    # Check if all model columns exist
    missing_cols = [c for c in model_cols if c not in df.columns]
    if missing_cols:
        print(f"❌ Error: Missing columns for model: {missing_cols}")
        return

    model_df = df.dropna(subset=['Number.of.Engines', 'Broad.Phase.of.Flight'])
    
    # Basic Feature Engineering for Model
    model_df['Month'] = model_df['Event.Date'].dt.month
    
    model_df.to_csv("../dataset/clean_model_data.csv", index=False)
    print(f"🤖 Saved {len(model_df)} rows for AI Training.")

if __name__ == "__main__":
    load_and_clean_data("../dataset/AviationData.csv")