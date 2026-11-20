import pickle
import pandas as pd
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# LOAD TRAINED MODEL
BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "benzene_model.pkl", "rb") as f:
    model_data = pickle.load(f)

model = model_data["model"]
features = model_data["features"]
threshold = model_data["threshold"]
high_level = model_data["high_level"]

# CREATE FASTAPI APP
app = FastAPI(title="Air Quality Prediction System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# INPUT DATA
class AirQualityInput(BaseModel):
    PT08_S1_CO: float
    PT08_S3_NOx: float
    PT08_S4_NO2: float
    PT08_S5_O3: float
    Temperature: float
    Relative_Humidity: float
    Absolute_Humidity: float
    C6H6_lag1: float
    C6H6_lag2: float
    C6H6_lag3: float
    C6H6_lag24: float
    hour: int
    actual_benzene: Optional[float] = None


# HOME PAGE
@app.get("/")
def home():
    return {"message": "Air Quality Prediction API is running"}


# PREDICTION
@app.post("/predict")
def predict_air_quality(data: AirQualityInput):

    input_data = {
        "PT08.S1(CO)": data.PT08_S1_CO,
        "PT08.S3(NOx)": data.PT08_S3_NOx,
        "PT08.S4(NO2)": data.PT08_S4_NO2,
        "PT08.S5(O3)": data.PT08_S5_O3,
        "T": data.Temperature,
        "RH": data.Relative_Humidity,
        "AH": data.Absolute_Humidity,
        "C6H6_lag1": data.C6H6_lag1,
        "C6H6_lag2": data.C6H6_lag2,
        "C6H6_lag3": data.C6H6_lag3,
        "C6H6_lag24": data.C6H6_lag24,
        "hour": data.hour
    }

    input_df = pd.DataFrame(
        [[input_data[feature] for feature in features]],
        columns=features
    )

    prediction = float(model.predict(input_df)[0])

    result = {
        "predicted_benzene": round(prediction, 3),
        "high_level": round(high_level, 3),
        "pollution_status": (
            "High Benzene Level"
            if prediction > high_level
            else "Normal Benzene Level"
        )
    }

    if data.actual_benzene is not None:
        residual = data.actual_benzene - prediction
        anomaly = abs(residual) > threshold

        result["actual_benzene"] = data.actual_benzene
        result["residual"] = round(residual, 3)
        result["anomaly_status"] = (
            "Unusual Reading Detected"
            if anomaly
            else "No Unusual Reading Detected"
        )
    else:
        result["anomaly_status"] = "Actual reading not provided"

    return result