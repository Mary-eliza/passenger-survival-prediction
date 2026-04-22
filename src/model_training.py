import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

def train_risk_model():
    print("[INFO] Loading Cleaned Data...")
    try:
        df = pd.read_csv("../dataset/clean_model_data.csv")
    except FileNotFoundError:
        print("[ERROR] 'clean_model_data.csv' not found.")
        return

    # --- 1. Create Risk Classes (The Pivot) ---
    # Instead of predicting exact %, we predict classes:
    # 0 = Critical Risk (Survival < 20%)
    # 1 = Moderate Risk (Survival 20% - 80%)
    # 2 = High Chance of Survival (> 80%)
    
    def get_risk_category(rate):
        if rate > 0.80: return 2 # Safe
        if rate < 0.20: return 0 # Danger
        return 1 # Uncertain

    df['Risk_Class'] = df['Survival_Rate'].apply(get_risk_category)

    # --- 2. Handling Rare Manufacturers ---
    print("[INFO] Grouping rare manufacturers...")
    make_counts = df['Make'].value_counts()
    common_makes = make_counts[make_counts >= 10].index
    df['Make_Grouped'] = df['Make'].apply(lambda x: x if x in common_makes else 'OTHER')
    
    # --- 3. Encoding ---
    print("[INFO] Encoding features...")
    le_make = LabelEncoder()
    le_phase = LabelEncoder()
    le_weather = LabelEncoder()
    
    df['Make_Code'] = le_make.fit_transform(df['Make_Grouped'].astype(str))
    df['Phase_Code'] = le_phase.fit_transform(df['Broad.Phase.of.Flight'].astype(str))
    df['Weather_Code'] = le_weather.fit_transform(df['Weather.Condition'].astype(str))
    
    # --- 4. Train/Test Split ---
    features = ['Make_Code', 'Phase_Code', 'Weather_Code', 'Number.of.Engines', 'Month']
    target = 'Risk_Class'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # --- 5. Train Random Forest Classifier ---
    print(f"[INFO] Training Classifier on {len(X_train)} flights...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # --- 6. Evaluation ---
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    
    print("-" * 30)
    print("MODEL UPGRADED TO CLASSIFIER!")
    print(f"Accuracy Score: {acc*100:.2f}%") # Expecting 80%+
    print("-" * 30)
    
    # --- 7. Save Artifacts ---
    artifacts = {
        "model": model,
        "le_make": le_make,
        "le_phase": le_phase,
        "le_weather": le_weather,
        "common_makes": list(common_makes),
        "model_type": "classifier" # Tagging this so App knows
    }
    
    joblib.dump(artifacts, "../models/risk_model.pkl") # Save as one file for simplicity
    print("[SUCCESS] Optimized Model saved to /models/")

if __name__ == "__main__":
    train_risk_model()