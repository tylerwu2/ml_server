from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleWare 
from prometheus_fastapi_instrumentator import Instrumentator 

from schemas import HealthResponse, PredictResponse, BatchResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load model, connect to cache and yield 
    await 

app = FastAPI("ML Server API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleWare, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator.instrument(app).expose(app) # mounts .metrics for Prometheus 

@app.get("/health", response_model=HealthResponse)
async def get_health():
    await

@app.post("/predict", response_model=PredictResponse)
async def predict():
    await

@app.post("/batch", response_model=BatchResponse)
async def batch_predict():
    await