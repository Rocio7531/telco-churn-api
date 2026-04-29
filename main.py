import os
from typing import Any, Dict

import joblib
import pandas as pd
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
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
def predict(
    data: Dict[str, Any] = Body(
        ...,
        example={
            "gender": "Female",
            "Partner": "Yes",
            "Dependents": "No",
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "Yes",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Month-to-month",
            "PaymentMethod": "Electronic check",
            "tenure": 5,
            "MonthlyCharges": 70.5,
            "TotalCharges": 350.2
        }
    ) # Endpoint importante: recibo datos --> hago una predicción
):
    try:
        df = pd.DataFrame([data]) # convierto a dataframe porque sklearn espera eso
        probability = float(model.predict_proba(df)[:, 1][0]) #probabilidad de churn
        prediction = int(probability >= 0.30)

        return {
            "prediction": prediction,
            "churn_probability": probability
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
