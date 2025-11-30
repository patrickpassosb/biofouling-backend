from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import health, predictions
from app.core.model_loader import model_loader
import logging
from contextlib import asynccontextmanager

settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    logger.info("Starting up...")
    try:
        model_loader.load_model()
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000", # React/Next.js default
    "https://biofouling-frontend.vercel.app", # Example Vercel deployment
    "*" # Allow all for hackathon simplicity, restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, tags=["Health"])
app.include_router(predictions.router, prefix=settings.API_V1_STR, tags=["Predictions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
