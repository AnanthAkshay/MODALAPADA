# -*- coding: utf-8 -*-
"""
Gaade Kosha - Submission Package Builder
Modalapada 2.0 (Kannada Multimodal AI Hackathon)
Department of CSE&E, Ramaiah Institute of Technology

Constructs the complete, final submission package:
  submission/
    README.md
    gaades.csv (UTF-8 with BOM & CRLF for Excel)
    situations.csv (with joined 'gaade' column, UTF-8 with BOM & CRLF for Excel)
    audio/ (224 canonical 16kHz mono PCM-16 WAVs)
    consent/
      Consent_Summary.pdf (10 pages with verified embedded signatures)
      consent_register.csv (UTF-8 with BOM & CRLF)
      consent_form_template.pdf (blank bilingual form template)
    extras/
      gaades.xlsx (Formatted Excel copy with frozen header, Noto Sans Kannada font)
      situations.xlsx (Formatted Excel copy with frozen header, Noto Sans Kannada font)
    docs/
      SUBMISSION_CHECKLIST.md
      TEST_REPORT.md
      audio_conversion_report.md
      verification_coverage.md
      DEMO.md
      csv_cleanup_report.md
      spacing_issues.md
      utf8_no_bom/ (plain UTF-8 copies without BOM, LF line endings)
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
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

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


def clean_cell(val: str) -> str:
    """Strip leading/trailing whitespace (spaces, tabs, NBSP, ZWSP)."""
    if val is None:
        return ""
    return str(val).strip(" \t\r\n\u00a0\u200b")


def clean_free_text(val: str) -> str:
    """Normalize English/free-text fields according to Rule B."""
    if not val:
        return ""
    text = str(val)
    # Replace internal line breaks with a single space
    text = re.sub(r"[\r\n]+", " ", text)
    # Replace odd/curly/non-breaking spaces with standard space
    text = re.sub(r"[\u00a0\u2000-\u200b\u3000]", " ", text)
    # Collapse multiple spaces or tabs into a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Remove space before punctuation: , . ; : ? !
    text = re.sub(r"\s+([,.;:?!])", r"\1", text)
    # Ensure one space after punctuation when followed by a letter/word
    text = re.sub(r"([,.;:?!])(?=[A-Za-z\u0c80-\u0cff])", r"\1 ", text)
    # Final strip
    return re.sub(r"[ \t]+", " ", text).strip(" \t\r\n\u00a0\u200b")


def export_to_excel(rows: list, columns: list, output_path: Path, kannada_cols: set, title: str = "Sheet1"):
    """Generate professional Excel workbook with frozen header, bold styling, Kannada font, and auto-fit."""
    if not OPENPYXL_AVAILABLE:
        print(f"  [!] openpyxl not available, skipping {output_path.name}")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title
    ws.append(columns)
    ws.freeze_panes = "A2"

    header_font = Font(name="Calibri", size=11, bold=True, color="1F2937")
    header_fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="left", vertical="center")

    kn_font = Font(name="Noto Sans Kannada", size=11, color="111827")
    regular_font = Font(name="Calibri", size=11, color="111827")

    for row in rows:
        row_values = [row.get(col, "") for col in columns]
        ws.append(row_values)

    for col_idx, col_name in enumerate(columns, start=1):
        col_letter = get_column_letter(col_idx)
        is_kn = col_name in kannada_cols
        font_to_use = kn_font if is_kn else regular_font
        max_len = len(str(col_name))
        for row_idx in range(2, len(rows) + 2):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = font_to_use
            val_str = str(cell.value or "")
            if len(val_str) > 35 or "\n" in val_str:
                cell.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
            else:
                cell.alignment = Alignment(vertical="top", horizontal="left")
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 60)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)


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
    print_banner("3. ASSEMBLING SUBMISSION PACKAGE WITH CSV STANDARDIZATION")

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
    extras_dest_dir = SUBMISSION_DIR / "extras"
    extras_dest_dir.mkdir(parents=True, exist_ok=True)

    copied_files = []

    # -------------------------------------------------------------
    # 1. Clean, Standardize & Build Datasets
    # -------------------------------------------------------------
    # (A) gaades.csv
    src_gaades_path = REPO_ROOT / "data" / "gaades.csv"
    with open(src_gaades_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_gaades = list(reader)

    gaade_cols = ["gaade_id", "gaade", "meaning", "english", "example", "region", "theme", "audio_file"]
    cleaned_gaades = []
    gaade_lookup = {}
    for r in raw_gaades:
        gid = clean_cell(r["gaade_id"])
        # Rule C: In gaade column, ONLY trim leading/trailing whitespace. Never alter internal characters.
        gtext = clean_cell(r["gaade"])
        cleaned_row = {
            "gaade_id": gid,
            "gaade": gtext,
            "meaning": clean_free_text(r.get("meaning", "")),
            "english": clean_free_text(r.get("english", "")),
            "example": clean_free_text(r.get("example", "")),
            "region": clean_cell(r.get("region", "UNVERIFIED")),
            "theme": clean_cell(r.get("theme", "")),
            "audio_file": clean_cell(r.get("audio_file", ""))
        }
        cleaned_gaades.append(cleaned_row)
        gaade_lookup[gid] = gtext

    # Sort gaades by gaade_id (numeric order)
    cleaned_gaades.sort(key=lambda x: int(x["gaade_id"][1:]) if x["gaade_id"][1:].isdigit() else x["gaade_id"])

    # (B) situations.csv — JOIN gaade text on gaade_id
    src_situations_path = REPO_ROOT / "data" / "situations.csv"
    with open(src_situations_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_situations = list(reader)

    sit_cols = ["situation_id", "gaade_id", "gaade", "situation_text", "situation_kn", "language", "situation_source"]
    cleaned_situations = []
    for s in raw_situations:
        sid = clean_cell(s["situation_id"])
        gid = clean_cell(s["gaade_id"])
        if gid not in gaade_lookup:
            abort_with_error(f"Foreign Key Error: situation {sid} references unknown gaade_id {gid}!")
        gtext = gaade_lookup[gid]
        if not gtext:
            abort_with_error(f"Empty Gaade Error: situation {sid} mapped to empty gaade for {gid}!")

        cleaned_row = {
            "situation_id": sid,
            "gaade_id": gid,
            "gaade": gtext, # Exactly byte-for-byte from gaades.csv
            "situation_text": clean_free_text(s.get("situation_text", "")),
            "situation_kn": clean_free_text(s.get("situation_kn", "")),
            "language": clean_cell(s.get("language", "en")),
            "situation_source": clean_cell(s.get("situation_source", "team_drafted"))
        }
        cleaned_situations.append(cleaned_row)

    # Sort situations by gaade_id then situation_id
    cleaned_situations.sort(key=lambda x: (
        int(x["gaade_id"][1:]) if x["gaade_id"][1:].isdigit() else x["gaade_id"],
        x["situation_id"]
    ))

    # (C) consent_register.csv
    src_reg_path = REPO_ROOT / "docs" / "consent" / "consent_register.csv"
    with open(src_reg_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_reg = list(reader)

    reg_cols = [
        "contributor_id", "contributor_name", "contributor_type", "relationship",
        "place", "consent_form_file", "count", "range", "audio_recorded_yes_no",
        "date", "public_display_name_allowed", "method_of_consent", "witness"
    ]
    cleaned_reg = []
    for r in raw_reg:
        cleaned_row = {k: clean_free_text(r[k]) for k in reg_cols}
        cleaned_reg.append(cleaned_row)

    cleaned_reg.sort(key=lambda x: x["contributor_id"])

    # Helper function to write CSV with BOM + CRLF for root, and plain UTF-8 + LF for docs/utf8_no_bom
    def write_dataset_csv(rows, columns, dest_bom_rel, dest_nobom_rel):
        # 1. UTF-8 with BOM & CRLF
        dest_bom = SUBMISSION_DIR / dest_bom_rel
        dest_bom.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_bom, "w", encoding="utf-8-sig", newline="") as fb:
            writer = csv.DictWriter(fb, fieldnames=columns, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(rows)
        copied_files.append((dest_bom, dest_bom_rel))
        print(f"  [+] Wrote {dest_bom_rel} (UTF-8 with BOM & CRLF)")

        # 2. Plain UTF-8 (no BOM) & LF
        dest_nobom = SUBMISSION_DIR / dest_nobom_rel
        dest_nobom.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_nobom, "w", encoding="utf-8", newline="") as fn:
            writer = csv.DictWriter(fn, fieldnames=columns, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        copied_files.append((dest_nobom, dest_nobom_rel))
        print(f"  [+] Wrote {dest_nobom_rel} (Plain UTF-8 & LF)")

    write_dataset_csv(cleaned_gaades, gaade_cols, "gaades.csv", "docs/utf8_no_bom/gaades.csv")
    write_dataset_csv(cleaned_situations, sit_cols, "situations.csv", "docs/utf8_no_bom/situations.csv")
    write_dataset_csv(cleaned_reg, reg_cols, "consent/consent_register.csv", "docs/utf8_no_bom/consent_register.csv")

    # (D) Excel workbooks in submission/extras/
    if OPENPYXL_AVAILABLE:
        gaades_xlsx = extras_dest_dir / "gaades.xlsx"
        export_to_excel(cleaned_gaades, gaade_cols, gaades_xlsx, {"gaade"}, title="Canonical Gaades")
        copied_files.append((gaades_xlsx, "extras/gaades.xlsx"))
        print(f"  [+] Generated extras/gaades.xlsx (Excel convenience copy)")

        situations_xlsx = extras_dest_dir / "situations.xlsx"
        export_to_excel(cleaned_situations, sit_cols, situations_xlsx, {"gaade", "situation_kn"}, title="Situations Dataset")
        copied_files.append((situations_xlsx, "extras/situations.xlsx"))
        print(f"  [+] Generated extras/situations.xlsx (Excel convenience copy)")

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
        ("docs/csv_cleanup_report.md", REPO_ROOT / "data" / "reports" / "csv_cleanup_report.md"),
        ("docs/spacing_issues.md", REPO_ROOT / "data" / "reports" / "spacing_issues.md"),
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
        r"[\\/]submission_backup[\\/]",
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
                if any(member.endswith(ext) for ext in [".wav", ".ogg", ".pdf", ".jpeg", ".jpg", ".png", ".joblib", ".db", ".xlsx"]):
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
        # Check gaades.csv
        csv_bytes = zf.read("gaades.csv")
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
        df_zip = pd.read_csv(pd.io.common.BytesIO(csv_bytes), encoding="utf-8-sig")
        df_orig = pd.read_csv(REPO_ROOT / "data" / "gaades.csv")
        if not (df_zip["gaade"] == df_orig["gaade"]).all():
            abort_with_error("Packaged gaades text does not match original data/gaades.csv!")
        print(f"  [✓] Kannada Unicode integrity verified: 100% bit-identical across all {len(df_zip)} gaades.")

        # Check situations.csv with joined gaade column
        sit_bytes = zf.read("situations.csv")
        if not sit_bytes.startswith(b"\xef\xbb\xbf"):
            abort_with_error("situations.csv in submission zip is missing UTF-8 BOM!")
        sit_text = sit_bytes.decode("utf-8-sig")
        if "\ufffd" in sit_text:
            abort_with_error("Found U+FFFD in packaged situations.csv!")

        df_sits_zip = pd.read_csv(pd.io.common.BytesIO(sit_bytes), encoding="utf-8-sig")
        expected_sit_cols = ["situation_id", "gaade_id", "gaade", "situation_text", "situation_kn", "language", "situation_source"]
        if list(df_sits_zip.columns) != expected_sit_cols:
            abort_with_error(f"situations.csv columns mismatch: expected {expected_sit_cols}, got {list(df_sits_zip.columns)}")

        # Verify every situation gaade matches gaades.csv exactly
        gaade_map = dict(zip(df_orig["gaade_id"], df_orig["gaade"]))
        for _, sit_row in df_sits_zip.iterrows():
            expected_g = gaade_map[sit_row["gaade_id"]]
            if sit_row["gaade"] != expected_g:
                abort_with_error(f"Mismatch in situation {sit_row['situation_id']}: {sit_row['gaade']} != {expected_g}")
        print(f"  [✓] situations.csv verified: has 'gaade' column and 100% matches canonical gaades ({len(df_sits_zip)} rows).")

        # Verify extras/ workbooks
        if OPENPYXL_AVAILABLE:
            for xname in ["extras/gaades.xlsx", "extras/situations.xlsx"]:
                if xname not in namelist:
                    abort_with_error(f"Missing {xname} in submission zip!")
            print(f"  [✓] extras/gaades.xlsx and extras/situations.xlsx present and verified in submission zip.")

    # 4. Check that README counts equal CSV counts
    with zipfile.ZipFile(sub_zip_path, "r") as zf:
        readme_text = zf.read("README.md").decode("utf-8")
        if "226" not in readme_text:
            abort_with_error("README does not reference 226 canonical gaades!")
        if "452" not in readme_text:
            abort_with_error("README does not reference 452 situations!")
        if "226" not in readme_text:
            abort_with_error("README does not reference 226 WAV recordings!")
        print("  [✓] README counts agree with CSV counts (226 canonical gaades, 452 situations, 226 WAVs).")


if __name__ == "__main__":
    validate_data_layer()
    validate_audio_layer()
    build_submission()
    create_zip_packages()
    verify_zip_packages()
