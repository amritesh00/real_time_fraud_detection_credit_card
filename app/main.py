from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import joblib
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(middleware=[TrustedHostMiddleware(allowed_hosts=["*"])])
app.state.limiter = limiter

# Load model
MODEL_PATH = "model.joblib"
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Model loaded successfully")
except Exception as e:
    logging.error(f"Model loading failed: {str(e)}")
    raise

@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, transaction: dict):
    """Sample input: {"amount": 100, "time": 50000, "v1": -0.5, ..., "v28": 0.2}"""
    try:
        features = [transaction["amount"], transaction["time"]] + [
            transaction[f"v{i}"] for i in range(1, 29)
        ]
        prediction = model.predict([features])[0]
        logging.info(f"Prediction made for transaction: {transaction['amount']}")
        return {
            "is_fraud": bool(prediction == -1),
            "confidence": float(np.abs(model.score_samples([features])[0])),
            "model_version": "v1.0"
        }
    except KeyError as e:
        logging.warning(f"Missing feature: {e}")
        raise HTTPException(status_code=400, detail=f"Missing feature: {e}")
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def health_check():
    return {
        "status": "OK",
        "model_loaded": Path(MODEL_PATH).exists(),
        "version": "v1.0"
    }

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logging.warning(f"Rate limit exceeded: {request.client.host}")
    return HTTPException(
        status_code=429,
        detail="Too many requests"
    )