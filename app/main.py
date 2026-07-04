"""
main.py
-------
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000
(from inside the backend/ directory)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Support Ticket Classification API",
    description="Classifies customer support tickets by category and priority using NLP.",
    version="1.0.0",
)

# Allow the static frontend (served separately, e.g. from file:// or a dev server) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/", tags=["System"])
def root():
    return {"message": "Ticket Classification API is running. See /docs for API docs."}
