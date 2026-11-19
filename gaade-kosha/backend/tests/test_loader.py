# -*- coding: utf-8 -*-
"""
Tests for Gaade Kosha SQLite Database Loader.
Verifies idempotency, foreign key enforcement, and rejection of broken references.
"""

import os
import tempfile
import pytest
from scripts.load_db import load_data
from backend.app.db import get_db_connection, get_stats

def test_loader_execution_and_counts():
    """Verify clean database loading and expected record counts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_gaade_kosha.db")
        summary = load_data(db_path=test_db, drop_existing=True)
        
        assert summary['gaades_inserted'] == 226, f"Expected 226 gaades, got {summary['gaades_inserted']}"
        assert summary['provenance_inserted'] == 226, f"Expected 226 provenance records, got {summary['provenance_inserted']}"
        assert summary['provenance_rejected'] == 26, f"Expected 26 duplicate rows rejected, got {summary['provenance_rejected']}"
        assert summary['situations_inserted'] == 452, f"Expected 452 situations, got {summary['situations_inserted']}"
        assert summary['situations_rejected'] == 0, f"Expected 0 situations rejected, got {summary['situations_rejected']}"
        
        conn = get_db_connection(test_db)
        gaades_cnt, sits_cnt = get_stats(conn)
        conn.close()
        
        assert gaades_cnt == 226
        assert sits_cnt == 452

def test_loader_idempotency():
    """Verify that running the loader multiple times does not duplicate or corrupt rows."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_gaade_kosha.db")
        # Run 1
        load_data(db_path=test_db, drop_existing=True)
        # Run 2 with no drop (incremental / overwrite)
        load_data(db_path=test_db, drop_existing=False)
        
        conn = get_db_connection(test_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM gaades;")
        assert cur.fetchone()[0] == 226
        cur.execute("SELECT COUNT(*) FROM provenance;")
        assert cur.fetchone()[0] == 226
        cur.execute("SELECT COUNT(*) FROM situations;")
        assert cur.fetchone()[0] == 452
        conn.close()

