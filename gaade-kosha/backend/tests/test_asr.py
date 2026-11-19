# -*- coding: utf-8 -*-
"""
Unit tests for Hosted ASR Fallback Endpoint (/api/transcribe)
Tests:
1. Missing API key returns 401 Unauthorized
2. Oversize audio (> 5 MB) returns 413 Payload Too Large
3. Empty audio (< 100 bytes) returns 400 Bad Request
4. Timeout (> 20s) returns 504 Gateway Timeout
5. Mocked Groq Whisper provider returns 200 OK with Kannada transcript
6. Mocked Sarvam AI provider returns 200 OK with Kannada transcript
7. Rate limiting (> 20 requests/min per IP) returns 429 Too Many Requests
"""

import io
import pytest
import httpx
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.asr import rate_limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_asr_test_env(monkeypatch):
    """Enable backend ASR and reset rate limiter state before each test."""
    monkeypatch.setattr(settings, "ENABLE_BACKEND_ASR", True)
    rate_limiter.reset()


def test_transcribe_missing_key_returns_401(monkeypatch):
    """When ASR_API_KEY is not set or empty, /api/transcribe must return 401 Unauthorized."""
    monkeypatch.setattr(settings, "ASR_API_KEY", None)
    monkeypatch.setattr(settings, "GROQ_API_KEY", None)
    monkeypatch.setattr(settings, "SARVAM_API_KEY", None)
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", None)
    monkeypatch.delenv("ASR_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("SARVAM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    fake_audio = io.BytesIO(b"RIFF" + b"\x00" * 200)
    files = {"file": ("test.webm", fake_audio, "audio/webm")}
    data = {"lang": "kn", "provider": "groq-whisper"}

    response = client.post("/api/transcribe", files=files, data=data)
    assert response.status_code == 401
    json_data = response.json()
    assert "error" in json_data or "detail" in json_data


def test_transcribe_oversize_returns_413(monkeypatch):
    """When audio payload exceeds 5 MB limit, /api/transcribe must return 413 Payload Too Large."""
    monkeypatch.setattr(settings, "ASR_API_KEY", "dummy_test_key_123")
    monkeypatch.setattr(settings, "ASR_MAX_FILE_SIZE_BYTES", 5 * 1024 * 1024)

    # 5.2 MB payload
    large_payload = io.BytesIO(b"X" * (5 * 1024 * 1024 + 200 * 1024))
    files = {"file": ("huge.webm", large_payload, "audio/webm")}

    response = client.post("/api/transcribe", files=files, data={"lang": "kn"})
    assert response.status_code == 413
    json_data = response.json()
    assert "exceeds" in json_data["detail"].lower() or "limit" in json_data["detail"].lower()


def test_transcribe_empty_file_returns_400(monkeypatch):
    """When audio payload is empty or too short (<100 bytes), /api/transcribe must return 400 Bad Request."""
    monkeypatch.setattr(settings, "ASR_API_KEY", "dummy_test_key_123")

    tiny_payload = io.BytesIO(b"RIFFtiny")
    files = {"file": ("tiny.webm", tiny_payload, "audio/webm")}

    response = client.post("/api/transcribe", files=files, data={"lang": "kn"})
    assert response.status_code == 400
    json_data = response.json()
    assert "too short" in json_data["detail"].lower() or "empty" in json_data["detail"].lower()


@pytest.mark.anyio
async def test_transcribe_timeout_returns_504(monkeypatch):
    """When upstream ASR call times out, /api/transcribe must return 504 Gateway Timeout."""
    monkeypatch.setattr(settings, "ASR_API_KEY", "dummy_test_key_123")
    monkeypatch.setattr(settings, "ASR_PROVIDER", "groq-whisper")

    fake_audio = io.BytesIO(b"RIFF" + b"\x00" * 300)
    files = {"file": ("test.webm", fake_audio, "audio/webm")}

    # Mock httpx.AsyncClient.post to raise TimeoutException
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Upstream timed out")):
        response = client.post("/api/transcribe", files=files, data={"lang": "kn"})
        assert response.status_code == 504
        json_data = response.json()
        assert "timed out" in json_data["detail"].lower()


@pytest.mark.anyio
async def test_transcribe_success_groq(monkeypatch):
    """When Groq Whisper returns 200, /api/transcribe returns structured {text, provider, language}."""
    monkeypatch.setattr(settings, "ASR_API_KEY", "gsk_test_groq_key_123")
    monkeypatch.setattr(settings, "ASR_PROVIDER", "groq-whisper")

    fake_audio = io.BytesIO(b"RIFF" + b"\x00" * 300)
    files = {"file": ("kannada_speech.webm", fake_audio, "audio/webm")}

    # Mock successful Groq response
    mock_resp = httpx.Response(
        200,
        json={"text": "ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು"},
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/audio/transcriptions")
    )

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        response = client.post("/api/transcribe", files=files, data={"lang": "kn"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["text"] == "ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು"
        assert data["transcript"] == "ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು"
        assert data["provider"] == "groq-whisper"
        assert data["language"] == "kn"


@pytest.mark.anyio
async def test_transcribe_success_sarvam(monkeypatch):
    """When Sarvam returns 200, /api/transcribe returns structured {text, provider, language}."""
    monkeypatch.setattr(settings, "ASR_API_KEY", "sarvam_test_key_456")
    monkeypatch.setattr(settings, "ASR_PROVIDER", "sarvam")

    fake_audio = io.BytesIO(b"RIFF" + b"\x00" * 300)
    files = {"file": ("kannada_speech.wav", fake_audio, "audio/wav")}

    # Mock successful Sarvam response
    mock_resp = httpx.Response(
        200,
        json={"transcript": "ಕಾಯಕವೇ ಕೈಲಾಸ"},
        request=httpx.Request("POST", "https://api.sarvam.ai/speech-to-text")
    )

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        response = client.post("/api/transcribe", files=files, data={"lang": "kn", "provider": "sarvam"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["text"] == "ಕಾಯಕವೇ ಕೈಲಾಸ"
        assert data["provider"] == "sarvam"
        assert data["language"] == "kn"


def test_transcribe_rate_limit_exceeded_returns_429(monkeypatch):
    """When client IP exceeds 20 requests in 1 minute, the 21st request returns 429 Too Many Requests."""
    monkeypatch.setattr(settings, "ASR_API_KEY", "gsk_test_key")
    monkeypatch.setattr(settings, "ASR_RATE_LIMIT_PER_MINUTE", 20)
    rate_limiter.max_requests = 20

    fake_audio = io.BytesIO(b"RIFF" + b"\x00" * 200)

    # Mock successful upstream response
    mock_resp = httpx.Response(
        200,
        json={"text": "ಟೆಸ್ಟ್"},
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/audio/transcriptions")
    )

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        for i in range(20):
            files = {"file": ("test.webm", io.BytesIO(b"RIFF" + b"\x00" * 200), "audio/webm")}
            r = client.post("/api/transcribe", files=files, data={"lang": "kn"})
            assert r.status_code == 200, f"Request {i+1} should pass"

        # 21st request must trigger 429
        files = {"file": ("test.webm", io.BytesIO(b"RIFF" + b"\x00" * 200), "audio/webm")}
        r21 = client.post("/api/transcribe", files=files, data={"lang": "kn"})
        assert r21.status_code == 429
        assert "rate limit exceeded" in r21.json()["detail"].lower()
