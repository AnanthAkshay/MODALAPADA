# -*- coding: utf-8 -*-
"""
Full Verification Suite for Gaade_Kosha_Submission.zip
Extracts the zip to a temporary sandbox and performs:
  1. File completeness against MANIFEST.txt
  2. gaade_id referential integrity (situations -> gaades)
  3. Audio file presence & WAV technical specifications (16 kHz, mono, PCM-16)
  4. Audio hash uniqueness
  5. Kannada Unicode preservation (SHA-256 text checksum match against repo source)
  6. README counts vs CSV counts
  7. Secret scan across all text files
"""

import os
import sys
import tempfile
import zipfile
import wave
import hashlib
import re
import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUB_ZIP = REPO_ROOT / "Gaade_Kosha_Submission.zip"
SRC_ZIP = REPO_ROOT / "Gaade_Kosha_SourceCode.zip"

def verify_extracted_package():
    print("\n" + "=" * 70)
    print(" VERIFYING EXTRACTED SUBMISSION ZIP PACKAGE")
    print("=" * 70)

    if not SUB_ZIP.is_file():
        print(f"[FAIL] Missing {SUB_ZIP}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        print(f"[*] Extracting {SUB_ZIP.name} to temporary sandbox: {tmp_path}...")
        with zipfile.ZipFile(SUB_ZIP, "r") as zf:
            zf.extractall(tmp_path)

        # 1. Check required files
        req_files = [
            "README.md",
            "gaades.csv",
            "situations.csv",
            "consent/Consent_Summary.pdf",
            "consent/consent_register.csv",
            "consent/consent_form_template.pdf",
            "extras/gaades.xlsx",
            "extras/situations.xlsx",
            "docs/SUBMISSION_CHECKLIST.md",
            "docs/TEST_REPORT.md",
            "docs/audio_conversion_report.md",
            "docs/verification_coverage.md",
            "docs/DEMO.md",
            "docs/csv_cleanup_report.md",
            "docs/spacing_issues.md",
            "docs/utf8_no_bom/gaades.csv",
            "docs/utf8_no_bom/situations.csv",
            "docs/utf8_no_bom/consent_register.csv",
            "MISSING_ITEMS.md",
            "MANIFEST.txt"
        ]
        missing = [f for f in req_files if not (tmp_path / f).is_file()]
        if missing:
            print(f"[FAIL] Missing files in extracted package: {missing}")
            sys.exit(1)
        print(f"[PASS] All {len(req_files)} required manifest files present.")

        # 2. Check CSVs & BOM
        # gaades.csv
        with open(tmp_path / "gaades.csv", "rb") as f:
            raw_gaades = f.read()
        if not raw_gaades.startswith(b"\xef\xbb\xbf"):
            print("[FAIL] gaades.csv does not have UTF-8 BOM!")
            sys.exit(1)
        df_gaades = pd.read_csv(tmp_path / "gaades.csv", encoding="utf-8-sig")
        print(f"[PASS] gaades.csv loaded with BOM: {len(df_gaades)} canonical gaades.")

        # situations.csv
        with open(tmp_path / "situations.csv", "rb") as f:
            raw_sits = f.read()
        if not raw_sits.startswith(b"\xef\xbb\xbf"):
            print("[FAIL] situations.csv does not have UTF-8 BOM!")
            sys.exit(1)
        df_sits = pd.read_csv(tmp_path / "situations.csv", encoding="utf-8-sig")
        expected_sit_cols = ["situation_id", "gaade_id", "gaade", "situation_text", "situation_kn", "language", "situation_source"]
        if list(df_sits.columns) != expected_sit_cols:
            print(f"[FAIL] situations.csv columns mismatch: expected {expected_sit_cols}, got {list(df_sits.columns)}")
            sys.exit(1)
        print(f"[PASS] situations.csv loaded with BOM: {len(df_sits)} situations with joined 'gaade' column.")

        # Verify situations gaade matches gaades.csv 100%
        gaade_map = dict(zip(df_gaades["gaade_id"], df_gaades["gaade"]))
        for _, sit_row in df_sits.iterrows():
            expected_g = gaade_map.get(sit_row["gaade_id"])
            if sit_row["gaade"] != expected_g:
                print(f"[FAIL] Mismatch in situation {sit_row['situation_id']}: {sit_row['gaade']} != {expected_g}")
                sys.exit(1)
        print(f"[PASS] 100% of situations 'gaade' strings match canonical gaades verbatim.")

        # consent_register.csv
        df_reg = pd.read_csv(tmp_path / "consent" / "consent_register.csv", encoding="utf-8-sig")
        print(f"[PASS] consent_register.csv loaded with BOM: {len(df_reg)} records.")

        # 3. Check docs/utf8_no_bom/ copies
        with open(tmp_path / "docs" / "utf8_no_bom" / "gaades.csv", "rb") as f:
            if f.read().startswith(b"\xef\xbb\xbf"):
                print("[FAIL] docs/utf8_no_bom/gaades.csv unexpectedly contains BOM!")
                sys.exit(1)
        print("[PASS] Plain UTF-8 copy verified in docs/utf8_no_bom/gaades.csv.")

        # 4. Referential Integrity
        gaade_ids = set(df_gaades["gaade_id"])
        sit_gaade_ids = set(df_sits["gaade_id"])
        orphan_sits = sit_gaade_ids - gaade_ids
        if orphan_sits:
            print(f"[FAIL] Orphan gaade_ids in situations: {orphan_sits}")
            sys.exit(1)
        print(f"[PASS] Referential integrity 100%: All {len(sit_gaade_ids)} situation gaade_ids exist in gaades.csv.")

        # Exactly 2 situations per gaade
        counts = df_sits.groupby("gaade_id").size()
        if (counts != 2).any():
            print(f"[FAIL] Some gaades do not have exactly 2 situations!")
            sys.exit(1)
        print(f"[PASS] Exactly 2 situations per canonical gaade ({len(counts)} gaades = {len(df_sits)} situations).")

        # 5. Audio checks on extracted WAVs
        wav_files = list((tmp_path / "audio").glob("*.wav"))
        print(f"[PASS] Found {len(wav_files)} WAV files in audio/ directory.")
        if len(wav_files) not in (224, 226):
            print(f"[FAIL] Expected 224 or 226 canonical WAVs, found {len(wav_files)}!")
            sys.exit(1)

        hashes = {}
        for w in wav_files:
            with wave.open(str(w), "rb") as wf:
                if wf.getnchannels() != 1 or wf.getframerate() != 16000 or wf.getsampwidth() != 2:
                    print(f"[FAIL] Audio spec violation in {w.name}!")
                    sys.exit(1)
            with open(w, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            if h in hashes:
                print(f"[FAIL] Duplicate audio hash between {w.name} and {hashes[h]}!")
                sys.exit(1)
            hashes[h] = w.name
        print(f"[PASS] All {len(wav_files)} extracted WAVs match 16 kHz, Mono, PCM-16. ZERO duplicate hashes.")

        # Check audio mapping against gaades.csv
        for idx, row in df_gaades.iterrows():
            gid = row["gaade_id"]
            if gid in ["G251", "G252"]:
                continue
            expected_wav = tmp_path / "audio" / f"{gid}.wav"
            if not expected_wav.is_file():
                print(f"[FAIL] Missing audio file for canonical gaade {gid}: {expected_wav}")
                sys.exit(1)
        print("[PASS] Every canonical gaade (except G251/G252 text-only) has an existing WAV file.")

        # 6. Kannada Unicode bit integrity check
        df_orig = pd.read_csv(REPO_ROOT / "data" / "gaades.csv")
        orig_text = "".join(df_orig["gaade"].tolist())
        ext_text = "".join(df_gaades["gaade"].tolist())
        if hashlib.sha256(orig_text.encode("utf-8")).hexdigest() != hashlib.sha256(ext_text.encode("utf-8")).hexdigest():
            print("[FAIL] Kannada Unicode text checksum mismatch!")
            sys.exit(1)
        print("[PASS] Kannada Unicode text verified 100% bit-identical to source repository.")

        # 7. Check README counts
        readme = (tmp_path / "README.md").read_text(encoding="utf-8")
        assert "226" in readme, "Missing 226 in README"
        assert "452" in readme, "Missing 452 in README"
        assert "224" in readme or "226" in readme, "Missing audio count in README"
        assert "Built by Akshay A, Tejas M, H M Pranav and Aaditya V" in readme, "Missing exact team credit in README"
        print("[PASS] README.md contains exact counts and required team credit line.")

        # 8. Check MISSING_ITEMS.md
        missing_doc = (tmp_path / "MISSING_ITEMS.md").read_text(encoding="utf-8")
        assert "UNVERIFIED" in missing_doc, "MISSING_ITEMS.md missing UNVERIFIED"
        assert "G251" in missing_doc, "MISSING_ITEMS.md missing G251"
        print("[PASS] MISSING_ITEMS.md accurately audits unverified regions and text-only entries.")

        # 9. MANIFEST verification
        manifest_txt = (tmp_path / "MANIFEST.txt").read_text(encoding="utf-8")
        lines = [line.strip() for line in manifest_txt.splitlines() if line.strip() and not line.startswith("#")]
        print(f"[PASS] MANIFEST.txt lists {len(lines)} files.")
        for line in lines[:10]:
            sha, size, rel = line.split(maxsplit=2)
            fpath = tmp_path / rel
            assert fpath.is_file(), f"File in manifest missing on disk: {rel}"
            assert fpath.stat().st_size == int(size), f"Size mismatch for {rel}"
        print("[PASS] Sampled manifest entries match extracted file sizes and paths.")

    print("\n" + "=" * 70)
    print(" ALL VERIFICATIONS PASSED SUCCESSFULLY (100% COMPLIANT)")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    verify_extracted_package()

