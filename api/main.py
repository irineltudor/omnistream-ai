"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.generate import router as generate_router
from utils.logging_config import logger
from utils.config import Config

# Initialize FastAPI app
app = FastAPI(
    title="Universal Video Factory",
    description="Automated video generation using free/local tools",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router, prefix="/api", tags=["video"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Universal Video Factory",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("Universal Video Factory API starting up")
    Config.ensure_directories()
    logger.info("Directories initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Universal Video Factory API shutting down")
