# -*- coding: utf-8 -*-
"""
Gaade Kosha API - Data Layer & REST API Service
Problem 2: Proverbs for Every Situation (Modalapada 2.0)
Department of CSE&E, Ramaiah Institute of Technology
"""

import os
import re
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Path, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError

from backend.app.config import settings
from backend.app.db import (
    get_db_connection,
    get_stats,
    list_gaades,
    get_gaade_by_id,
    get_situations_for_gaade,
    get_themes_summary
)
from backend.app.models import (
    HealthResponse,
    GaadeListResponse,
    GaadeDetailResponse,
    SituationListResponse,
    ThemeListResponse,
    MatchRequest,
    MatchResponse,
    TranscribeResponse,
    ErrorResponse
)
from backend.app.matcher import MatcherService

# Setup structured logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("gaade_kosha_api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Proverb companion matching Kannada proverbs to real-life situations with explanations and human audio.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Regex pattern for strict Gaade ID format (G followed by exactly 3 digits)
GAADE_ID_PATTERN = re.compile(r"^G\d{3}$")


# Global Exception Handlers for Consistent JSON Error Responses
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "detail": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": str(exc.errors()),
            "code": 422
        }
    )


# Root & Health Endpoints
@app.get("/", tags=["General"])
def get_root(request: Request):
    """Root endpoint: serves frontend UI for browsers, JSON info for API clients."""
    accept = request.headers.get("accept", "")
    dist_index = os.path.abspath(os.path.join(settings.BASE_DIR, "frontend", "dist", "index.html"))
    if "text/html" in accept and os.path.isfile(dist_index):
        return FileResponse(dist_index)
    return {
        "message": "Welcome to Gaade Kosha API (ಗಾದೆ ಕೋಶ)",
        "project": "Modalapada 2.0 - Problem 2",
        "health": "/health",
        "docs": "/docs",
        "ui": "/index.html"
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
def get_health() -> HealthResponse:
    """
    Health check endpoint returning system status, version, and database metrics.
    """
    db_status = "connected"
    gaades_count = 0
    situations_count = 0
    try:
        conn = get_db_connection()
        gaades_count, situations_count = get_stats(conn)
        conn.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        message="Hello World from Gaade Kosha backend!",
        database=db_status,
        gaades_count=gaades_count,
        situations_count=situations_count
    )


# Proverbs (Gaades) Endpoints
@app.get(
    "/api/gaades",
    response_model=GaadeListResponse,
    tags=["Gaades"],
    responses={500: {"model": ErrorResponse}}
)
def get_gaades(
    theme: Optional[str] = Query(None, description="Filter proverbs by thematic category"),
    region: Optional[str] = Query(None, description="Filter proverbs by geographic origin"),
    q: Optional[str] = Query(None, description="Text search across Kannada proverb, meaning, and English text"),
    limit: int = Query(50, ge=1, le=300, description="Maximum items per page"),
    offset: int = Query(0, ge=0, description="Items to skip for pagination")
):
    """
    List and search canonical Kannada proverbs with pagination and filtering.
    """
    conn = get_db_connection()
    try:
        total, items = list_gaades(conn, theme=theme, region=region, q=q, limit=limit, offset=offset)
        return GaadeListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items
        )
    finally:
        conn.close()


@app.get(
    "/api/gaades/{gaade_id}",
    response_model=GaadeDetailResponse,
    tags=["Gaades"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid Gaade ID format"},
        404: {"model": ErrorResponse, "description": "Proverb not found"}
    }
)
def get_gaade(
    gaade_id: str = Path(..., description="Unique 3-digit gaade identifier, e.g. G001")
):
    """
    Retrieve full details for a specific Kannada proverb by ID, including ethical provenance.
    """
    if not GAADE_ID_PATTERN.match(gaade_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gaade_id format '{gaade_id}'. Expected format '^G\\d{{3}}$' (e.g. G001)."
        )
        
    conn = get_db_connection()
    try:
        item = get_gaade_by_id(conn, gaade_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proverb with ID '{gaade_id}' was not found in the collection."
            )
        return item
    finally:
        conn.close()


