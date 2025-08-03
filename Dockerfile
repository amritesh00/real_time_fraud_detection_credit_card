FROM python:3.9-slim

WORKDIR /app

# 1. Install dependencies first (optimized for caching)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy ALL app files (including the pre-generated model)
COPY app .

# 3. Health check verification
RUN python -c "
import joblib
try:
    joblib.load('model.joblib')
    print('✓ Model loaded successfully')
except Exception as e:
    print(f'✗ Model loading failed: {e}')
    raise
"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]