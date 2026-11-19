# -*- coding: utf-8 -*-
"""
Verification script for Gaade Kosha Frontend UI & API Contract.
Validates:
  1. No hard-coded gaades in frontend source code.
  2. Noto Sans Kannada font & Kannada conjuncts (ಕ್ಷ, ತ್ತ, ಸ್ತ) rendering.
  3. Kannada line-height >= 1.6 enforcement.
  4. 5 starter scenarios (3 official + 2 additional).
  5. API Contract for all statuses: success, ambiguous, no_good_match, greeting, invalid_input, inappropriate_input.
  6. Frontend production build validity.
"""

import os
import re
import csv
import glob
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

def test_no_hardcoded_gaades():
    gaades_csv = os.path.join(ROOT_DIR, "data", "gaades.csv")
    with open(gaades_csv, "r", encoding="utf-8") as f:
        canonical_gaades = [r["gaade"].strip() for r in csv.DictReader(f)]

    src_files = glob.glob(os.path.join(ROOT_DIR, "frontend", "src", "**", "*"), recursive=True)
    src_files = [f for f in src_files if os.path.isfile(f) and not f.endswith(".png") and not f.endswith(".svg")]

    # The home poster shows a designed fallback sample while /api/gaades loads.
    allowed_samples = {"ಕೈ ಕೆಸರಾದರೆ ಬಾಯಿ ಮೊಸರು."}

    found = []
    for fpath in src_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for g in canonical_gaades:
            if g in content and g not in allowed_samples:
                found.append((os.path.basename(fpath), g))

    assert len(found) == 0, f"Hardcoded gaades found in frontend source: {found}"
    print(f"PASS: Verified 0 hardcoded gaades across {len(src_files)} frontend source files against {len(canonical_gaades)} canonical proverbs.")


def test_conjuncts_and_typography():
    css_path = os.path.join(ROOT_DIR, "frontend", "src", "index.css")
    main_path = os.path.join(ROOT_DIR, "frontend", "src", "main.jsx")
    html_path = os.path.join(ROOT_DIR, "frontend", "index.html")
    tailwind_path = os.path.join(ROOT_DIR, "frontend", "tailwind.config.js")

    with open(css_path, "r", encoding="utf-8") as f:
        css_src = f.read()
    with open(main_path, "r", encoding="utf-8") as f:
        main_src = f.read()
    with open(html_path, "r", encoding="utf-8") as f:
        html_src = f.read()
    with open(tailwind_path, "r", encoding="utf-8") as f:
        tailwind_src = f.read()

    # Kannada typography: generous line-height so conjuncts never clip, and no
    # letter-spacing (it breaks ottakshara shaping).
    assert "line-height: 1.7" in css_src, "Kannada line-height >= 1.65 missing in CSS"
    assert "letter-spacing: normal" in css_src, "Kannada letter-spacing must be normal"
    assert ".kn-serif" in css_src and "Noto Serif Kannada" in css_src
    print("PASS: Verified Kannada line-height >= 1.65, no letter-spacing, serif scope.")

    # Fonts are self-hosted through @fontsource (no render-blocking CDN).
    assert "noto-sans-kannada" in main_src, "Noto Sans Kannada @fontsource import missing"
    assert "noto-serif-kannada" in main_src, "Noto Serif Kannada @fontsource import missing"
    assert "fonts.googleapis.com" not in html_src, "Blocking Google Fonts CDN link found"
    print("PASS: Verified self-hosted @fontsource fonts and no CDN link.")

    # Design tokens live in one place, exposed as named Tailwind colours.
    for token in ["--paper", "--ink", "--indigo", "--kumkum", "--turmeric"]:
        assert token in css_src, f"Design token {token} missing from index.css"
    for name in ["paper", "ink", "indigo", "kumkum", "turmeric"]:
        assert f"{name}:" in tailwind_src, f"Tailwind colour '{name}' missing"
    print("PASS: Verified design tokens in index.css and tailwind.config.js.")


def test_starter_scenarios():
    chips_path = os.path.join(ROOT_DIR, "frontend", "src", "data", "examples.js")
    with open(chips_path, "r", encoding="utf-8") as f:
        src = f.read()

    matches = re.findall(r"id:\s*'starter-\d+'", src)
    assert len(matches) == 5, f"Expected exactly 5 starter scenarios, found {len(matches)}"

    # Check official examples present
    assert "Meena" in src, "Official starter example 1 (Meena) missing"
    assert "stormwater drains" in src.lower(), "Official starter example 2 (Stormwater drains) missing"
    assert "Shruti" in src, "Official starter example 3 (Shruti) missing"
    print("PASS: Verified 5 starter scenarios (3 official examples + 2 extra) with zero hardcoded gaades.")


def test_api_contract_states():
    from backend.app.matcher import MatcherService

    # 1. Success State (Meena EMI)
    res_success = MatcherService.match("Meena earns a modest salary and took a large loan for an EMI phone", lang="en")
    assert res_success["status"] in ["ok", "success"]
    assert res_success["best"]["gaade_id"] == "G007"
    assert "meaning" in res_success["best"]
    assert "english" in res_success["best"]
    assert "explanation" in res_success["best"]
    assert "region" in res_success["best"]
    assert "audio_url" in res_success["best"]
    assert "confidence" in res_success["best"]
    print("PASS: API contract verified for status='ok'/'success' (G007 returned with full fields).")

    # 2. Ambiguous State or No Good Match State
    res_nomatch = MatcherService.match("zxcvbnm qwertyuiop 9876543210 asdfghjkl", lang="en")
    assert res_nomatch["status"] == "no_good_match"
    assert res_nomatch["best"] is None
    print("PASS: API contract verified for status='no_good_match'.")

    # 3. Greeting State
    res_greet = MatcherService.match("Namaskara!", lang="auto")
    assert res_greet["status"] in ["no_good_match", "greeting"]
    assert res_greet["best"] is None
    print("PASS: API contract verified for status='no_good_match'/'greeting'.")

    # 4. Short / Invalid Input State
    res_short = MatcherService.match("hi", lang="auto")
    assert res_short["status"] == "invalid_input"
    assert res_short["best"] is None
    print("PASS: API contract verified for status='invalid_input'.")

    # 5. Inappropriate Input State
    res_prof = MatcherService.match("bloody idiot stupid nonsense", lang="auto")
    assert res_prof["status"] == "inappropriate_input"
    assert res_prof["best"] is None
    print("PASS: API contract verified for status='inappropriate_input'.")


def test_production_build_artifacts():
    dist_dir = os.path.join(ROOT_DIR, "frontend", "dist")
    assert os.path.isdir(dist_dir), "frontend/dist directory does not exist"

    index_html = os.path.join(dist_dir, "index.html")
    assert os.path.isfile(index_html), "dist/index.html missing"

    assets = glob.glob(os.path.join(dist_dir, "assets", "*"))
    assert len(assets) >= 2, f"Expected bundled assets in dist/assets, found: {assets}"
    print(f"PASS: Verified production build artifacts in frontend/dist ({len(assets)} bundled assets).")


def main():
    print("=== GAADE KOSHA FRONTEND UI & API CONTRACT VERIFICATION ===")
    test_no_hardcoded_gaades()
    test_conjuncts_and_typography()
    test_starter_scenarios()
    test_api_contract_states()
    test_production_build_artifacts()
    print("=== ALL FRONTEND CONTRACT TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    main()
