"""
Health check endpoints
"""
from fastapi import APIRouter
from app.config import settings
from app.services.vector_store import VectorStoreService

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "provider": settings.llm_provider,
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    vector_store = VectorStoreService.get_instance()

    # Check vector store
    vector_store_status = "healthy"
    vector_store_info = {}
    try:
        vector_store_info = await vector_store.get_collection_stats()
        vector_store_status = "healthy" if vector_store_info else "unhealthy"
    except Exception as e:
        vector_store_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "services": {
            "llm": {
                "status": "healthy",
                "provider": settings.llm_provider
            },
            "vector_store": {
                "status": vector_store_status,
                "info": vector_store_info
            },
            "web_search": {
                "status": "enabled" if settings.enable_web_search else "disabled"
            }
        }
    }
