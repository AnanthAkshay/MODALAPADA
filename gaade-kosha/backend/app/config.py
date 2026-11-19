# -*- coding: utf-8 -*-
"""
Configuration settings for Gaade Kosha Backend.
Loads environment variables with robust fallback defaults.
"""

import os
from typing import List, Optional

# Base directory is gaade-kosha root
candidate_1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if os.path.exists(os.path.join(candidate_1, 'gaade-kosha', 'audio', 'wav')):
    BASE_DIR = os.path.join(candidate_1, 'gaade-kosha')
elif os.path.exists(os.path.join(candidate_1, 'audio', 'wav')):
    BASE_DIR = candidate_1
else:
    BASE_DIR = candidate_1

def get_env_list(key: str, default: List[str]) -> List[str]:
    val = os.getenv(key)
    if not val:
        return default
    return [v.strip() for v in val.split(',') if v.strip()]

class Settings:
    BASE_DIR: str = BASE_DIR
    PROJECT_NAME: str = "Gaade Kosha API"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Database
    DB_REL_PATH: str = os.getenv("DATABASE_PATH", "data/gaade_kosha.db")
    DATABASE_PATH: str = os.path.abspath(os.path.join(BASE_DIR, DB_REL_PATH))
    
    # Audio
    AUDIO_REL_PATH: str = os.getenv("AUDIO_DIR", "audio/wav")
    AUDIO_DIR: str = os.path.abspath(os.path.join(BASE_DIR, AUDIO_REL_PATH))
    
    # Data Directory
    DATA_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "data"))
    
    # CORS
    CORS_ORIGINS: List[str] = get_env_list(
        "CORS_ORIGINS",
        ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"]
    )

    # Hosted ASR Provider Configuration
    ASR_PROVIDER: str = os.getenv("ASR_PROVIDER", "groq-whisper").lower().strip()
    ASR_API_KEY: Optional[str] = os.getenv("ASR_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    SARVAM_API_KEY: Optional[str] = os.getenv("SARVAM_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    ASR_MAX_FILE_SIZE_BYTES: int = int(os.getenv("ASR_MAX_FILE_SIZE_BYTES", str(5 * 1024 * 1024)))
    ASR_TIMEOUT_SECONDS: float = float(os.getenv("ASR_TIMEOUT_SECONDS", "20.0"))
    ASR_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("ASR_RATE_LIMIT_PER_MINUTE", "20"))
    ENABLE_BACKEND_ASR: bool = os.getenv("ENABLE_BACKEND_ASR", "false").lower() in ("true", "1", "t")

    # LLM Matcher Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower().strip()
    LLM_API_KEY: Optional[str] = (
        os.getenv("LLM_API_KEY")
        or (os.getenv("GROQ_API_KEY") if os.getenv("LLM_PROVIDER", "").lower().strip() == "groq" else None)
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GROQ_API_KEY")
    )
    LLM_MODEL: Optional[str] = os.getenv("LLM_MODEL")
    LLM_TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "15.0"))
    LLM_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("LLM_RATE_LIMIT_PER_MINUTE", "60"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))


settings = Settings()
