from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routers.auth import router as auth_router
from backend.app.api.routers.policy import router as policy_router
from backend.app.core.config import settings
from backend.app.core.logging_config import configure_logging
from backend.app.core.middleware import LoggingMiddleware
from backend.app.database.init_db import init_db

configure_logging()

app = FastAPI(title=settings.project_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

app.include_router(auth_router)
app.include_router(policy_router)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.project_name}
