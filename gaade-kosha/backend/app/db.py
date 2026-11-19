# -*- coding: utf-8 -*-
"""
Database Access Layer for Gaade Kosha (SQLite).
Enforces foreign keys, creates indexes, and provides query helpers.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from backend.app.config import settings

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    Configures row_factory for dict-like access and enables foreign keys.
    """
    path = db_path or settings.DATABASE_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: Optional[str] = None, drop_existing: bool = False) -> None:
    """
    Initialize SQLite schema for gaades, situations, and provenance.
    """
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    if drop_existing:
        cur.execute("DROP TABLE IF EXISTS situations;")
        cur.execute("DROP TABLE IF EXISTS provenance;")
        cur.execute("DROP TABLE IF EXISTS gaades;")
    
    # 1. Gaades Table (Canonical Kannada Proverbs)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gaades (
        gaade_id TEXT PRIMARY KEY,
        gaade TEXT NOT NULL,
        meaning TEXT NOT NULL,
        english TEXT NOT NULL,
        example TEXT,
        region TEXT NOT NULL,
        theme TEXT NOT NULL,
        audio_file TEXT NOT NULL
    );
    """)
    
    # 2. Provenance Table (Ethics & Verification Audit)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS provenance (
        gaade_id TEXT PRIMARY KEY,
        source_pdf_number INTEGER NOT NULL,
        source_type TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        duplicate_of TEXT,
        consent_ref TEXT NOT NULL,
        notes TEXT,
        example_source TEXT,
        FOREIGN KEY (gaade_id) REFERENCES gaades(gaade_id) ON DELETE CASCADE
    );
    """)
    
    # 3. Situations Table (Contextual Scenarios)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS situations (
        situation_id TEXT PRIMARY KEY,
        gaade_id TEXT NOT NULL,
        situation_text TEXT NOT NULL,
        situation_kn TEXT NOT NULL,
        language TEXT NOT NULL,
        situation_source TEXT NOT NULL,
        FOREIGN KEY (gaade_id) REFERENCES gaades(gaade_id) ON DELETE CASCADE
    );
    """)
    
    # Indexes for rapid retrieval
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gaades_theme ON gaades(theme);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gaades_region ON gaades(region);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_situations_gaade_id ON situations(gaade_id);")
    
    conn.commit()
    conn.close()

def get_stats(conn: sqlite3.Connection) -> Tuple[int, int]:
    """Return count of (gaades, situations)."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM gaades;")
    gaades_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM situations;")
    sits_count = cur.fetchone()[0]
    return gaades_count, sits_count

def list_gaades(
    conn: sqlite3.Connection,
    theme: Optional[str] = None,
    region: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Query gaades with optional filtering by theme, region, and search term q.
    Returns (total_matching_count, items).
    """
    cur = conn.cursor()
    where_clauses = []
    params: List[Any] = []
    
    if theme:
        where_clauses.append("LOWER(theme) = LOWER(?)")
        params.append(theme)
    if region:
        where_clauses.append("LOWER(region) = LOWER(?)")
        params.append(region)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        where_clauses.append("(gaade LIKE ? OR meaning LIKE ? OR english LIKE ?)")
        params.extend([search_term, search_term, search_term])
        
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    # Total count
    count_sql = f"SELECT COUNT(*) FROM gaades {where_sql};"
    cur.execute(count_sql, params)
    total = cur.fetchone()[0]
    
    # Page items
    items_sql = f"""
    SELECT gaade_id, gaade, meaning, english, example, region, theme, audio_file
    FROM gaades
    {where_sql}
    ORDER BY gaade_id ASC
    LIMIT ? OFFSET ?;
    """
    page_params = params + [limit, offset]
    cur.execute(items_sql, page_params)
    rows = cur.fetchall()
    
    items = []
    for r in rows:
        item = dict(r)
        item['audio_url'] = f"/api/audio/{item['gaade_id']}" if item['audio_file'] != "MISSING" else None
        items.append(item)
        
    return total, items

def get_gaade_by_id(conn: sqlite3.Connection, gaade_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single gaade by ID, including its provenance and situation count.
    """
    cur = conn.cursor()
    cur.execute("""
    SELECT g.*, 
           p.source_pdf_number, p.source_type, p.verification_status, p.duplicate_of, p.consent_ref, p.notes,
           (SELECT COUNT(*) FROM situations s WHERE s.gaade_id = g.gaade_id) AS situations_count
    FROM gaades g
    LEFT JOIN provenance p ON g.gaade_id = p.gaade_id
    WHERE g.gaade_id = ?;
    """, (gaade_id,))
    row = cur.fetchone()
    if not row:
        return None
        
    res = dict(row)
    provenance = None
    if res.get('source_pdf_number') is not None:
        provenance = {
            'source_pdf_number': res.pop('source_pdf_number'),
            'source_type': res.pop('source_type'),
            'verification_status': res.pop('verification_status'),
            'duplicate_of': res.pop('duplicate_of'),
            'consent_ref': res.pop('consent_ref'),
            'notes': res.pop('notes')
        }
    else:
        for k in ['source_pdf_number', 'source_type', 'verification_status', 'duplicate_of', 'consent_ref', 'notes']:
            res.pop(k, None)
            
    res['provenance'] = provenance
    res['audio_url'] = f"/api/audio/{gaade_id}" if res['audio_file'] != "MISSING" else None
    return res

def get_situations_for_gaade(conn: sqlite3.Connection, gaade_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch situations for a given gaade. Returns None if the gaade does not exist.
    """
    cur = conn.cursor()
    # Check gaade existence first
    cur.execute("SELECT 1 FROM gaades WHERE gaade_id = ?;", (gaade_id,))
    if not cur.fetchone():
        return None
        
    cur.execute("""
    SELECT situation_id, gaade_id, situation_text, situation_kn, language, situation_source
    FROM situations
    WHERE gaade_id = ?
    ORDER BY situation_id ASC;
    """, (gaade_id,))
    return [dict(r) for r in cur.fetchall()]

def get_themes_summary(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Aggregate counts of gaades grouped by theme.
    """
    cur = conn.cursor()
    cur.execute("""
    SELECT theme, COUNT(*) AS count
    FROM gaades
    GROUP BY theme
    ORDER BY count DESC, theme ASC;
    """)
    return [dict(r) for r in cur.fetchall()]

