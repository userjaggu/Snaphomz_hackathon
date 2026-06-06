from backend.main import app

# Expose ASGI `app` for platforms (like Vercel) that expect a function under `/api`.
# This simple wrapper imports the FastAPI app defined in `backend/main.py`.

__all__ = ("app",)
