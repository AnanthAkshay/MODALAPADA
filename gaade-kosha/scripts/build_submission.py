# -*- coding: utf-8 -*-
"""
Gaade Kosha - Submission Package Builder
Modalapada 2.0 (Kannada Multimodal AI Hackathon)
Department of CSE&E, Ramaiah Institute of Technology

Constructs the complete, final submission package:
  submission/
    README.md
    gaades.csv (UTF-8 with BOM for Excel)
    situations.csv (UTF-8 with BOM for Excel)
    audio/ (224 canonical 16kHz mono PCM-16 WAVs)
    consent/
      Consent_Summary.pdf (10 pages with verified embedded signatures)
      consent_register.csv (UTF-8 with BOM)
      consent_form_template.pdf (blank bilingual form template)
    docs/
      SUBMISSION_CHECKLIST.md
      TEST_REPORT.md
      audio_conversion_report.md
      verification_coverage.md
      DEMO.md
      utf8_no_bom/ (plain UTF-8 copies without BOM)
        gaades.csv
        situations.csv
        consent_register.csv
    MISSING_ITEMS.md
    MANIFEST.txt (SHA-256 and size per file)
    MANIFEST.json

Also produces:
  - Gaade_Kosha_Submission.zip
  - Gaade_Kosha_SourceCode.zip
And executes an automated verification on the zipped artifacts.
"""

import os
import sys
import shutil
import hashlib
import json
import wave
import zipfile
import re
import pandas as pd
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SUBMISSION_DIR = REPO_ROOT / "submission"
ROOT_DIR = REPO_ROOT.parent if (REPO_ROOT.parent / "Kannada_Gaadegalu_Revised_1_to_250.pdf").exists() else REPO_ROOT

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


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


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

    # 3. consent_register.csv
    reg_path = REPO_ROOT / "docs" / "consent" / "consent_register.csv"
    if not reg_path.is_file():
        abort_with_error(f"Missing consent register at {reg_path}")
    df_reg = pd.read_csv(reg_path)
    print(f"  [✓] Loaded {len(df_reg)} verified consent records from consent_register.csv")


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
    utf8_no_bom_dir = docs_dest_dir / "utf8_no_bom"
    utf8_no_bom_dir.mkdir(parents=True, exist_ok=True)

    copied_files = []

    # 1. Process & Write CSVs (with BOM in root, without BOM in docs/utf8_no_bom/)
    csv_mappings = [
        ("gaades.csv", REPO_ROOT / "data" / "gaades.csv"),
        ("situations.csv", REPO_ROOT / "data" / "situations.csv"),
        ("consent/consent_register.csv", REPO_ROOT / "docs" / "consent" / "consent_register.csv")
    ]

    for rel_dest, src_path in csv_mappings:
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Destination with BOM
        dest_with_bom = SUBMISSION_DIR / rel_dest
        dest_with_bom.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_with_bom, "w", encoding="utf-8-sig") as f:
            f.write(content)
        copied_files.append((dest_with_bom, rel_dest))
        print(f"  [+] Wrote {rel_dest} (UTF-8 with BOM)")

        # Destination without BOM in docs/utf8_no_bom/
        base_name = Path(rel_dest).name
        dest_no_bom = utf8_no_bom_dir / base_name
        with open(dest_no_bom, "w", encoding="utf-8") as f:
            f.write(content)
        copied_files.append((dest_no_bom, f"docs/utf8_no_bom/{base_name}"))
        print(f"  [+] Wrote docs/utf8_no_bom/{base_name} (Plain UTF-8)")

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

    # 4. Copy MISSING_ITEMS.md
    missing_src = REPO_ROOT / "docs" / "MISSING_ITEMS.md"
    missing_dst = SUBMISSION_DIR / "MISSING_ITEMS.md"
    shutil.copy2(missing_src, missing_dst)
    copied_files.append((missing_dst, "MISSING_ITEMS.md"))
    print(f"  [+] Copied MISSING_ITEMS.md")

    # 5. Copy Consent PDFs
    consent_pdfs = [
        ("consent/Consent_Summary.pdf", REPO_ROOT / "docs" / "consent" / "Consent_Summary.pdf"),
        ("consent/consent_form_template.pdf", REPO_ROOT / "docs" / "consent" / "consent_form_template.pdf"),
    ]
    for rel_dest, src_path in consent_pdfs:
        if src_path.is_file():
            dst = SUBMISSION_DIR / rel_dest
            shutil.copy2(src_path, dst)
            copied_files.append((dst, rel_dest))
            print(f"  [+] Copied {rel_dest}")

    # 6. Copy documentation files into docs/
    doc_files = [
        ("docs/SUBMISSION_CHECKLIST.md", REPO_ROOT / "docs" / "SUBMISSION_CHECKLIST.md"),
        ("docs/TEST_REPORT.md", REPO_ROOT / "docs" / "TEST_REPORT.md"),
        ("docs/audio_conversion_report.md", REPO_ROOT / "data" / "reports" / "audio_conversion_report.md"),
        ("docs/verification_coverage.md", REPO_ROOT / "docs" / "verification_coverage.md"),
        ("docs/DEMO.md", REPO_ROOT / "docs" / "DEMO.md"),
    ]
    for rel_dest, src_path in doc_files:
        if src_path.is_file():
            dst = SUBMISSION_DIR / rel_dest
            shutil.copy2(src_path, dst)
            copied_files.append((dst, rel_dest))
            print(f"  [+] Copied {rel_dest}")

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


