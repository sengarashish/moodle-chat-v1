"""
Configuration management for AI Assistant backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # LLM Provider
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_model: str = "claude-3-opus-20240229"
    openai_embedding_model: str = "text-embedding-3-small"

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "moodle_knowledge"
    qdrant_vector_size: int = 1536

    # Search
    enable_web_search: bool = True
    serper_api_key: Optional[str] = None

    # Application
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = False
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Moodle
    moodle_base_url: str = "http://localhost"
    moodle_upload_dir: str = "/tmp/moodle_uploads"

    # Age-based responses
    enable_age_based_responses: bool = True
    child_age_max: int = 12
    teen_age_max: int = 17

    # RAG
    rag_top_k: int = 5
    rag_score_threshold: float = 0.7
    max_history_length: int = 10

    # Rate limiting
    rate_limit_per_minute: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
