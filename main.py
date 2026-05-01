import os
from typing import Any, Dict
import joblib
import pandas as pd
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)

class CustomerData(BaseModel):
    gender: str
    Partner: str
    Dependents: str
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaymentMethod: str
    tenure: int
    MonthlyCharges: float
    TotalCharges: float

MODEL_PATH = os.getenv("MODEL_PATH", "model_pipeline.pkl")
ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS_RAW.split(",") if o.strip()]
#Enviroments variables

app = FastAPI(
    title="Telco Churn API",
    version="1.0.0",
    description="A customer churn prediction API deployed on Render using FastAPI"
)
# Initialize the FastAPI application

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rocio7531.github.io"], # Configure CORS to allow requests from the frontend
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load the model from {MODEL_PATH}: {e}")
# Load the trained model

@app.get("/")
def home():
    return {"message": "API is up and running"}
# Simple endpoint to check if the API is running

@app.get("/health")
def health():
    return {"status": "ok", "model_path": MODEL_PATH}
# Health check endpoint for deployment (used by Render)

@app.post("/predict")
def predict(data: CustomerData): # FastAPI automatically interprets a dict as request body data
    try:
        df = pd.DataFrame([data.model_dump()]) ## Convert input data to a DataFrame as required by scikit-learn
# model_dump() converts the Pydantic object (CustomerData) into a dictionary
        probability = float(model.predict_proba(df)[:, 1][0]) #probabilidad de churn
        prediction = int(probability >= 0.30)

        logging.info("Prediction request received")
        logging.info(f"Prediction: {prediction}, Probability: {probability}")

        return {
            "prediction": prediction,
            "churn_probability": probability
        }
    except Exception as e:
        logging.exception("Prediction_failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
