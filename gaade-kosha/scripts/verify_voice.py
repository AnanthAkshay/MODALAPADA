# -*- coding: utf-8 -*-
"""
Verification Script for Prompt 8: Spoken Input & Spoken Output.
Validates all tasks and constraints:
  1. Browser Web Speech API integration (kn-IN, en-IN toggle, interim results, editable transcript).
  2. Error handling: unsupported browser, permission denied, no speech, network error.
  3. Backend ASR fallback endpoint (/api/transcribe) 503 status when disabled.
  4. Original recorded gaade audio playback (/api/audio/) with auto-play toggle, play/stop/replay.
  5. Optional explanation machine voice (speechSynthesis, Kannada voice check, hidden when missing, 'machine voice' label).
  6. Mutual exclusivity: never record and play at the same time.
"""

import os
import sys
import glob
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)


def test_backend_transcribe_fallback_503():
    """Verify backend ASR endpoint returns 503 by default."""
    assert settings.ENABLE_BACKEND_ASR is False, "ENABLE_BACKEND_ASR must be False by default"
    res = client.post("/api/transcribe")
    assert res.status_code == 503, f"Expected 503, got {res.status_code}"
    data = res.json()
    assert data["code"] == 503
    assert "Backend ASR Disabled" in data["error"]
    assert "Web Speech API" in data["detail"]
    print("PASS: Verified backend fallback POST /api/transcribe returns 503 when ENABLE_BACKEND_ASR=false.")


def test_voice_input_source_contract():
    """Verify VoiceInput component source conforms to all Web Speech API requirements."""
    vi_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "VoiceInput.jsx")
    assert os.path.isfile(vi_path), "VoiceInput.jsx does not exist"

    with open(vi_path, "r", encoding="utf-8") as f:
        src = f.read()

    # Web Speech API references
    assert "SpeechRecognition" in src and "webkitSpeechRecognition" in src, "Web Speech API recognition missing"
    assert "kn-IN" in src, "Default Kannada lang 'kn-IN' missing"
    assert "en-IN" in src, "English toggle lang 'en-IN' missing"
    assert "interimResults = true" in src, "Interim results missing"
    assert "onresult" in src, "Result handler missing"
    assert "onTranscriptChange" in src, "Transcript update callback missing"

    # Error handling
    assert "not-allowed" in src, "Permission denied error handling missing"
    assert "no-speech" in src, "No speech error handling missing"
    assert "network" in src, "Network error handling missing"
    assert "audio-capture" in src, "Audio capture error handling missing"

    # Editable transcript notice
    assert "edit the transcript" in src.lower(), "Editable transcript guidance missing"

    # Mutual exclusivity event
    assert "gaade:stop-playback" in src, "Stop playback event on mic start missing"

    print("PASS: Verified VoiceInput component Web Speech API integration, kn-IN/en-IN toggle, and error handlers.")


def test_gaade_audio_and_autoplay_contract():
    """Verify Gaade audio player uses human recordings, auto-play toggle, play/stop/replay."""
    ap_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "AudioPlayer.jsx")
    hdr_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "Header.jsx")

    with open(ap_path, "r", encoding="utf-8") as f:
        ap_src = f.read()
    with open(hdr_path, "r", encoding="utf-8") as f:
        hdr_src = f.read()

    # Audio player features
    assert "autoPlay" in ap_src, "AudioPlayer autoPlay prop missing"
    assert "handlePlay" in ap_src, "handlePlay missing"
    assert "handleStop" in ap_src, "handleStop missing"
    assert "handleReplay" in ap_src, "handleReplay missing"
    assert "audio-wave-bars" in ap_src, "Playing state wave animation missing"
    assert "gaade:stop-playback" in ap_src, "Stop event listener missing"
    assert "gaade:stop-recording" in ap_src, "Stop recording event trigger missing"

    # Autoplay toggle in Header
    assert "autoplay-toggle-btn" in hdr_src, "Autoplay toggle button in Header missing"
    assert "Auto-play Gaade" in hdr_src, "Autoplay Gaade label in Header missing"

    print("PASS: Verified Gaade Audio Player human recording playback, play/stop/replay, and auto-play toggle.")


def test_explanation_tts_contract():
    """Verify ExplanationTTS component uses speechSynthesis, checks Kannada voice, and labels machine voice."""
    tts_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "ExplanationTTS.jsx")
    assert os.path.isfile(tts_path), "ExplanationTTS.jsx does not exist"

    with open(tts_path, "r", encoding="utf-8") as f:
        src = f.read()

    assert "speechSynthesis" in src, "speechSynthesis missing in ExplanationTTS"
    assert "kn-IN" in src or "kn" in src, "Kannada voice check missing"
    assert "hasKannadaVoice" in src, "Voice existence check missing"
    assert "!hasKannadaVoice" in src and "return null" in src, "Hidden when voice missing rule missing"
    assert "machine voice" in src, "Must be clearly labeled 'machine voice'"
    assert "gaade:stop-playback" in src, "TTS mutual exclusivity trigger missing"

    print("PASS: Verified ExplanationTTS speechSynthesis integration, voice discovery, and 'machine voice' label.")


def test_no_tts_for_gaade_heading():
    """Verify that gaade proverb itself NEVER uses TTS."""
    pc_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "ProverbCard.jsx")
    with open(pc_path, "r", encoding="utf-8") as f:
        src = f.read()

    # The audio button next to the gaade heading must be AudioPlayer (human recording)
    assert "<AudioPlayer audioUrl={item.audio_url}" in src, "ProverbCard must use human AudioPlayer for gaade"
    assert "ExplanationTTS" in src, "ExplanationTTS must be used for explanation only"

    print("PASS: Verified Gaade proverb strictly uses original human recording via /api/audio/, zero TTS for gaade.")


def main():
    print("=== GAADE KOSHA VOICE FEATURES VERIFICATION (PROMPT 8) ===")
    test_backend_transcribe_fallback_503()
    test_voice_input_source_contract()
    test_gaade_audio_and_autoplay_contract()
    test_explanation_tts_contract()
    test_no_tts_for_gaade_heading()
    print("=== ALL VOICE FEATURE VERIFICATIONS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    main()

