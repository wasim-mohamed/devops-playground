# backend/tests/test_api.py
import json
import pytest
# use a full import path so CI and local runs resolve the module the same
from backend.app.api import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as c:
        yield c

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert json.loads(resp.data)["status"] == "ok"
