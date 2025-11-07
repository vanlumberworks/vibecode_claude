"""Backend package for Forex Agent System API."""

from backend.streaming_adapter import StreamingForexSystem
from backend.server import app

__all__ = ["StreamingForexSystem", "app"]
