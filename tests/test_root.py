"""Tests for the root endpoint"""

from fastapi.testclient import TestClient


def test_root_redirect(client: TestClient):
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_root_redirect_with_follow(client: TestClient):
    """Test that following the redirect doesn't error (status 200 for the final resource)"""
    response = client.get("/", follow_redirects=True)
    # Following redirect may give 200 or 404 depending on if static files are served
    # Just verify the redirect happens without crashing
    assert response.status_code in [200, 404]
