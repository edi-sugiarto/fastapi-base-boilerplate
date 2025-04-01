from fastapi import FastAPI

from app.api.routes import router
from config.config import settings

app = FastAPI(
    title="FastAPI Boilerplate",
    description="A FastAPI boilerplate with SQLAlchemy, CRUD abstraction, and more",
    version=settings.APP_VERSION or "v0.1.0",
)

app.include_router(router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Service is up, hurray!"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
