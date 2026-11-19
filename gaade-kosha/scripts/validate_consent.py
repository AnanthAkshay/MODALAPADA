# -*- coding: utf-8 -*-
"""
Consent Register & Evidence Validator
Validates that every row in docs/consent/consent_register.csv has valid metadata,
and verifies that referenced evidence files actually exist on disk.
"""

import os
import sys
import hashlib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def validate_consent():
    register_path = BASE_DIR / "docs" / "consent" / "consent_register.csv"
    if not register_path.is_file():
        print(f"[FAIL] Missing consent register at {register_path}")
        return False

    df = pd.read_csv(register_path)
    print(f"[INFO] Loaded {len(df)} records from {register_path.name}")

    required_cols = [
        "contributor_id", "contributor_name", "contributor_type", "relationship",
        "place", "consent_form_file", "date", "public_display_name_allowed",
        "method_of_consent", "witness"
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"[FAIL] Missing required columns in consent_register.csv: {missing_cols}")
        return False

    all_valid = True
    for idx, row in df.iterrows():
        cid = row["contributor_id"]
        cname = row["contributor_name"]
        efile = row["consent_form_file"]
        
        # Check evidence file
        full_path = BASE_DIR / efile
        if not full_path.is_file():
            print(f"[FAIL] Record {cid} ({cname}) specifies missing evidence file: {efile}")
            all_valid = False
        else:
            with open(full_path, "rb") as f:
                sha = hashlib.sha256(f.read()).hexdigest()
            print(f"[PASS] {cid} - {cname:<16} | {efile} (SHA-256: {sha[:12]}...)")

    if all_valid:
        print(f"\n[SUCCESS] All {len(df)} consent records validated with verifiable on-disk evidence.")
    return all_valid

if __name__ == "__main__":
    success = validate_consent()
    sys.exit(0 if success else 1)

