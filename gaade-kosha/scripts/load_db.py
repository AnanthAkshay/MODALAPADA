# -*- coding: utf-8 -*-
"""
Database Loader Script for Gaade Kosha (Problem 2, Modalapada 2.0).
Idempotent loader importing data from CSVs into SQLite database with foreign key integrity.
Reads CSVs using utf-8-sig (BOM-tolerant), rejects broken gaade_id references, and prints an audit summary.
"""

import os
import sys
import csv
import time
import argparse
from typing import Dict, List, Set, Any

# Ensure backend package is in python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.config import settings
from backend.app.db import get_db_connection, init_db

def load_data(
    db_path: str = settings.DATABASE_PATH,
    data_dir: str = settings.DATA_DIR,
    drop_existing: bool = True
) -> Dict[str, Any]:
    start_time = time.time()
    
    gaades_csv = os.path.join(data_dir, 'gaades.csv')
    provenance_csv = os.path.join(data_dir, 'gaade_provenance.csv')
    situations_csv = os.path.join(data_dir, 'situations.csv')
    
    for path, name in [(gaades_csv, 'gaades.csv'), (provenance_csv, 'gaade_provenance.csv'), (situations_csv, 'situations.csv')]:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Required CSV not found: {path}")
            
    print(f"=== INITIALIZING SQLITE DATABASE ===")
    print(f"Database Path: {db_path}")
    print(f"Data Directory: {data_dir}")
    
    init_db(db_path, drop_existing=drop_existing)
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    loaded_gaades: Set[str] = set()
    gaades_inserted = 0
    
    # 1. Load gaades.csv
    print("\n1. Loading gaades.csv...")
    with open(gaades_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gid = row.get('gaade_id', '').strip()
            if not gid:
                continue
            cur.execute("""
            INSERT OR REPLACE INTO gaades (gaade_id, gaade, meaning, english, example, region, theme, audio_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                gid,
                row.get('gaade', '').strip(),
                row.get('meaning', '').strip(),
                row.get('english', '').strip(),
                row.get('example', '').strip(),
                row.get('region', 'UNVERIFIED').strip(),
                row.get('theme', '').strip(),
                row.get('audio_file', 'MISSING').strip()
            ))
            loaded_gaades.add(gid)
            gaades_inserted += 1
            
    print(f"Loaded {gaades_inserted} canonical proverbs into gaades table.")
    
    # 2. Load gaade_provenance.csv (Reject broken FKs)
    print("\n2. Loading gaade_provenance.csv...")
    provenance_inserted = 0
    provenance_rejected: List[Dict[str, str]] = []
    
    with open(provenance_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gid = row.get('gaade_id', '').strip()
            if not gid:
                continue
            if gid not in loaded_gaades:
                provenance_rejected.append({
                    'gaade_id': gid,
                    'reason': f"Foreign key violation: {gid} is not a canonical gaade in gaades table",
                    'duplicate_of': row.get('duplicate_of', '')
                })
                continue
                
            pdf_num = int(row.get('source_pdf_number', 0)) if row.get('source_pdf_number', '').isdigit() else 0
            cur.execute("""
            INSERT OR REPLACE INTO provenance (gaade_id, source_pdf_number, source_type, verification_status, duplicate_of, consent_ref, notes, example_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                gid,
                pdf_num,
                row.get('source_type', '').strip(),
                row.get('verification_status', '').strip(),
                row.get('duplicate_of', '').strip() or None,
                row.get('consent_ref', '').strip(),
                row.get('notes', '').strip(),
                row.get('example_source', 'team_drafted').strip()
            ))
            provenance_inserted += 1
            
    print(f"Loaded {provenance_inserted} provenance records. Rejected {len(provenance_rejected)} non-canonical rows.")
    
    # 3. Load situations.csv (Reject broken FKs)
    print("\n3. Loading situations.csv...")
    situations_inserted = 0
    situations_rejected: List[Dict[str, str]] = []
    
    with open(situations_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row.get('situation_id', '').strip()
            gid = row.get('gaade_id', '').strip()
            if not sid or not gid:
                continue
            if gid not in loaded_gaades:
                situations_rejected.append({
                    'situation_id': sid,
                    'gaade_id': gid,
                    'reason': f"Foreign key violation: {gid} is not in gaades table"
                })
                continue
                
            cur.execute("""
            INSERT OR REPLACE INTO situations (situation_id, gaade_id, situation_text, situation_kn, language, situation_source)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (
                sid,
                gid,
                row.get('situation_text', '').strip(),
                row.get('situation_kn', '').strip(),
                row.get('language', 'en').strip(),
                row.get('situation_source', 'team_drafted').strip()
            ))
            situations_inserted += 1
            
    print(f"Loaded {situations_inserted} situations. Rejected {len(situations_rejected)} rows.")
    
    conn.commit()
    conn.close()
    
    elapsed = time.time() - start_time
    summary = {
        'database_path': db_path,
        'gaades_inserted': gaades_inserted,
        'provenance_inserted': provenance_inserted,
        'provenance_rejected': len(provenance_rejected),
        'situations_inserted': situations_inserted,
        'situations_rejected': len(situations_rejected),
        'elapsed_seconds': round(elapsed, 4)
    }
    
    print("\n=== DATABASE LOAD SUMMARY ===")
    print(f"- Gaades loaded: {gaades_inserted}")
    print(f"- Provenance records loaded: {provenance_inserted} (Rejected: {len(provenance_rejected)})")
    print(f"- Situations loaded: {situations_inserted} (Rejected: {len(situations_rejected)})")
    print(f"- Execution Time: {summary['elapsed_seconds']} s")
    print("Database successfully synchronized.")
    
    return summary

def main():
    parser = argparse.ArgumentParser(description="Load Gaade Kosha datasets into SQLite.")
    parser.add_argument('--db-path', default=settings.DATABASE_PATH, help="Path to SQLite database.")
    parser.add_argument('--data-dir', default=settings.DATA_DIR, help="Path to CSV data directory.")
    parser.add_argument('--no-drop', action='store_true', help="Do not drop existing tables (test idempotency).")
    
    args = parser.parse_args()
    load_data(
        db_path=os.path.abspath(args.db_path),
        data_dir=os.path.abspath(args.data_dir),
        drop_existing=not args.no_drop
    )

if __name__ == '__main__':
    main()

