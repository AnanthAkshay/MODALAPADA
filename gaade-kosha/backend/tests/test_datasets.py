# -*- coding: utf-8 -*-
import csv
import os
import re

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
GAADES_CSV = os.path.join(DATA_DIR, 'gaades.csv')
SITUATIONS_CSV = os.path.join(DATA_DIR, 'situations.csv')
HELDOUT_CSV = os.path.join(DATA_DIR, 'eval', 'heldout_situations.csv')

def test_gaades_dataset():
    assert os.path.isfile(GAADES_CSV), "gaades.csv missing"
    with open(GAADES_CSV, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 226, f"Expected 226 canonical gaades, found {len(reader)}"
    for row in reader:
        assert row['gaade_id'].startswith('G')
        assert row['gaade'].strip()
        assert row['meaning'].strip()

def test_situations_dataset():
    assert os.path.isfile(SITUATIONS_CSV), "situations.csv missing"
    with open(SITUATIONS_CSV, 'r', encoding='utf-8') as f:
        situations = list(csv.DictReader(f))
    assert len(situations) == 452, f"Expected 452 situations (2 per gaade), found {len(situations)}"
    
    with open(GAADES_CSV, 'r', encoding='utf-8') as f:
        canonical_ids = set(r['gaade_id'] for r in csv.DictReader(f))
        
    counts = {}
    for row in situations:
        gid = row['gaade_id']
        assert gid in canonical_ids, f"Unknown gaade_id {gid}"
        counts[gid] = counts.get(gid, 0) + 1
        assert row['situation_text'].strip()
        assert row['situation_kn'].strip()
        assert row['language'] == 'en'
        assert row['situation_source'] == 'team_drafted'
        
    for gid in canonical_ids:
        assert counts.get(gid) == 2, f"Gaade {gid} does not have exactly 2 situations: {counts.get(gid)}"

def test_heldout_dataset():
    assert os.path.isfile(HELDOUT_CSV), "heldout_situations.csv missing"
    with open(HELDOUT_CSV, 'r', encoding='utf-8') as f:
        heldout = list(csv.DictReader(f))
    assert len(heldout) == 40, f"Expected 40 heldout situations, found {len(heldout)}"
    
    with open(GAADES_CSV, 'r', encoding='utf-8') as f:
        canonical_ids = set(r['gaade_id'] for r in csv.DictReader(f))
        
    seen = set()
    for row in heldout:
        assert row['gaade_id'] in canonical_ids
        assert row['gaade_id'] not in seen, f"Duplicate gaade_id in heldout: {row['gaade_id']}"
        seen.add(row['gaade_id'])
        assert row['split'] == 'heldout_test'
        assert row['situation_text'].strip()
        assert row['situation_kn'].strip()

def test_token_overlap():
    with open(SITUATIONS_CSV, 'r', encoding='utf-8') as f:
        situations = list(csv.DictReader(f))
        
    def tokenize(text):
        return set(re.findall(r'\b\w+\b', text.lower()))
        
    token_sets = [(r['situation_id'], tokenize(r['situation_text'])) for r in situations]
    for i in range(len(token_sets)):
        for j in range(i + 1, min(i + 30, len(token_sets))):
            s1_id, t1 = token_sets[i]
            s2_id, t2 = token_sets[j]
            inter = len(t1 & t2)
            union = len(t1 | t2)
            if union > 0:
                assert (inter / union) < 0.60, f"Overlap >= 0.60 between {s1_id} and {s2_id}"

def test_audio_dataset():
    base_dir = os.path.abspath(os.path.join(DATA_DIR, '..'))
    wav_dir = os.path.join(base_dir, 'audio', 'wav')
    unused_dir = os.path.join(base_dir, 'audio', 'wav_unused_duplicates')
    
    assert os.path.isdir(wav_dir), "audio/wav directory missing"
    assert os.path.isdir(unused_dir), "audio/wav_unused_duplicates missing"
    
    wav_files = [f for f in os.listdir(wav_dir) if f.endswith('.wav')]
    assert len(wav_files) == 224, f"Expected 224 canonical WAV files, found {len(wav_files)}"
    
    unused_files = [f for f in os.listdir(unused_dir) if f.endswith('.wav')]
    assert len(unused_files) == 26, f"Expected 26 unused duplicate WAV files, found {len(unused_files)}"
    
    # Check gaades.csv audio_file references
    with open(GAADES_CSV, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        
    for row in reader:
        gid = row['gaade_id']
        audio_file = row['audio_file']
        if gid in ("G251", "G252"):
            assert audio_file == "MISSING"
        else:
            assert audio_file == f"audio/wav/{gid}.wav"
            full_path = os.path.join(base_dir, audio_file)
            assert os.path.isfile(full_path), f"Audio file not found: {full_path}"