@app.get(
    "/api/gaades/{gaade_id}/situations",
    response_model=SituationListResponse,
    tags=["Gaades"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid Gaade ID format"},
        404: {"model": ErrorResponse, "description": "Proverb not found"}
    }
)
def get_gaade_situations(
    gaade_id: str = Path(..., description="Unique 3-digit gaade identifier, e.g. G001")
):
    """
    Retrieve real-life situation scenarios associated with a specific Kannada proverb.
    """
    if not GAADE_ID_PATTERN.match(gaade_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gaade_id format '{gaade_id}'. Expected format '^G\\d{{3}}$' (e.g. G001)."
        )
        
    conn = get_db_connection()
    try:
        situations = get_situations_for_gaade(conn, gaade_id)
        if situations is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proverb with ID '{gaade_id}' was not found."
            )
        return SituationListResponse(
            gaade_id=gaade_id,
            total=len(situations),
            items=situations
        )
    finally:
        conn.close()


@app.get(
    "/api/themes",
    response_model=ThemeListResponse,
    tags=["Themes"]
)
def get_themes():
    """
    List all thematic categories with proverbs counts.
    """
    conn = get_db_connection()
    try:
        items = get_themes_summary(conn)
        return ThemeListResponse(
            total_themes=len(items),
            items=items
        )
    finally:
        conn.close()


# Audio Serving Endpoint (Strict Path Traversal Prevention)
@app.get(
    "/api/audio/{gaade_id}",
    tags=["Audio"],
    responses={
        200: {"content": {"audio/wav": {}}, "description": "16 kHz mono WAV recording"},
        400: {"model": ErrorResponse, "description": "Invalid Gaade ID format"},
        404: {"model": ErrorResponse, "description": "Audio recording missing or not found"}
    }
)
def get_audio(
    gaade_id: str = Path(..., description="Unique 3-digit gaade identifier, e.g. G001")
):
    """
    Stream standardized 16 kHz mono WAV recording of the human speaker reciting the proverb.
    Strict regex enforcement prevents path traversal.
    """
    # Strict regex check to prevent directory traversal
    if not GAADE_ID_PATTERN.match(gaade_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gaade_id '{gaade_id}'. Path traversal rejected."
        )
        
    wav_path = os.path.join(settings.AUDIO_DIR, f"{gaade_id}.wav")
    
    if not os.path.isfile(wav_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio recording for gaade '{gaade_id}' was not found or is missing."
        )
        
    return FileResponse(
        path=wav_path,
        media_type="audio/wav",
        filename=f"{gaade_id}.wav"
    )


# Semantic Proverb Matcher Endpoint
@app.post(
    "/api/match",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Matcher"],
    summary="Match situation description to relevant Kannada proverbs",
    responses={
        200: {"model": MatchResponse, "description": "Match result or diagnostic resolution"},
        400: {"model": ErrorResponse, "description": "Invalid request payload"},
        500: {"model": ErrorResponse, "description": "Server internal error"}
    }
)
def match_proverb(request: MatchRequest):
    """
    Semantic proverb matcher endpoint.
    Accepts user situation narrative (English, Kannada, or Kanglish) and returns the best matching proverb,
    ranked alternatives, confidence score, and grounded explanation.
    """
    result = MatcherService.match(text=request.text, lang=request.lang)
    return result


# Optional Backend ASR Fallback Endpoint (Prompt 8 Task 2)
@app.post(
    "/api/transcribe",
    response_model=TranscribeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Audio"],
    summary="Transcribe spoken audio blob (optional fallback ASR)",
    responses={
        200: {"model": TranscribeResponse, "description": "Transcription result"},
        503: {"model": ErrorResponse, "description": "Backend ASR disabled or unavailable"}
    }
)
async def transcribe_audio(
    file: Optional[UploadFile] = File(None)
):
    """
    Optional backend fallback for audio transcription.
    Disabled by default (ENABLE_BACKEND_ASR=false).
    Browser Web Speech API is the primary ASR path.
    """
    if not settings.ENABLE_BACKEND_ASR:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Backend ASR Disabled",
                "detail": "Backend Whisper ASR is disabled (ENABLE_BACKEND_ASR=false). Primary speech recognition is handled in-browser via the Web Speech API.",
                "code": 503
            }
        )

    # If backend ASR is enabled, attempt Whisper transcription
    try:
        import whisper
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Model Unavailable",
                "detail": "Whisper speech-to-text model could not be loaded. Please use browser Web Speech API.",
                "code": 503
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "ASR Engine Unavailable",
                "detail": f"Backend ASR error: {str(e)}. Please use browser Web Speech API.",
                "code": 503
            }
        )


# Optional Static Frontend Mount (serves production build if available)
dist_dir = os.path.abspath(os.path.join(settings.BASE_DIR, "frontend", "dist"))
if os.path.exists(dist_dir) and os.path.isfile(os.path.join(dist_dir, "index.html")):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static_frontend")
    logger.info(f"Mounted static frontend from {dist_dir}")

