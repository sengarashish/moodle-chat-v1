"""
Main FastAPI application for Moodle AI Assistant
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config import settings
from app.api import chat, ingest, health
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)

# Create FastAPI app
app = FastAPI(
    title="Moodle AI Assistant API",
    description="RAG-powered AI assistant for Moodle with LangChain and Qdrant",
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Moodle AI Assistant backend...")

    try:
        # Initialize vector store
        logger.info("Initializing Qdrant vector store...")
        vector_store = VectorStoreService.get_instance()
        await vector_store.initialize()
        logger.info("✓ Vector store initialized")

        # Initialize LLM service
        logger.info("Initializing LLM service...")
        llm_service = LLMService.get_instance()
        logger.info(f"✓ LLM service initialized with provider: {settings.llm_provider}")

        logger.info("🚀 Backend startup complete!")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Moodle AI Assistant backend...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Moodle AI Assistant API",
        "version": "1.0.0",
        "status": "running",
        "provider": settings.llm_provider
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )
