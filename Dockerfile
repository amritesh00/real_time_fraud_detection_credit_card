FROM python:3.9-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

# Verify model exists
RUN test -f model.joblib && echo "Model verification passed" || (echo "Model file missing!" && exit 1)

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]