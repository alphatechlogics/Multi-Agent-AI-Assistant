"""Configuration settings for the Multi-Agent AI Assistant."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ========================
    # Core API Keys
    # ========================
    anam_api_key: str
    cerebras_api_key: str
    serpapi_key: str
    mem0_api_key: str
    groq_api_key: Optional[str] = None

    # ========================
    # Anam AI Configuration (for avatar/voice - multi-modal)
    # ========================
    anam_api_base_url: str = "https://api.anam.ai"
    anam_avatar_id: str = "30fa96d0-26c4-4e55-94a0-517025942e18"  # Default
    anam_voice_id: str = "6bfbe25a-979d-40f3-a92b-5394170af54b"   # Default

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
    primary_llm_model: str = "gpt-oss-120b"  # Only reasoning model
    
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
    # FastRTC Configuration (Ultra-low latency Voice)
    # ========================
    fastrtc_enabled: bool = True
    fastrtc_server_url: Optional[str] = None

    # ========================
    # Interaction Modes
    # ========================
    enable_text_chat: bool = True
    enable_video_avatar: bool = True
    enable_voice_agent: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Global settings instance
settings = Settings()
