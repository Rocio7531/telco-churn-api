import os
from typing import Any, Dict
import joblib
import pandas as pd
from fastapi import FastAPI, Header, HTTPException
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

API_KEY = os.getenv("API_KEY")
print("API KEY:", API_KEY)
# Aca obtengo una variable de entorno llamada API_KEY


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
def predict(
    data: dict, # FastAPI ya sabe que si es un dict --> viene del body, por eso no se escribe
    x_api_key: str = Header(...) # Headers le dice a FastAPI "este valor viene en los HEADERS del request"
):
    if  x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")
    
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
