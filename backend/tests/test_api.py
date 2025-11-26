# backend/tests/test_api.py
import json
import pytest
import sys
from pathlib import Path

# Ensure the backend/ directory is on sys.path regardless of current working dir
# This makes the test robust both locally and in CI (repo-root or backend/ as cwd).
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Import the app using the package name the app uses locally
from app.api import app


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert json.loads(resp.data)["status"] == "ok"
