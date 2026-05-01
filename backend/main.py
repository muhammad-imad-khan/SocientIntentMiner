import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import init_db
from routes import auth, leads, billing, projects, health

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Social Intent Miner...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS — support wildcard patterns for Vercel preview deploys
def _expand_origins(origins: list[str]) -> list[str]:
    expanded = []
    for o in origins:
        if "*" in o:
            # CORSMiddleware needs allow_origin_regex for wildcards
            pass
        else:
            expanded.append(o)
    return expanded


_has_wildcard = any("*" in o for o in settings.ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_expand_origins(settings.ALLOWED_ORIGINS) if _has_wildcard else settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app" if _has_wildcard else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Routes
prefix = settings.API_PREFIX
app.include_router(health.router)
app.include_router(auth.router, prefix=f"{prefix}/auth")
app.include_router(projects.router, prefix=f"{prefix}/projects")
app.include_router(leads.router, prefix=f"{prefix}/leads")
app.include_router(billing.router, prefix=f"{prefix}/billing")
