# Dependency Builder 
FROM python:3.11-slim as BUILDER 

WORKDIR /build

# Copies dependency files only first, only re-run when pyproject.toml changes
COPY pyproject.toml .
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --target /install

# Runtime Image
FROM python:3.11-slim as runtime 

# Create non-root user
RUN adduser --disabled-password --gecos "" --uid 1001 appuser

WORKDIR /app

# Copies installed packages from builder, pip is not used in the runtime image 
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# Copies application code
COPY api/ ./api/

# Copy model artifacts 
COPY model/artifacts/ ./model/artifacts/

# Sets ownership before switching user
RUN chown -R appuser:appuser/app

USER appuser

ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/app/model/artifacts/model.joblib \
    LABELS_PATH=/app/model/artifacts/labels.joblib \
    REDIS_URL=redis://redis:6379 \
    WORKERS=2

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS}"]