from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleWare 
from prometheus_fastapi_instrumentator import Instrumentator 

from api.schemas import HealthResponse, PredictRequest, PredictResponse, BatchPredictRequest, BatchResponse
from api.model_loader import ModelLoader
from api.cache import PredictionCache
from api.config import Settings

model_loader = ModelLoader()
cache = PredictionCache() 
settings = Settings() 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # load model, connect to cache and yield 
    model_loader.load()
    await cache.connect() 
    yield 
    await cache.close() 

app = FastAPI("ML Server API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleWare, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator.instrument(app).expose(app) # mounts .metrics for Prometheus 

@app.get("/health", response_model=HealthResponse)
async def get_health():
    return HealthResponse(
        status = "ok",
        model_loaded = model_loader.is_loaded,
        cache_connected= await cache.ping(),
    )

@app.post("/predict", response_model=PredictResponse)
async def predict(request):
    if not model_loader.is_loaded: 
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    cached_res = await cache.get(request.text)
    if cached_res:
        cached_res["cached"] = True 
        return PredictResponse(**cached_res)
    
    res = model_loader.predict(request.text)
    await cache.set(request.text, res)
    return PredictResponse(**res, cached=False)


@app.post("/batch", response_model=BatchResponse)
async def batch_predict(requests):
    if not model_loader.is_loaded:
        raise HTTPException(stauts_code=503, detail="Model not loaded")
    predictions = [PredictResponse(**model_loader.predict(t), cached=False) for t in requests.texts] 
    return BatchResponse(predictions=predictions, responses=len(predictions))
         