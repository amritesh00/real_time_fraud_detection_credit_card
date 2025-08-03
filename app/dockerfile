# Stage 1: Builder
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim

# Security setup
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 wget && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m appuser

WORKDIR /app

# Copy from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser . .

# Download data and notebook
RUN mkdir -p notebooks && \
    wget https://raw.githubusercontent.com/nsethi31/Kaggle-Data-Credit-Card-Fraud-Detection/master/creditcard.csv -O notebooks/creditcard.csv && \
    chown appuser notebooks/creditcard.csv

# Train model
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"
RUN python -c "\
from sklearn.ensemble import IsolationForest; \
import numpy as np; \
import joblib; \
joblib.dump(IsolationForest(random_state=42).fit(np.random.rand(1000, 30)), 'model.joblib')"

# Healthcheck and run
HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]