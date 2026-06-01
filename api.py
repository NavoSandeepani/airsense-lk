from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import xgboost as xgb
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import uvicorn

# ── app setup ──────────────────────────────────────────────
app = FastAPI(
    title="AirSense LK — Air Quality Prediction API",
    description="Predicts AQI for Sri Lankan cities using real-time data",
    version="1.0.0"
)

engine = create_engine("sqlite:///data/airsense.db")

FEATURE_COLS = [
    'pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2',
    'temperature', 'humidity', 'wind_speed',
    'hour', 'day_of_week', 'is_rush_hour', 'is_night',
    'pm25_3hr_avg', 'pm25_24hr_avg', 'aqi_6hr_avg',
    'pm25_change', 'aqi_change'
]

AQI_LABELS = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor"
}

AQI_ADVICE = {
    1: "Air quality is good. Enjoy outdoor activities freely.",
    2: "Air quality is acceptable. Sensitive people should consider reducing outdoor activity.",
    3: "Moderate pollution. Sensitive groups should reduce prolonged outdoor activity.",
    4: "Poor air quality. Everyone should reduce outdoor activity. Wear a mask outside.",
    5: "Very poor air quality. Avoid all outdoor activity. Keep windows closed."
}

AQI_COLOR = {
    1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🟣"
}

# ── load model at startup ───────────────────────────────────
print("Loading model from MLflow registry...")
try:
    MODEL_PATH = "/app/mlruns/1/models/m-1a8153dd90794bad9222bf43061daf44/artifacts/model.ubj"
    model = xgb.Booster()
    model.load_model(MODEL_PATH)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Model load failed: {e}")
    model = None

# ── helper ──────────────────────────────────────────────────
def get_latest_city_features(city: str):
    query = f"""
        SELECT * FROM air_quality_features
        WHERE city = '{city}'
        ORDER BY timestamp DESC
        LIMIT 1
    """
    df = pd.read_sql(query, engine)
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for city: {city}. Available: Colombo, Kandy, Galle, Jaffna"
        )
    return df.iloc[0]

# ── request / response models ───────────────────────────────
class PredictRequest(BaseModel):
    city: str

    model_config = {
        "json_schema_extra": {
            "example": {"city": "Colombo"}
        }
    }

class PredictResponse(BaseModel):
    city: str
    timestamp: str
    current_aqi: int
    current_aqi_label: str
    predicted_aqi: int
    predicted_aqi_label: str
    color_indicator: str
    main_pollutant: str
    advice: str
    pm2_5: float
    pm10: float
    temperature: float
    humidity: float

# ── endpoints ───────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/cities")
def get_cities():
    return {
        "cities": ["Colombo", "Kandy", "Galle", "Jaffna"],
        "description": "Send any of these city names to /predict"
    }

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    row = get_latest_city_features(request.city)

    # prepare features
    features_df = pd.DataFrame([row[FEATURE_COLS]])
    dmatrix = xgb.DMatrix(features_df)

    # predict — booster returns raw scores, get class
    pred = model.predict(dmatrix)
    predicted_class = int(round(float(pred[0]))) + 1
    predicted_class = max(1, min(5, predicted_class))

    # find main pollutant
    pollutants = {
        "PM2.5": float(row['pm2_5']),
        "PM10":  float(row['pm10']),
        "CO":    float(row['co']) / 100,
        "NO2":   float(row['no2']),
        "O3":    float(row['o3'])
    }
    main_pollutant = max(pollutants, key=pollutants.get)

    return PredictResponse(
        city=request.city,
        timestamp=str(row['timestamp']),
        current_aqi=int(row['aqi']),
        current_aqi_label=AQI_LABELS.get(int(row['aqi']), "Unknown"),
        predicted_aqi=predicted_class,
        predicted_aqi_label=AQI_LABELS.get(predicted_class, "Unknown"),
        color_indicator=AQI_COLOR.get(predicted_class, "⚪"),
        main_pollutant=main_pollutant,
        advice=AQI_ADVICE.get(predicted_class, "No advice available"),
        pm2_5=round(float(row['pm2_5']), 2),
        pm10=round(float(row['pm10']), 2),
        temperature=round(float(row['temperature']), 1),
        humidity=round(float(row['humidity']), 1)
    )

@app.get("/history/{city}")
def get_history(city: str, hours: int = 24):
    query = f"""
        SELECT timestamp, city, aqi, pm2_5, pm10, temperature, humidity
        FROM air_quality
        WHERE city = '{city}'
        ORDER BY timestamp DESC
        LIMIT {hours}
    """
    df = pd.read_sql(query, engine)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {city}")
    return {
        "city": city,
        "hours_requested": hours,
        "readings": df.to_dict(orient="records")
    }

# ── run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)