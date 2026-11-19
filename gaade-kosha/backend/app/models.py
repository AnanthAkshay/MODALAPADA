# -*- coding: utf-8 -*-
"""
Pydantic Models for Gaade Kosha API schemas.
Preserves exact Unicode representations for Kannada texts.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# Health Check
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    message: str
    database: Optional[str] = "unknown"
    gaades_count: Optional[int] = 0
    situations_count: Optional[int] = 0

# Provenance
class ProvenanceItem(BaseModel):
    source_pdf_number: int
    source_type: str
    verification_status: str
    duplicate_of: Optional[str] = None
    consent_ref: str
    notes: Optional[str] = None

# Gaade
class GaadeListItem(BaseModel):
    gaade_id: str
    gaade: str
    meaning: str
    english: str
    example: Optional[str] = ""
    region: str
    theme: str
    audio_file: str
    audio_url: Optional[str] = None

class GaadeDetailResponse(BaseModel):
    gaade_id: str
    gaade: str
    meaning: str
    english: str
    example: Optional[str] = ""
    region: str
    theme: str
    audio_file: str
    audio_url: Optional[str] = None
    provenance: Optional[ProvenanceItem] = None
    situations_count: int = 0

class GaadeListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[GaadeListItem]

# Situations
class SituationItem(BaseModel):
    situation_id: str
    gaade_id: str
    situation_text: str
    situation_kn: str
    language: str
    situation_source: str

class SituationListResponse(BaseModel):
    gaade_id: str
    total: int
    items: List[SituationItem]

# Themes
class ThemeItem(BaseModel):
    theme: str
    count: int

class ThemeListResponse(BaseModel):
    total_themes: int
    items: List[ThemeItem]

# Match Request / Response Models
class MatchCandidate(BaseModel):
    gaade_id: str
    gaade: str
    meaning: str
    english: str
    theme: str
    region: str
    audio_file: Optional[str] = None
    audio_url: Optional[str] = None
    example: Optional[str] = ""
    confidence: float
    explanation: Optional[str] = None
    closest_situation_id: Optional[str] = None
    provenance: Optional[ProvenanceItem] = None
    situations_count: Optional[int] = 0

class MatchRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Situation description in English, Kannada, or Kanglish")
    lang: Optional[str] = Field(default="auto", description="Query language hint (en, kn, kanglish, auto)")

class MatchResponse(BaseModel):
    status: str
    matcher_backend: str
    detected_lang: str
    message: str
    best: Optional[MatchCandidate] = None
    alternatives: List[MatchCandidate] = Field(default_factory=list)

# Audio Transcription (ASR) Models
class TranscribeResponse(BaseModel):
    status: str = "success"
    text: str
    transcript: str
    provider: str = "groq-whisper"
    language: Optional[str] = "kn"
    confidence: Optional[float] = None

# Consistent Error Model
class ErrorResponse(BaseModel):
    error: str
    detail: str
    code: int

