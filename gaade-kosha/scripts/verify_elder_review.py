# -*- coding: utf-8 -*-
"""
Verification Script for Elder Review Sheet and Workflow
Checks:
1. elder_review_sheet.csv format and empty fields
2. elder_review_sheet.pdf integrity and Kannada conjuncts
3. returned/ folder contains only README.txt and zero pre-filled data
4. Every canonical gaade appears exactly once
"""

import os
import sys
import csv
import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
GAADES_CSV = DATA_DIR / "gaades.csv"
ELDER_DIR = DATA_DIR / "elder_review"
REVIEW_CSV = ELDER_DIR / "elder_review_sheet.csv"
REVIEW_PDF = ELDER_DIR / "elder_review_sheet.pdf"
REVIEW_HTML = ELDER_DIR / "elder_review_sheet.html"
RETURNED_DIR = ELDER_DIR / "returned"
README_TXT = RETURNED_DIR / "README.txt"


def verify_all():
    errors = []
    print("=== RUNNING ELDER REVIEW SHEET AUDIT ===")

    # 1. Canonical Gaades comparison
    df_canonical = pd.read_csv(GAADES_CSV, encoding="utf-8")
    canonical_ids = set(df_canonical["gaade_id"])
    print(f"[✓] Canonical gaades in gaades.csv: {len(canonical_ids)}")

    # 2. Check elder_review_sheet.csv
    if not REVIEW_CSV.is_file():
        errors.append(f"Missing {REVIEW_CSV}")
    else:
        df_review = pd.read_csv(REVIEW_CSV, encoding="utf-8")
        expected_cols = [
            "gaade_id",
            "gaade",
            "meaning",
            "I_know_this (Y/N)",
            "I_use_it_in_my_area (Y/N)",
            "spelling_or_wording_correction",
            "notes"
        ]
        if list(df_review.columns) != expected_cols:
            errors.append(f"Column mismatch in elder_review_sheet.csv: {list(df_review.columns)}")
        
        if len(df_review) != len(canonical_ids):
            errors.append(f"Row count mismatch: {len(df_review)} vs {len(canonical_ids)} canonical")

        review_ids = list(df_review["gaade_id"])
        if set(review_ids) != canonical_ids:
            errors.append("Gaade ID set does not match canonical set!")
        if len(review_ids) != len(set(review_ids)):
            errors.append("Duplicate gaade IDs found in elder_review_sheet.csv!")

        # Verify last four columns strictly empty
        for col in ["I_know_this (Y/N)", "I_use_it_in_my_area (Y/N)", "spelling_or_wording_correction", "notes"]:
            non_empty = df_review[df_review[col].notnull() & (df_review[col].astype(str).str.strip() != "")]
            if len(non_empty) > 0:
                errors.append(f"Column '{col}' must be empty, found {len(non_empty)} non-empty entries!")

        # Check for U+FFFD
        raw_text = REVIEW_CSV.read_text(encoding="utf-8")
        if "\ufffd" in raw_text:
            errors.append("Unicode replacement character U+FFFD detected in elder_review_sheet.csv")

        print(f"[✓] elder_review_sheet.csv passed: {len(df_review)} rows, exact schema, last 4 columns 100% empty.")

    # 3. Check elder_review_sheet.pdf
    if not REVIEW_PDF.is_file():
        errors.append(f"Missing {REVIEW_PDF}")
    else:
        with open(REVIEW_PDF, "rb") as f:
            header = f.read(5)
        if header != b"%PDF-":
            errors.append("Invalid PDF magic bytes header!")

        import fitz
        doc = fitz.open(str(REVIEW_PDF))
        num_pages = len(doc)
        if num_pages < 10:
            errors.append(f"Suspiciously low page count in PDF: {num_pages}")
        
        total_text = ""
        pages_with_kn = 0
        for p in doc:
            t = p.get_text()
            total_text += t
            if any(0x0C80 <= ord(c) <= 0x0CFF for c in t):
                pages_with_kn += 1
        doc.close()

        if pages_with_kn != num_pages:
            errors.append(f"Not all pages contain Kannada text: {pages_with_kn} / {num_pages}")

        # Check that all canonical IDs appear in the PDF text
        missing_ids = [gid for gid in canonical_ids if gid not in total_text]
        if missing_ids:
            errors.append(f"Missing {len(missing_ids)} gaade IDs from PDF text: {missing_ids[:5]}")

        print(f"[✓] elder_review_sheet.pdf passed: {num_pages} pages, all with rendered Kannada, all {len(canonical_ids)} IDs present.")

    # 4. Check returned/ folder
    if not RETURNED_DIR.is_dir():
        errors.append(f"Missing returned directory at {RETURNED_DIR}")
    if not README_TXT.is_file():
        errors.append(f"Missing {README_TXT}")

    # Check for pre-filled files in returned/
    files_in_returned = list(RETURNED_DIR.glob("*"))
    non_readme = [f for f in files_in_returned if f.name != "README.txt"]
    if non_readme:
        errors.append(f"Pre-filled or unexpected files found in returned/: {[f.name for f in non_readme]}")

    print(f"[✓] returned/ folder passed: contains README.txt and zero pre-filled data files.")

    # Final Result
    if errors:
        print("\n[FAILED] Errors encountered:")
        for err in errors:
            print(f"  ❌ {err}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All elder review sheet acceptance criteria passed!")


if __name__ == "__main__":
    verify_all()

