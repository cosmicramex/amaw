"""
Application configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://amaw_user:amaw_password@localhost:5432/amaw_mvp")
    
    # AI API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # YouTube API
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # File Upload
    MAX_FILE_SIZE: str = os.getenv("MAX_FILE_SIZE", "50MB")
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "./uploads")
    
    # Gemini Model Configuration
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Free tier model
    GEMINI_IMAGE_MODEL: str = "imagen-3.0-generate-001"  # Image generation model
    
    # API Limits
    MAX_REQUESTS_PER_MINUTE: int = 60  # Gemini free tier limit
    MAX_TOKENS_PER_REQUEST: int = 1000000  # Gemini context limit

settings = Settings()
