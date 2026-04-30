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
#enviroments variables

app = FastAPI(
    title="Telco Churn API",
    version="1.0.0",
    description="API de predicción de churn desplegable en Render"
)
# Aca estoy creando la API

#if ALLOWED_ORIGINS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rocio7531.github.io"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
    # Aca uso CORS indicandole al navegador que el frontend tiene permiso para usar la API.
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"No se pudo cargar el modelo en {MODEL_PATH}: {e}")
# Aca cargo el modelo entrenado

@app.get("/")
def home():
    return {"message": "API funcionando"}
# si alguien entra a la API, le digo que está viva (Endpoint simple)

@app.get("/health")
def health():
    return {"status": "ok", "model_path": MODEL_PATH}
# Chequeo técnico para Render (Endpoint simple)

@app.post("/predict")
def predict(data: CustomerData): #FastAPI ya sabe que si es un dict --> viene del body, por eso no se escribe
    try:
        df = pd.DataFrame([data.model_dump()]) # convierto a dataframe porque sklearn espera eso. 
        #model_dump() convierte el objeto (CustomerData) en un diccionario
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
