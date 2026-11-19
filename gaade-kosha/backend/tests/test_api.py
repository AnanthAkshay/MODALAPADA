# -*- coding: utf-8 -*-
"""
Tests for Gaade Kosha REST API.
Verifies all endpoints, pagination, query filtering, 404s, audio delivery,
path traversal prevention, and byte-for-byte Kannada Unicode round-tripping.
"""

import os
import csv
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)

DATA_DIR = settings.DATA_DIR
GAADES_CSV = os.path.join(DATA_DIR, 'gaades.csv')
SITUATIONS_CSV = os.path.join(DATA_DIR, 'situations.csv')

def test_api_health_endpoint():
    """Verify health endpoint reports connected database and 226 gaades."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["gaades_count"] == 226
    assert data["situations_count"] == 452

def test_api_list_gaades_pagination():
    """Verify pagination limit and offset parameters."""
    res = client.get("/api/gaades?limit=10&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 226
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["items"]) == 10
    assert data["items"][0]["gaade_id"] == "G001"

    res2 = client.get("/api/gaades?limit=5&offset=10")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["limit"] == 5
    assert data2["offset"] == 10
    assert len(data2["items"]) == 5

def test_api_list_gaades_filtering():
    """Verify filtering by theme and text search query q."""
    # Filter by theme
    res = client.get("/api/gaades?theme=work")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["theme"].lower() == "work"

    # Search query in Kannada
    res_kn = client.get("/api/gaades?q=ಆಸೆ")
    assert res_kn.status_code == 200
    data_kn = res_kn.json()
    assert data_kn["total"] >= 1
    found_g001 = any(item["gaade_id"] == "G001" for item in data_kn["items"])
    assert found_g001

    # Search query in English
    res_en = client.get("/api/gaades?q=greed")
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["total"] >= 1

def test_api_get_gaade_by_id():
    """Verify single gaade retrieval by ID with provenance."""
    res = client.get("/api/gaades/G001")
    assert res.status_code == 200
    data = res.json()
    assert data["gaade_id"] == "G001"
    assert data["gaade"] == "ಅತಿ ಆಸೆ ಗತಿ ಕೇಡು."
    assert data["audio_url"] == "/api/audio/G001"
    assert data["provenance"] is not None
    assert data["provenance"]["source_pdf_number"] == 1
    assert data["situations_count"] == 2

def test_api_get_gaade_by_id_404():
    """Verify 404 response for nonexistent gaade."""
    res = client.get("/api/gaades/G999")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert data["code"] == 404
    assert "not found" in data["detail"].lower()

def test_api_get_gaade_invalid_id_format():
    """Verify 400 Bad Request on regex mismatch."""
    res = client.get("/api/gaades/invalid_id")
    assert res.status_code == 400
    data = res.json()
    assert data["code"] == 400
    assert "format" in data["detail"].lower()

def test_api_get_gaade_situations():
    """Verify situations endpoint returns both situations for a gaade."""
    res = client.get("/api/gaades/G001/situations")
    assert res.status_code == 200
    data = res.json()
    assert data["gaade_id"] == "G001"
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["situation_id"] == "S001_1"
    assert data["items"][1]["situation_id"] == "S001_2"

def test_api_get_gaade_situations_404():
    """Verify 404 response when querying situations for nonexistent gaade."""
    res = client.get("/api/gaades/G999/situations")
    assert res.status_code == 404
    assert res.json()["code"] == 404

def test_api_get_themes():
    """Verify themes endpoint returns list of themes with counts."""
    res = client.get("/api/themes")
    assert res.status_code == 200
    data = res.json()
    assert data["total_themes"] > 0
    assert len(data["items"]) == data["total_themes"]
    for t in data["items"]:
        assert "theme" in t
        assert t["count"] > 0

def test_api_audio_endpoint_success():
    """Verify audio endpoint delivers 16 kHz WAV file with correct Content-Type."""
    res = client.get("/api/audio/G001")
    assert res.status_code == 200
    assert "audio/wav" in res.headers["content-type"].lower()
    assert len(res.content) > 1000

def test_api_audio_endpoint_missing_audio():
    """Verify 404 JSON response for canonical gaades without recordings (G251, G252)."""
    res = client.get("/api/audio/G251")
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == 404
    assert "missing" in data["detail"].lower() or "not found" in data["detail"].lower()

def test_api_audio_path_traversal_prevention():
    """Verify strict regex rejects directory traversal attempts."""
    res = client.get("/api/audio/..%2F..%2Fetc%2Fpasswd")
    assert res.status_code == 400 or res.status_code == 404

    res2 = client.get("/api/audio/G001_evil")
    assert res2.status_code == 400

def test_api_match_starter_examples():
    """
    ACCEPTANCE CRITERIA: Verify that all 3 official starter examples
    achieve Top-1 match to the expected canonical Kannada proverbs.
    """
    # 1. Meena loan on EMI -> G007
    q1 = {
        "text": "Meena earns a modest salary as an entry-level clerk. However, she took a large personal loan to buy an expensive smartphone on EMI, and now struggles to pay her monthly rent and groceries.",
        "lang": "en"
    }
    res1 = client.post("/api/match", json=q1)
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["status"] in ["ok", "success"]
    assert d1["best"]["gaade_id"] == "G007"
    assert d1["best"]["gaade"] == "ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು."
    assert d1["best"]["audio_url"] == "/api/audio/G007"
    assert len(d1["best"]["explanation"]) > 20
    assert d1["best"]["confidence"] > 0.4
    assert len(d1["alternatives"]) >= 1

    # 2. Municipal flood drain negligence -> G251
    q2 = {
        "text": "Municipal authorities ignored clearing clogged stormwater drains all summer. When torrential monsoon rains lashed the city and inundated residential basements, they frantically scrambled to deploy emergency diesel suction pumps.",
        "lang": "en"
    }
    res2 = client.post("/api/match", json=q2)
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["status"] in ["ok", "success"]
    assert d2["best"]["gaade_id"] == "G251"
    assert d2["best"]["gaade"] == "ಬೆಂಕಿ ಬಂದಾಗ ಬಾವಿ ತೋಡಿದಂತೆ."
    assert d2["best"]["confidence"] > 0.4

    # 3. Social media glamour vs debt -> G252
    q3 = {
        "text": "Shruti felt depressed seeing glamorous vacation photos of influencers on social media, assuming everyone else had flawless, effortless lives. Her grandmother reminded her that behind closed doors, every family contends with private heartaches, unpaid bills, and difficult conflicts.",
        "lang": "en"
    }
    res3 = client.post("/api/match", json=q3)
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["status"] in ["ok", "success"]
    assert d3["best"]["gaade_id"] == "G252"
    assert d3["best"]["gaade"] == "ಎಲ್ಲರ ಮನೆ ದೋಸೆಯೂ ತೂತು."
    assert d3["best"]["confidence"] > 0.4


def test_api_match_kannada_query():
    """Verify semantic matching using pure Kannada text input."""
    payload = {
        "text": "ಮೀನಾ ಒಬ್ಬ ಕಿರಿಯ ಗುಮಾಸ್ತೆಯಾಗಿ ಸಣ್ಣ ಸಂಬಳ ಪಡೆಯುತ್ತಿದ್ದರೂ, ದುಬಾರಿ ಸ್ಮಾರ್ಟ್‌ಫೋನನ್ನು ಮಾಸಿಕ ಕಂತಿನಲ್ಲಿ ಖರೀದಿಸಿ ಈಗ ಕೋಣೆಯ ಬಾಡಿಗೆ ಕಟ್ಟಲು ಪರದಾಡುತ್ತಿದ್ದಾಳೆ.",
        "lang": "kn"
    }
    res = client.post("/api/match", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["ok", "success", "ambiguous"]
    assert data["detected_lang"] in ["kn", "mixed"]
    assert data["best"]["gaade_id"] == "G007"


def test_api_match_kanglish_query():
    """Verify Kanglish detection and semantic matching."""
    payload = {
        "text": "nanna friend tumba lazy aagi kelasa madalla sumne iddare adikke kashta bantu",
        "lang": "auto"
    }
    res = client.post("/api/match", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["detected_lang"] in ["kanglish", "en", "mixed"]
    assert data["status"] in ["ok", "success", "ambiguous"]
    assert data["best"] is not None


def test_api_match_edge_cases():
    """Verify edge case handling: greeting, invalid length, profanity, and no match."""
    # 1. Greeting
    res_greet = client.post("/api/match", json={"text": "Namaskara!"})
    assert res_greet.status_code == 200
    d_greet = res_greet.json()
    assert d_greet["status"] in ["no_good_match", "greeting"]
    assert d_greet["best"] is None
    assert "Namaskara" in d_greet["message"]

    # 2. Too short / invalid input
    res_short = client.post("/api/match", json={"text": "hi"})
    assert res_short.status_code == 200
    d_short = res_short.json()
    assert d_short["status"] == "invalid_input"
    assert d_short["best"] is None

    # 3. Profanity
    res_prof = client.post("/api/match", json={"text": "You bloody idiot stupid jerk"})
    assert res_prof.status_code == 200
    d_prof = res_prof.json()
    assert d_prof["status"] in ["inappropriate", "inappropriate_input"]
    assert d_prof["best"] is None

    # 4. Gibberish / No match
    res_none = client.post("/api/match", json={"text": "qqwwxxyyzz 1234567890 qwertyuiop asdfghjkl"})
    assert res_none.status_code == 200
    d_none = res_none.json()
    assert d_none["status"] == "no_good_match"
    assert d_none["best"] is None

def test_kannada_unicode_roundtrip():
    """
    CRITICAL TEST: Verify that Kannada Unicode characters retrieved via API
    match data/gaades.csv byte-for-byte across all 226 canonical proverbs.
    Zero normalization or encoding corruption allowed.
    """
    with open(GAADES_CSV, 'r', encoding='utf-8') as f:
        csv_gaades = {r['gaade_id']: r for r in csv.DictReader(f)}
        
    res = client.get("/api/gaades?limit=300")
    assert res.status_code == 200
    api_items = res.json()["items"]
    assert len(api_items) == 226
    
    for item in api_items:
        gid = item["gaade_id"]
        assert gid in csv_gaades, f"Unexpected gaade_id {gid} in API response"
        csv_row = csv_gaades[gid]
        
        # Exact Unicode character sequence equality
        assert item["gaade"] == csv_row["gaade"], f"Kannada text mismatch for {gid}"
        assert item["meaning"] == csv_row["meaning"], f"Meaning mismatch for {gid}"
        assert item["english"] == csv_row["english"], f"English mismatch for {gid}"
        assert item["theme"] == csv_row["theme"], f"Theme mismatch for {gid}"
        assert item["region"] == csv_row["region"], f"Region mismatch for {gid}"

def test_all_canonical_gaades_retrievable_and_audio():
    """
    ACCEPTANCE CRITERIA: Verify every canonical gaade (all 226) is retrievable
    via GET /api/gaades/{gaade_id}, and has a working audio URL (or 404 for missing).
    """
    res = client.get("/api/gaades?limit=300")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 226
    
    for item in items:
        gid = item["gaade_id"]
        # 1. Single item endpoint works
        res_item = client.get(f"/api/gaades/{gid}")
        assert res_item.status_code == 200
        data_item = res_item.json()
        assert data_item["gaade_id"] == gid
        assert len(data_item["gaade"]) > 0
        assert data_item["situations_count"] == 2
        
        # 2. Audio URL verification
        num = int(gid[1:])
        if num <= 250:
            assert data_item["audio_url"] == f"/api/audio/{gid}"
            res_audio = client.get(f"/api/audio/{gid}")
            assert res_audio.status_code == 200
            assert "audio/wav" in res_audio.headers["content-type"].lower()
            assert len(res_audio.content) > 100
        else:
            assert data_item["audio_file"] == "MISSING"
            assert data_item["audio_url"] is None
            res_audio = client.get(f"/api/audio/{gid}")
            assert res_audio.status_code == 404
            assert res_audio.json()["code"] == 404

def test_api_transcribe_disabled_503():
    """Verify POST /api/transcribe returns 503 when ENABLE_BACKEND_ASR=false."""
    res = client.post("/api/transcribe")
    assert res.status_code == 503
    data = res.json()
    assert data["code"] == 503
    assert "Backend ASR Disabled" in data["error"]
    assert "Web Speech API" in data["detail"]

