import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from api.main import app