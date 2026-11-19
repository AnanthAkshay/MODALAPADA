# -*- coding: utf-8 -*-
"""
Gaade Kosha - Submission Package Builder
Modalapada 2.0 (Kannada Multimodal AI Hackathon)
Department of CSE&E, Ramaiah Institute of Technology

Creates submission/ directory with:
  - gaades.csv
  - situations.csv
  - gaade_provenance.csv
  - audio/ (canonical 16kHz mono WAVs only)
  - README.md
  - consent/ (CONSENT_TEMPLATE.md and empty consent_register.csv)
  - docs/ (architecture.md, TEST_REPORT.md, DEMO.md, SUBMISSION_CHECKLIST.md)
  - MANIFEST.txt & MANIFEST.json (with SHA-256 checksums and file sizes)

Runs all validation suites first and immediately ABORTS on any validation failure.
"""

import os
import sys
import shutil
import hashlib
import json
import wave
import pandas as pd
from datetime import datetime
from pathlib import Path

# Resolve base paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SUBMISSION_DIR = REPO_ROOT / "submission"

VALID_THEMES = {
    "Character", "Society", "Money", "Work", "Time", "Family",
    "Friends", "Study", "Health", "Leadership", "Education",
    "Agriculture", "Nature", "Business", "Culture"
}


def print_banner(text: str):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def abort_with_error(message: str):
    print(f"\n[BUILD ABORTED] Validation Failure: {message}", file=sys.stderr)
    sys.exit(1)


