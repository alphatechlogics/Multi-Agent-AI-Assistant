"""Configuration settings for the Multi-Agent AI Assistant."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ========================
    # Core API Keys
    # ========================
    anam_api_key: Optional[str] = None
    anam_api_base_url: Optional[str] = None
    cerebras_api_key: str
    serpapi_key: str
    mem0_api_key: str
    groq_api: str
    openai_api_key: Optional[str] = None


    # ========================
    # Mem0 Configuration (Long-term Memory)
    # ========================
    mem0_enabled: bool = True
    mem0_version: str = "v1.0"

    # ========================
    # ChromaDB Configuration (RAG)
    # ========================
    chromadb_collection_name: str = "documents"
    chromadb_persist_directory: str = "./data/chroma"

    # ========================
    # Agent Configuration
    # ========================
    primary_llm_model: str = "llama-3.1-8b-instant"  # Groq Reasoning Model
    
    # Specialized agent domains
    agent_domains: List[str] = [
        "research",
        "finance",
        "travel",
        "shopping",
        "jobs",
        "recipes"
    ]

    # ========================
    # Interaction Modes
    # ========================
    enable_text_chat: bool = True
    enable_voice_agent: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Global settings instance
settings = Settings()
