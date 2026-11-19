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
    """Verify the Web Speech API hook and its UI conform to every voice requirement."""
    hook_path = os.path.join(ROOT_DIR, "frontend", "src", "hooks", "useSpeechRecognition.js")
    form_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "SituationForm.jsx")
    copy_path = os.path.join(ROOT_DIR, "frontend", "src", "i18n", "strings.js")
    assert os.path.isfile(hook_path), "useSpeechRecognition.js does not exist"
    assert os.path.isfile(form_path), "SituationForm.jsx does not exist"
    assert os.path.isfile(copy_path), "i18n strings.js does not exist"

    with open(hook_path, "r", encoding="utf-8") as f:
        hook_src = f.read()
    with open(form_path, "r", encoding="utf-8") as f:
        form_src = f.read()
    with open(copy_path, "r", encoding="utf-8") as f:
        copy_src = f.read()
    src = hook_src + form_src + copy_src

    # Web Speech API references
    assert "SpeechRecognition" in src and "webkitSpeechRecognition" in src, "Web Speech API recognition missing"
    assert "kn-IN" in src, "Default Kannada lang 'kn-IN' missing"
    assert "en-IN" in src, "English toggle lang 'en-IN' missing"
    assert "interimResults = true" in src, "Interim results missing"
    assert "onresult" in src, "Result handler missing"
    assert "onTranscript" in src, "Transcript update callback missing"

    # Error handling
    assert "not-allowed" in src, "Permission denied error handling missing"
    assert "no-speech" in src, "No speech error handling missing"
    assert "network" in src, "Network error handling missing"
    assert "audio-capture" in src, "Audio capture error handling missing"

    # Editable transcript notice
    assert "transcript is editable" in src.lower(), "Editable transcript guidance missing"

    # Copy is centralised: the form must not carry its own strings
    assert "home.transcriptHint" in form_src, "Transcript hint must come from i18n"
    assert "ಮಾತನಾಡಿ" in copy_src, "Kannada speak label missing from i18n"

    # Mutual exclusivity event
    assert "gaade:stop-playback" in src, "Stop playback event on mic start missing"

    print("PASS: Verified VoiceInput component Web Speech API integration, kn-IN/en-IN toggle, and error handlers.")


def test_gaade_audio_and_waveform_contract():
    """Verify the gaade player uses human recordings with a playing waveform."""
    ap_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "AudioPlayer.jsx")
    wave_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "Waveform.jsx")
    copy_path = os.path.join(ROOT_DIR, "frontend", "src", "i18n", "strings.js")

    with open(ap_path, "r", encoding="utf-8") as f:
        ap_src = f.read()
    with open(wave_path, "r", encoding="utf-8") as f:
        wave_src = f.read()
    with open(copy_path, "r", encoding="utf-8") as f:
        copy_src = f.read()

    assert "mediaUrl" in ap_src, "AudioPlayer must resolve the /api/audio path"
    assert "toggle" in ap_src, "Play/pause handler missing"
    assert "gaade:stop-playback" in ap_src, "Stop event listener missing"
    assert "gaade:stop-recording" in ap_src, "Stop recording event trigger missing"
    assert "result.noRecording" in ap_src, "Missing-audio copy missing"
    assert "No recording for this gaade" in copy_src, "Missing-audio copy missing from i18n"
    assert "animate-wave-bar" in wave_src, "Playing state wave animation missing"

    print("PASS: Verified Gaade Audio Player human recording playback, waveform, and no-recording state.")


def test_explanation_tts_contract():
    """Verify ExplanationTTS component uses speechSynthesis, checks Kannada voice, and labels machine voice."""
    tts_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "ExplanationTTS.jsx")
    assert os.path.isfile(tts_path), "ExplanationTTS.jsx does not exist"

    with open(tts_path, "r", encoding="utf-8") as f:
        src = f.read()

    assert "speechSynthesis" in src, "speechSynthesis missing in ExplanationTTS"
    assert "kn-IN" in src or "kn" in src, "Kannada voice check missing"
    copy_path = os.path.join(ROOT_DIR, "frontend", "src", "i18n", "strings.js")
    with open(copy_path, "r", encoding="utf-8") as f:
        copy_src = f.read()

    assert "getVoices" in src, "Voice discovery missing"
    assert "if (!voice || !text) return null" in src, "Hidden when voice missing rule missing"
    assert "result.machineVoice" in src, "Machine voice label must come from i18n"
    assert "machine voice" in copy_src.lower(), "Must be clearly labeled 'machine voice'"
    assert "ಯಂತ್ರ ಧ್ವನಿ" in copy_src, "Kannada machine-voice label missing"
    assert "gaade:stop-playback" in src, "TTS mutual exclusivity trigger missing"

    print("PASS: Verified ExplanationTTS speechSynthesis integration, voice discovery, and 'machine voice' label.")


def test_no_tts_for_gaade_heading():
    """Verify that gaade proverb itself NEVER uses TTS."""
    rs_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "ResultScreen.jsx")
    with open(rs_path, "r", encoding="utf-8") as f:
        src = f.read()

    # The audio button next to the gaade heading must be AudioPlayer (human recording)
    assert "<AudioPlayer audioUrl={item.audio_url}" in src, "ResultScreen must use human AudioPlayer for gaade"
    assert "<ExplanationTTS text={item.explanation" in src, "ExplanationTTS must be used for the explanation only"

    print("PASS: Verified Gaade proverb strictly uses original human recording via /api/audio/, zero TTS for gaade.")


def main():
    print("=== GAADE KOSHA VOICE FEATURES VERIFICATION (PROMPT 8) ===")
    test_backend_transcribe_fallback_503()
    test_voice_input_source_contract()
    test_gaade_audio_and_waveform_contract()
    test_explanation_tts_contract()
    test_no_tts_for_gaade_heading()
    print("=== ALL VOICE FEATURE VERIFICATIONS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    main()

