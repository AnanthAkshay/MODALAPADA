# -*- coding: utf-8 -*-
"""
Configuration settings for Gaade Kosha Backend.
Loads environment variables with robust fallback defaults.
"""

import os
from typing import List

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

    # ASR Fallback Configuration (Disabled by default per prompt specification)
    ENABLE_BACKEND_ASR: bool = os.getenv("ENABLE_BACKEND_ASR", "false").lower() in ("true", "1", "t")

settings = Settings()
