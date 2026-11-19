# -*- coding: utf-8 -*-
"""
Gaade Kosha - Hosted ASR Provider Service
Supports: Groq Whisper (default), Sarvam AI, and Google Cloud Speech.
Includes in-memory sliding-window rate limiting (20 req/min/IP),
20s timeout, 5MB file size limit, and clean error handling.
"""

import os
import time
import base64
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from threading import Lock
import httpx
from fastapi import HTTPException, status

from backend.app.config import settings

logger = logging.getLogger("gaade_kosha_asr")

class RateLimiter:
    """In-memory sliding-window rate limiter per client IP."""
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._records: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._records[client_ip]
            cutoff = now - self.window_seconds
            # Prune expired timestamps
            valid_timestamps = [t for t in timestamps if t > cutoff]
            if len(valid_timestamps) >= self.max_requests:
                self._records[client_ip] = valid_timestamps
                return False
            valid_timestamps.append(now)
            self._records[client_ip] = valid_timestamps
            return True

    def reset(self):
        """Reset rate limiter state (useful for tests)."""
        with self._lock:
            self._records.clear()

rate_limiter = RateLimiter(
    max_requests=settings.ASR_RATE_LIMIT_PER_MINUTE,
    window_seconds=60
)


class ASRService:
    """Hosted ASR Provider Service with support for Groq, Sarvam, and Google."""

    @classmethod
    def get_provider_and_key(cls, requested_provider: Optional[str] = None) -> Tuple[str, Optional[str]]:
        provider = (requested_provider or settings.ASR_PROVIDER or "groq-whisper").lower().strip()
        
        if provider in ("groq", "groq-whisper", "whisper"):
            provider_canonical = "groq-whisper"
            api_key = settings.ASR_API_KEY or settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY") or os.getenv("ASR_API_KEY")
        elif provider in ("sarvam", "sarvam-ai"):
            provider_canonical = "sarvam"
            api_key = settings.ASR_API_KEY or settings.SARVAM_API_KEY or os.getenv("SARVAM_API_KEY") or os.getenv("ASR_API_KEY")
        elif provider in ("google", "google-speech", "gemini"):
            provider_canonical = "google"
            api_key = settings.ASR_API_KEY or settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY") or os.getenv("ASR_API_KEY")
        else:
            provider_canonical = provider
            api_key = settings.ASR_API_KEY

        return provider_canonical, api_key

    @classmethod
    async def transcribe(
        cls,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        content_type: str = "audio/webm",
        lang: str = "kn",
        client_ip: str = "127.0.0.1",
        provider_override: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Transcribe audio using the configured hosted ASR provider.
        Enforces 5 MB size limit, 20 req/min rate limit, 20s timeout,
        and returns {text, transcript, provider, language}.
        """
        # 1. Rate Limiting Check (HTTP 429)
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for client IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded: maximum 20 audio transcription requests per minute per IP."
            )

        # 2. File Size Validation (HTTP 413)
        if len(audio_bytes) > settings.ASR_MAX_FILE_SIZE_BYTES:
            max_mb = settings.ASR_MAX_FILE_SIZE_BYTES / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"Audio file size exceeds the allowed limit of {max_mb:.1f} MB. Please record a shorter clip (maximum 30 seconds)."
            )

        if len(audio_bytes) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file payload is empty or too short. Please speak for at least 1 second."
            )

        # 3. Provider & Key Resolution (HTTP 401)
        provider, api_key = cls.get_provider_and_key(provider_override)

        if not api_key:
            logger.error(f"ASR API key missing for provider: {provider}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"ASR provider '{provider}' API key is not configured on the server. Please set ASR_API_KEY in the environment."
            )

        normalized_lang = "kn" if lang and lang.lower().startswith("kn") else "en"

        # 4. Dispatch to Provider with 20s Timeout
        timeout = httpx.Timeout(settings.ASR_TIMEOUT_SECONDS, connect=5.0)

        try:
            if provider == "groq-whisper":
                transcript = await cls._transcribe_groq(audio_bytes, filename, content_type, normalized_lang, api_key, timeout)
            elif provider == "sarvam":
                transcript = await cls._transcribe_sarvam(audio_bytes, filename, content_type, normalized_lang, api_key, timeout)
            elif provider == "google":
                transcript = await cls._transcribe_google(audio_bytes, content_type, normalized_lang, api_key, timeout)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported ASR provider '{provider}'. Supported providers: 'groq-whisper', 'sarvam', 'google'."
                )
        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to ASR provider '{provider}' after {settings.ASR_TIMEOUT_SECONDS}s")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Transcription request to '{provider}' timed out after {settings.ASR_TIMEOUT_SECONDS} seconds."
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling ASR provider '{provider}': {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"ASR provider '{provider}' returned an error: {str(e)}"
            )

        return {
            "status": "success",
            "text": transcript.strip(),
            "transcript": transcript.strip(),
            "provider": provider,
            "language": normalized_lang
        }

    @classmethod
    async def _transcribe_groq(
        cls,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        lang: str,
        api_key: str,
        timeout: httpx.Timeout
    ) -> str:
        """Call Groq Whisper API (whisper-large-v3)."""
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Whisper ISO code for Kannada is 'kn', English is 'en'
        files = {
            "file": (filename or "audio.webm", audio_bytes, content_type or "audio/webm")
        }
        data = {
            "model": "whisper-large-v3",
            "language": lang,
            "response_format": "json"
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, files=files, data=data)

        if resp.status_code != 200:
            err_text = resp.text[:300]
            logger.error(f"Groq API error {resp.status_code}: {err_text}")
            if resp.status_code == 401:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Groq API key.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq Whisper ASR error ({resp.status_code}): {err_text}"
            )

        result = resp.json()
        return result.get("text", "")

    @classmethod
    async def _transcribe_sarvam(
        cls,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        lang: str,
        api_key: str,
        timeout: httpx.Timeout
    ) -> str:
        """Call Sarvam AI Speech-to-Text API."""
        url = "https://api.sarvam.ai/speech-to-text"
        headers = {"api-subscription-key": api_key}
        
        sarvam_lang = "kn-IN" if lang == "kn" else "en-IN"
        files = {
            "file": (filename or "audio.wav", audio_bytes, content_type or "audio/wav")
        }
        data = {
            "model": "saaras:v1",
            "language_code": sarvam_lang
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, files=files, data=data)

        if resp.status_code != 200:
            err_text = resp.text[:300]
            logger.error(f"Sarvam API error {resp.status_code}: {err_text}")
            if resp.status_code == 401 or resp.status_code == 403:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Sarvam AI subscription key.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Sarvam AI ASR error ({resp.status_code}): {err_text}"
            )

        result = resp.json()
        return result.get("transcript") or result.get("text") or ""

    @classmethod
    async def _transcribe_google(
        cls,
        audio_bytes: bytes,
        content_type: str,
        lang: str,
        api_key: str,
        timeout: httpx.Timeout
    ) -> str:
        """Call Google Gemini 1.5 Flash multimodal transcription API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        b64_audio = base64.b64encode(audio_bytes).decode("ascii")
        prompt = (
            "Transcribe this audio recording verbatim. If spoken in Kannada, output exact Kannada script. "
            "If spoken in English, output English. Return ONLY the transcribed text, with no introductory text or markdown formatting."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": content_type or "audio/webm",
                                "data": b64_audio
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 256
            }
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload)

        if resp.status_code != 200:
            err_text = resp.text[:300]
            logger.error(f"Google API error {resp.status_code}: {err_text}")
            if resp.status_code == 400 and "API_KEY_INVALID" in err_text:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google API key.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google ASR error ({resp.status_code}): {err_text}"
            )

        result = resp.json()
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            return ""
