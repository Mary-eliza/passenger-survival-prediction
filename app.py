from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# --- 1. Load the "AeroSafe" Brain ---
print("⏳ Loading AI Model & Artifacts...")
try:
   artifacts = joblib.load('models/risk_model.pkl')

   model = artifacts['model']
   le_make = artifacts['le_make']
   le_phase = artifacts['le_phase']
   le_weather = artifacts['le_weather']
   common_makes = artifacts['common_makes']   

   print("✅ Model Loaded Successfully!")


except Exception as e:
   print(f"❌ CRITICAL ERROR: Could not load model. {e}")
# We don't exit, so the server can still start (but prediction won't work)

# --- 2. Load Map Data (For the 3D Globe) ---
try:
    map_data = pd.read_csv("dataset/clean_map_data.csv")
    # We limit to 2000 points so the browser doesn't freeze
    map_data = map_data[['Latitude', 'Longitude', 'Make', 'Survival_Rate']].dropna().head(2000)
    print(f"✅ Map Data Loaded ({len(map_data)} points)")
except Exception as e:
    print(f"⚠️ Warning: Map data missing. {e}")
    map_data = pd.DataFrame()

@app.route('/')
def home():
    """Renders the main dashboard"""

    makes = sorted(list(common_makes))
    phases = sorted(list(le_phase.classes_))
    weathers = sorted(list(le_weather.classes_))

    return render_template(
        'index.html',
        makes=makes,
        phases=phases,
        weathers=weathers
    )

@app.route("/scope")
def scope():
    return render_template("scope.html")


@app.route("/team")
def team():
    return render_template("team.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/api/predict', methods=['POST'])
def predict():
    """Handles prediction requests"""
    try:
        # 3. Encode Inputs (Text -> Numbers)
        make_input = request.json.get('make')
        phase_input = request.json.get('phase')
        weather_input = request.json.get('weather')
        engines = request.json.get('engines')
        month = request.json.get('month')

        make_code = le_make.transform([make_input])[0]
        phase_code = le_phase.transform([phase_input])[0]
        weather_code = le_weather.transform([weather_input])[0]
        
        # 4. Predict Probabilities
        features = [[make_code, phase_code, weather_code, engines, month]]
        
        # model.predict_proba returns [Prob_Class_0, Prob_Class_1, Prob_Class_2]
        # Class 0 = Critical Risk, Class 1 = Moderate, Class 2 = Safe
        probs = model.predict_proba(features)[0]

        # 5. Calculate "Safety Score" (0 to 100)
        # We give 100 points for "Safe" probability and 50 points for "Moderate"
        safety_score = (probs[2] * 100) + (probs[1] * 50)

        return jsonify({
            'success': True,
            'safety_score': round(safety_score, 1),
            'risk_level': get_risk_label(safety_score),
            'breakdown': {
                'critical': round(probs[0] * 100, 1),
                'moderate': round(probs[1] * 100, 1),
                'safe': round(probs[2] * 100, 1)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/map_data')
def get_map_data():
    """Sends coordinates to the frontend map"""
    return jsonify(map_data.to_dict(orient='records'))

# --- 4. Result Page Route ---

@app.route('/result')
def result():

    score = request.args.get("score")
    risk = request.args.get("risk")

    critical = request.args.get("critical")
    moderate = request.args.get("moderate")
    safe = request.args.get("safe")

    suggestion = request.args.get("suggestion")

    return render_template(
       "result.html",
       score=score,
       risk=risk,
       critical=critical,
       moderate=moderate,
       safe=safe,
       suggestion=suggestion
   )

# --- 5. Risk Label Function ---

def get_risk_label(score):
    if score >= 80: return "HIGH SURVIVABILITY"
    if score >= 50: return "MODERATE RISK"
    return "CRITICAL DANGER"
# --- 6. Run Server ---

if __name__ == '__main__':
    app.run(debug=True, port=5000)