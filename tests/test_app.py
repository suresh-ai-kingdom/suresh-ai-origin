import os
import sys

# Ensure repo root is on sys.path so tests can import `app` when pytest's cwd varies.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app, PRODUCTS


def test_home(client):
    rv = client.get("/")
    assert rv.status_code == 200


def test_buy(client):
    rv = client.get("/buy?product=starter")
    assert rv.status_code == 200


def test_success(client):
    rv = client.get("/success?product=starter")
    assert rv.status_code == 200


def test_download_invalid(client):
    rv = client.get("/download/invalid")
    assert rv.status_code == 404


def test_download_valid(client):
    product = next(iter(PRODUCTS))
    rv = client.get(f"/download/{product}")
    assert rv.status_code in (200, 302)
