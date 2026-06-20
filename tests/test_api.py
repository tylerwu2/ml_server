import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app 

async def test_predict_valid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/predict", json={"text": "some input"})
    assert resp.status_code == 200