"""
Supply Chain Analytics - API Client for Streamlit Frontend
"""
import requests
from typing import Dict, Any, Optional
import streamlit as st


class APIClient:
    """FastAPI backend client for Streamlit frontend"""

    def __init__(self, base_url: str = None):
        self.base_url = (base_url or "http://localhost:8000").rstrip("/")
        self.session = requests.Session()

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            return self.session.get(url, timeout=30, **kwargs)
        except requests.ConnectionError:
            return _error_response("Backend not reachable. Is the API server running?")

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            return self.session.post(url, timeout=60, **kwargs)
        except requests.ConnectionError:
            return _error_response("Backend not reachable. Is the API server running?")

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            return self.session.delete(url, timeout=30, **kwargs)
        except requests.ConnectionError:
            return _error_response("Backend not reachable")


def get_api_client() -> APIClient:
    """Get or create API client from Streamlit secrets"""
    try:
        base_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
    except Exception:
        base_url = "http://localhost:8000"
    return APIClient(base_url=base_url)


class _error_response:
    """Fake response for connection errors"""

    def __init__(self, message: str):
        self.status_code = 503
        self._message = message

    def json(self):
        return {"error": self._message}

    @property
    def content(self):
        return b""