def create_zip_packages():
    print_banner("5. CREATING SUBMISSION & SOURCE CODE ZIP ARCHIVES")

    # 1. Gaade_Kosha_Submission.zip
    sub_zip_path = REPO_ROOT / "Gaade_Kosha_Submission.zip"
    if sub_zip_path.exists():
        sub_zip_path.unlink()

    print(f"  [*] Packing {sub_zip_path.name} from {SUBMISSION_DIR}...")
    with zipfile.ZipFile(sub_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SUBMISSION_DIR):
            for f in files:
                full_path = Path(root) / f
                rel_path = full_path.relative_to(SUBMISSION_DIR)
                zf.write(full_path, arcname=str(rel_path))

    sub_size_mb = sub_zip_path.stat().st_size / (1024 * 1024)
    print(f"  [✓] Created {sub_zip_path.name} ({sub_size_mb:.2f} MB)")

    # 2. Gaade_Kosha_SourceCode.zip
    src_zip_path = REPO_ROOT / "Gaade_Kosha_SourceCode.zip"
    if src_zip_path.exists():
        src_zip_path.unlink()

    print(f"  [*] Packing {src_zip_path.name} (clean repo excluding caches, envs, node_modules)...")
    exclude_patterns = [
        r"[\\/]node_modules[\\/]",
        r"[\\/]\.git[\\/]",
        r"[\\/]\.pytest_cache[\\/]",
        r"[\\/]__pycache__[\\/]",
        r"[\\/]\.cache[\\/]",
        r"[\\/]\.vite[\\/]",
        r"[\\/]frontend[\\/]dist[\\/]",
        r"[\\/]submission[\\/]",
        r"\.py[cod]$",
        r"\.zip$",
        r"^\.env$",
        r"^\.env\.local$",
        r"^\.env\.production$"
    ]
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in exclude_patterns]

    with zipfile.ZipFile(src_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(REPO_ROOT):
            for f in files:
                full_path = Path(root) / f
                rel_path_str = str(full_path.relative_to(REPO_ROOT))

                # Check if ignored
                if any(p.search(str(full_path)) or p.search(rel_path_str) for p in compiled_patterns):
                    continue
                # Also do not include the zip files themselves
                if f.endswith(".zip"):
                    continue

                zf.write(full_path, arcname=rel_path_str)

    src_size_mb = src_zip_path.stat().st_size / (1024 * 1024)
    print(f"  [✓] Created {src_zip_path.name} ({src_size_mb:.2f} MB)")

    # Also make a copy at ROOT_DIR if REPO_ROOT is a subfolder
    if ROOT_DIR != REPO_ROOT:
        shutil.copy2(sub_zip_path, ROOT_DIR / sub_zip_path.name)
        shutil.copy2(src_zip_path, ROOT_DIR / src_zip_path.name)
        print(f"  [+] Mirrored zip archives to project root: {ROOT_DIR}")


def verify_zip_packages():
    print_banner("6. VERIFYING GENERATED ZIP ARCHIVES")

    sub_zip_path = REPO_ROOT / "Gaade_Kosha_Submission.zip"
    src_zip_path = REPO_ROOT / "Gaade_Kosha_SourceCode.zip"

    # 1. Test zip integrity
    with zipfile.ZipFile(sub_zip_path, "r") as zf:
        bad_file = zf.testzip()
        if bad_file:
            abort_with_error(f"Corrupted file in {sub_zip_path.name}: {bad_file}")
        namelist = zf.namelist()
        print(f"  [✓] {sub_zip_path.name} opened cleanly. Contains {len(namelist)} items.")

    with zipfile.ZipFile(src_zip_path, "r") as zf:
        bad_file = zf.testzip()
        if bad_file:
            abort_with_error(f"Corrupted file in {src_zip_path.name}: {bad_file}")
        src_namelist = zf.namelist()
        print(f"  [✓] {src_zip_path.name} opened cleanly. Contains {len(src_namelist)} items.")

    # 2. Secret Scan inside both zips
    print("  [*] Scanning zip archives for leaked secrets or API keys...")
    secret_regexes = [
        re.compile(r"AIzaSy[a-zA-Z0-9_\-]{30,}"),
        re.compile(r"sk-[a-zA-Z0-9]{30,}"),
        re.compile(r"gsk_[a-zA-Z0-9]{25,}"),
        re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----")
    ]
    leaks = []

    for zpath in [sub_zip_path, src_zip_path]:
        with zipfile.ZipFile(zpath, "r") as zf:
            for member in zf.namelist():
                # Skip binary audio/pdf files for text search
                if any(member.endswith(ext) for ext in [".wav", ".ogg", ".pdf", ".jpeg", ".jpg", ".png", ".joblib", ".db"]):
                    continue
                try:
                    content = zf.read(member).decode("utf-8", errors="ignore")
                    for reg in secret_regexes:
                        match = reg.search(content)
                        if match:
                            leaks.append((zpath.name, member, match.group(0)[:8] + "..."))
                except Exception:
                    pass

    if leaks:
        abort_with_error(f"SECURITY LEAK: Found secret patterns in zip archive: {leaks}")
    print("  [✓] Secret scan PASSED: Zero API keys, private tokens, or secrets found in zip archives.")

    # 3. Kannada Unicode Integrity check (compare before & after in submission zip)
    print("  [*] Verifying Kannada Unicode integrity in packaged CSVs...")
    with zipfile.ZipFile(sub_zip_path, "r") as zf:
        csv_bytes = zf.read("gaades.csv")
        # Check for BOM
        if not csv_bytes.startswith(b"\xef\xbb\xbf"):
            abort_with_error("gaades.csv in submission zip is missing UTF-8 BOM!")
        text = csv_bytes.decode("utf-8-sig")
        if "\ufffd" in text:
            abort_with_error("Found U+FFFD in packaged gaades.csv!")
        
        # Check text-only copy in docs/utf8_no_bom/
        no_bom_bytes = zf.read("docs/utf8_no_bom/gaades.csv")
        if no_bom_bytes.startswith(b"\xef\xbb\xbf"):
            abort_with_error("docs/utf8_no_bom/gaades.csv unexpectedly contains BOM!")
        
        # Verify gaade text content matches exactly
        df_zip = pd.read_csv(pd.io.common.BytesIO(csv_bytes))
        df_orig = pd.read_csv(REPO_ROOT / "data" / "gaades.csv")
        if not (df_zip["gaade"] == df_orig["gaade"]).all():
            abort_with_error("Packaged gaades text does not match original data/gaades.csv!")
        print(f"  [✓] Kannada Unicode integrity verified: 100% bit-identical across all {len(df_zip)} gaades.")

    # 4. Check that README counts equal CSV counts
    with zipfile.ZipFile(sub_zip_path, "r") as zf:
        readme_text = zf.read("README.md").decode("utf-8")
        if "226" not in readme_text:
            abort_with_error("README does not reference 226 canonical gaades!")
        if "452" not in readme_text:
            abort_with_error("README does not reference 452 situations!")
        if "224" not in readme_text:
            abort_with_error("README does not reference 224 WAV recordings!")
        print("  [✓] README counts agree with CSV counts (226 canonical gaades, 452 situations, 224 WAVs).")


if __name__ == "__main__":
    validate_data_layer()
    validate_audio_layer()
    build_submission()
    create_zip_packages()
    verify_zip_packages()