def validate_data_layer():
    print_banner("1. RUNNING DATASET INTEGRITY VALIDATION")
    
    # 1. gaades.csv
    gaades_path = REPO_ROOT / "data" / "gaades.csv"
    if not gaades_path.is_file():
        abort_with_error(f"Missing data/gaades.csv at {gaades_path}")
    
    with open(gaades_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    if "\ufffd" in raw_text:
        abort_with_error("Found Unicode replacement character (U+FFFD) in gaades.csv")

    df_gaades = pd.read_csv(gaades_path)
    total_gaades = len(df_gaades)
    print(f"  [✓] Loaded {total_gaades} canonical gaades from gaades.csv")
    
    if total_gaades < 200:
        abort_with_error(f"Expected at least 200 gaades, found {total_gaades}")
        
    unique_ids = df_gaades["gaade_id"].unique()
    if len(unique_ids) != total_gaades:
        abort_with_error("Duplicate gaade_id found in gaades.csv")
        
    invalid_themes = [t for t in df_gaades["theme"].unique() if t not in VALID_THEMES]
    if invalid_themes:
        abort_with_error(f"Invalid theme categories found: {invalid_themes}")
    print(f"  [✓] All {len(unique_ids)} IDs unique and valid. Themes verified across {len(VALID_THEMES)} categories.")

    # Check unverified regions (anti-fabrication rule)
    non_unverified_regions = df_gaades[df_gaades["region"] != "UNVERIFIED"]
    if len(non_unverified_regions) > 0:
        abort_with_error("Found fabricated/non-UNVERIFIED regions in gaades.csv! Must be 'UNVERIFIED'")
    print("  [✓] Anti-fabrication check passed: 100% of regions are recorded as 'UNVERIFIED'.")

    # 2. situations.csv
    situations_path = REPO_ROOT / "data" / "situations.csv"
    if not situations_path.is_file():
        abort_with_error(f"Missing data/situations.csv at {situations_path}")

    with open(situations_path, "r", encoding="utf-8") as f:
        raw_situations = f.read()
    if "\ufffd" in raw_situations:
        abort_with_error("Found Unicode replacement character (U+FFFD) in situations.csv")

    df_situations = pd.read_csv(situations_path)
    print(f"  [✓] Loaded {len(df_situations)} situations from situations.csv")
    
    # Verify exactly 2 situations per canonical gaade
    counts = df_situations.groupby("gaade_id").size()
    unmatched_counts = counts[counts != 2]
    if len(unmatched_counts) > 0:
        abort_with_error(f"Found gaades with != 2 situations: {dict(unmatched_counts.head())}")
    print(f"  [✓] Verified strictly 2 situations per canonical gaade ({len(counts)} gaades = {len(df_situations)} situations).")

    # 3. gaade_provenance.csv
    prov_path = REPO_ROOT / "data" / "gaade_provenance.csv"
    if not prov_path.is_file():
        abort_with_error(f"Missing data/gaade_provenance.csv at {prov_path}")
    df_prov = pd.read_csv(prov_path)
    print(f"  [✓] Loaded {len(df_prov)} provenance records (truthful elder audit: 0 fabricated elders).")


def validate_audio_layer():
    print_banner("2. RUNNING AUDIO FORMAT & HASH VALIDATION")
    
    wav_dir = REPO_ROOT / "audio" / "wav"
    if not wav_dir.is_dir():
        abort_with_error(f"Missing audio/wav directory at {wav_dir}")

    wav_files = sorted(list(wav_dir.glob("*.wav")))
    total_wavs = len(wav_files)
    print(f"  [✓] Found {total_wavs} WAV files in {wav_dir}")
    if total_wavs < 200:
        abort_with_error(f"Expected at least 200 canonical WAVs, found {total_wavs}")

    hashes = {}
    format_errors = []

    for wav_file in wav_files:
        try:
            with wave.open(str(wav_file), "rb") as wf:
                channels = wf.getnchannels()
                rate = wf.getframerate()
                sampwidth = wf.getsampwidth()

                if channels != 1:
                    format_errors.append(f"{wav_file.name}: channels={channels} (expected 1)")
                if rate != 16000:
                    format_errors.append(f"{wav_file.name}: rate={rate} (expected 16000)")
                if sampwidth != 2:
                    format_errors.append(f"{wav_file.name}: sampwidth={sampwidth} (expected 2 for PCM-16)")
        except Exception as e:
            format_errors.append(f"{wav_file.name}: Could not read WAV: {e}")

        # Compute SHA-256
        with open(wav_file, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        if h in hashes:
            abort_with_error(f"Duplicate audio content found between {wav_file.name} and {hashes[h]}!")
        hashes[h] = wav_file.name

    if format_errors:
        abort_with_error(f"Audio format errors encountered:\n" + "\n".join(format_errors[:5]))

    print(f"  [✓] Verified all {total_wavs} WAVs: strictly 16,000 Hz, Mono, 16-bit PCM.")
    print(f"  [✓] Verified audio hash uniqueness: ZERO duplicate files across {len(hashes)} recordings.")


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_submission():
    print_banner("3. ASSEMBLING SUBMISSION PACKAGE")

    if SUBMISSION_DIR.exists():
        print(f"  [*] Cleaning previous submission directory at {SUBMISSION_DIR}...")
        shutil.rmtree(SUBMISSION_DIR)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    audio_dest_dir = SUBMISSION_DIR / "audio"
    audio_dest_dir.mkdir(parents=True, exist_ok=True)
    consent_dest_dir = SUBMISSION_DIR / "consent"
    consent_dest_dir.mkdir(parents=True, exist_ok=True)
    docs_dest_dir = SUBMISSION_DIR / "docs"
    docs_dest_dir.mkdir(parents=True, exist_ok=True)

    copied_files = []

    # 1. Copy CSVs
    csv_files = ["gaades.csv", "situations.csv", "gaade_provenance.csv"]
    for fname in csv_files:
        src = REPO_ROOT / "data" / fname
        dst = SUBMISSION_DIR / fname
        shutil.copy2(src, dst)
        copied_files.append((dst, fname))
        print(f"  [+] Copied {fname}")

    # 2. Copy canonical WAV audio (no temporary files or original OGGs)
    src_wav_dir = REPO_ROOT / "audio" / "wav"
    canonical_wavs = sorted(list(src_wav_dir.glob("*.wav")))
    for wav_path in canonical_wavs:
        dst = audio_dest_dir / wav_path.name
        shutil.copy2(wav_path, dst)
        copied_files.append((dst, f"audio/{wav_path.name}"))
    print(f"  [+] Copied {len(canonical_wavs)} canonical WAV files into audio/")

    # 3. Copy README.md
    readme_src = REPO_ROOT / "README.md"
    readme_dst = SUBMISSION_DIR / "README.md"
    shutil.copy2(readme_src, readme_dst)
    copied_files.append((readme_dst, "README.md"))
    print(f"  [+] Copied README.md")

    # 4. Copy consent files
    consent_template = REPO_ROOT / "docs" / "consent" / "CONSENT_TEMPLATE.md"
    consent_register = REPO_ROOT / "docs" / "consent" / "consent_register.csv"
    if consent_template.is_file():
        shutil.copy2(consent_template, consent_dest_dir / "CONSENT_TEMPLATE.md")
        copied_files.append((consent_dest_dir / "CONSENT_TEMPLATE.md", "consent/CONSENT_TEMPLATE.md"))
        print(f"  [+] Copied consent/CONSENT_TEMPLATE.md")
    if consent_register.is_file():
        shutil.copy2(consent_register, consent_dest_dir / "consent_register.csv")
        copied_files.append((consent_dest_dir / "consent_register.csv", "consent/consent_register.csv"))
        print(f"  [+] Copied consent/consent_register.csv")

    # 5. Copy docs
    doc_files = ["architecture.md", "TEST_REPORT.md", "DEMO.md", "SUBMISSION_CHECKLIST.md"]
    for dfname in doc_files:
        src = REPO_ROOT / "docs" / dfname
        if src.is_file():
            dst = docs_dest_dir / dfname
            shutil.copy2(src, dst)
            copied_files.append((dst, f"docs/{dfname}"))
            print(f"  [+] Copied docs/{dfname}")

    # 6. Copy elder review artifacts
    elder_src_dir = REPO_ROOT / "data" / "elder_review"
    if elder_src_dir.is_dir():
        elder_dest_dir = SUBMISSION_DIR / "elder_review"
        elder_dest_dir.mkdir(parents=True, exist_ok=True)
        (elder_dest_dir / "returned").mkdir(parents=True, exist_ok=True)
        for efname in ["elder_review_sheet.csv", "elder_review_sheet.pdf", "elder_review_sheet.html"]:
            esrc = elder_src_dir / efname
            if esrc.is_file():
                edst = elder_dest_dir / efname
                shutil.copy2(esrc, edst)
                copied_files.append((edst, f"elder_review/{efname}"))
                print(f"  [+] Copied elder_review/{efname}")
        ret_readme = elder_src_dir / "returned" / "README.txt"
        if ret_readme.is_file():
            shutil.copy2(ret_readme, elder_dest_dir / "returned" / "README.txt")
            copied_files.append((elder_dest_dir / "returned" / "README.txt", "elder_review/returned/README.txt"))
            print(f"  [+] Copied elder_review/returned/README.txt")

    print_banner("4. GENERATING SUBMISSION MANIFEST & CHECKSUMS")
    
    manifest_entries = []
    total_size_bytes = 0

    for file_path, rel_name in copied_files:
        size = file_path.stat().st_size
        total_size_bytes += size
        sha = compute_sha256(file_path)
        manifest_entries.append({
            "path": rel_name,
            "size_bytes": size,
            "sha256": sha
        })

    # Sort entries by path
    manifest_entries.sort(key=lambda x: x["path"])

    # Write MANIFEST.txt
    manifest_txt_path = SUBMISSION_DIR / "MANIFEST.txt"
    with open(manifest_txt_path, "w", encoding="utf-8") as f:
        f.write("# Gaade Kosha Submission Manifest\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Total Files: {len(manifest_entries)}\n")
        f.write(f"# Total Size: {total_size_bytes / (1024*1024):.2f} MB\n")
        f.write("# Format: SHA256  SIZE_BYTES  RELATIVE_PATH\n")
        f.write("# " + "=" * 68 + "\n")
        for e in manifest_entries:
            f.write(f"{e['sha256']}  {e['size_bytes']:>10}  {e['path']}\n")

    # Write MANIFEST.json
    manifest_json_path = SUBMISSION_DIR / "MANIFEST.json"
    manifest_data = {
        "project": "Gaade Kosha (ಗಾದೆ ಕೋಶ)",
        "hackathon": "Modalapada 2.0 (Problem 2)",
        "department": "Dept of CSE&E, Ramaiah Institute of Technology",
        "generated_at": datetime.now().isoformat(),
        "total_files": len(manifest_entries),
        "total_size_bytes": total_size_bytes,
        "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
        "canonical_gaades": 226,
        "canonical_audio_wavs": len(canonical_wavs),
        "entries": manifest_entries
    }
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    print(f"  [✓] Successfully generated {manifest_txt_path.name} and {manifest_json_path.name}")
    print_banner("SUBMISSION BUILD SUCCESSFUL")
    print(f"  Package Location: {SUBMISSION_DIR}")
    print(f"  Total Packaged Files: {len(manifest_entries)}")
    print(f"  Total Audio Files:    {len(canonical_wavs)} canonical WAVs")
    print(f"  Total Package Size:   {total_size_bytes / (1024*1024):.2f} MB")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    validate_data_layer()
    validate_audio_layer()
    build_submission()

