# ml_server
 
A production-grade ML model serving platform built with **FastAPI**, **Docker**, and **Kubernetes**. Trains a text classification model via Jupyter notebooks, exposes it through a REST API with Redis prediction caching, and deploys to a Kubernetes cluster with Prometheus + Grafana observability.
 
---
 
## Architecture
 
```
Client / Postman
      │  HTTPS
AWS ALB / GCP Load Balancer
      │
Kubernetes Cluster (EKS / GKE)
  ┌──────────────────────────────────────────┐
  │  Ingress Controller (nginx)              │
  │       │                                  │
  │  FastAPI Service  (3 replicas)           │
  │  ┌─────────────┐  ┌────────────────────┐ │
  │  │  /predict   │  │  /health /metrics  │ │
  │  │  /batch     │  │  Prometheus scrape │ │
  │  └──────┬──────┘  └────────────────────┘ │
  │         │                                 │
  │  ┌──────▼──────┐  ┌────────────────────┐ │
  │  │    Redis    │  │  Model Store       │ │
  │  │    cache    │  │  (S3 / GCS)        │ │
  │  └─────────────┘  └────────────────────┘ │
  └──────────────────────────────────────────┘
        │  metrics
  Prometheus ──► Grafana
        │
  GitHub push ──► Actions ──► ECR ──► kubectl rollout
```
 
---
 
## Features
 
- **REST API** — `/predict`, `/batch`, and `/health` endpoints with full OpenAPI docs at `/docs`
- **Pydantic validation** — strict input/output schemas with automatic 422 error responses on bad input
- **Redis prediction cache** — SHA-256 input hashing with configurable TTL; cache hit/miss metrics exposed to Prometheus
- **Model versioning** — models identified by MD5 hash of artifact file; version returned in every prediction response
- **Multi-stage Docker build** — slim runtime image with no build tools or pip in production
- **Kubernetes deployment** — rolling updates with zero downtime, HorizontalPodAutoscaler (3–10 replicas on CPU > 70%)
- **CI/CD pipeline** — GitHub Actions: lint (ruff) → test (pytest) → build → push to ECR → kubectl rollout
- **Observability** — Prometheus instrumentation for request count, latency (p50/p95/p99), prediction confidence distribution, and cache hit rate
---
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| API | FastAPI, Pydantic v2, Uvicorn |
| Model | Scikit-learn, joblib |
| Caching | Redis |
| Containerization | Docker (multi-stage), docker-compose |
| Orchestration | Kubernetes (EKS / GKE), Helm |
| CI/CD | GitHub Actions, Amazon ECR |
| Observability | Prometheus, Grafana |
| Linting / Testing | ruff, pytest, httpx |
 
---
 
## Project Structure
 
```
ml_server/
├── model/
│   ├── notebooks/          # training, EDA, evaluation (Jupyter)
│   ├── train.py            # serializes model to artifacts/
│   ├── predict.py          # model-agnostic predict() interface
│   └── artifacts/          # .gitignore'd — stored in S3/GCS
├── api/
│   ├── main.py             # FastAPI app, routes, lifespan
│   ├── schemas.py          # Pydantic request/response models
│   ├── model_loader.py     # loads model once at startup
│   ├── cache.py            # Redis async prediction cache
│   ├── metrics.py          # Prometheus counters + histograms
│   └── config.py           # settings via pydantic-settings + .env
├── tests/
│   ├── test_api.py         # async API integration tests
│   ├── test_model.py       # model contract tests
│   └── conftest.py         # pytest fixtures
├── infra/
│   ├── k8s/                # Deployment, Service, HPA, Ingress manifests
│   └── terraform/          # EKS / GKE cluster provisioning
├── monitoring/
│   ├── prometheus.yml
│   └── grafana-dashboard.json
├── .github/workflows/
│   └── ci-cd.yml
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
 
---
 
## Local Setup
 
**Prerequisites:** Python 3.11+, Docker, Docker Compose
 
### 1. Clone and install
 
```bash
git clone https://github.com/tylerwu2/ml_server.git
cd ml_server
pip install -r requirements.txt
```
 
### 2. Train the model
 
```bash
python model/train.py
# artifacts saved to model/artifacts/
```
 
### 3. Run locally with Docker Compose
 
```bash
docker-compose up --build
```
 
This starts the FastAPI server, Redis, Prometheus, and Grafana.
 
| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| Prometheus metrics | http://localhost:8000/metrics |
| Grafana | http://localhost:3000 |
 
### 4. Test a prediction
 
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "The patient showed signs of recovery after treatment"}'
```
 
```json
{
  "label": "sci.med",
  "confidence": 0.91,
  "probabilities": { "sci.med": 0.91, "comp.graphics": 0.05, ... },
  "cached": false,
  "model_version": "a3f2c1b4"
}
```
 
---
 
## API Reference
 
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predict` | Single text classification |
| `POST` | `/batch` | Batch classification (up to 100 texts) |
| `GET` | `/health` | Liveness check — returns model + cache status |
| `GET` | `/metrics` | Prometheus scrape endpoint |
| `GET` | `/docs` | Auto-generated Swagger UI |
 
Full schema available at `/docs` when the server is running.
 
---
 
## Running Tests
 
```bash
pytest tests/ -v
```
 
Tests cover the `/predict` happy path, invalid input (422 validation), `/batch`, and `/health`. All tests run against the actual FastAPI app using `httpx` async transport — no mocking of the API layer.
 
---
 
## CI/CD
 
Every push to `main` triggers the GitHub Actions pipeline:
 
```
ruff lint → pytest → docker build → push to ECR → kubectl rollout
```
 
Branch protection on `main` requires CI to pass before merge. Rollbacks are instant via `kubectl rollout undo`.
 
---
 
## Environment Variables
 
Configured via `.env` locally; injected via Kubernetes ConfigMap and Secrets in production. Never commit `.env`.
 
| Variable | Default | Description |
|---|---|---|
| `MODEL_PATH` | `model/artifacts/model.joblib` | Path to serialized model |
| `LABELS_PATH` | `model/artifacts/labels.joblib` | Path to label mapping |
| `REDIS_URL` | `redis://redis:6379` | Redis connection string |
| `CACHE_TTL` | `3600` | Prediction cache TTL in seconds |
| `WORKERS` | `2` | Uvicorn worker count |
 
---
 
## Notebooks
 
Training, EDA, and evaluation work lives in `model/notebooks/`:
 
| Notebook | Contents |
|---|---|
| `01_eda.ipynb` | Dataset exploration, class distribution, text length analysis |
| `02_experiments.ipynb` | Hyperparameter search, loss curves, model comparison |
| `03_evaluation.ipynb` | Confusion matrix, per-class metrics, error analysis |
 
Shared preprocessing logic is extracted to `model/preprocessing.py` and imported by both notebooks and `train.py` to avoid duplication.
 
---
 
## Deployment
 
See `infra/k8s/` for Kubernetes manifests and `infra/terraform/` for cluster provisioning. The deployment uses a HorizontalPodAutoscaler targeting 70% CPU utilization, scaling between 3 and 10 replicas with zero-downtime rolling updates.
