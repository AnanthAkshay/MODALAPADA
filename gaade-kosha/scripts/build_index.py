# -*- coding: utf-8 -*-
"""
Index Precomputation Script for Gaade Kosha (Problem 2, Modalapada 2.0).
Embeds per gaade:
- Composite text: English meaning + Kannada meaning + usage context + theme + situations
- Each situation separately (for max-sim retrieval)
Saves to data/index/{backend_name}/:
- gaade_vectors.npy
- situation_vectors.npy
- index_meta.json
- vectorizer.joblib (for tfidf)
- bm25.joblib (for lexical search)
CRITICAL CONSTRAINT: Never indexes heldout_situations.csv!
"""

import os
import sys
import csv
import json
import time
import argparse
import numpy as np
import joblib

# Ensure backend package is in path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.config import settings
from backend.app.embeddings import TfidfEmbeddingProvider, get_embedding_provider
from rank_bm25 import BM25Okapi

DATA_DIR = settings.DATA_DIR
INDEX_ROOT = os.path.join(DATA_DIR, 'index')

def tokenize_for_bm25(text: str) -> list:
    """Tokenize text into lower-case words and Kannada character n-grams."""
    import re
    # Word tokens
    words = re.findall(r'\b\w+\b', text.lower())
    # Subword character n-grams for Kannada/Kanglish morphological matching
    kannada_chars = re.findall(r'[\u0C80-\u0CFF]+', text)
    kn_ngrams = []
    for chunk in kannada_chars:
        for n in (3, 4):
            for i in range(len(chunk) - n + 1):
                kn_ngrams.append(chunk[i:i + n])
    return words + kn_ngrams

def build_index_for_backend(backend_name: str = "tfidf", force: bool = False):
    print(f"\n==========================================")
    print(f"Building index for backend: {backend_name}")
    print(f"==========================================")
    
    out_dir = os.path.join(INDEX_ROOT, backend_name)
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load canonical gaades
    gaades_csv = os.path.join(DATA_DIR, 'gaades.csv')
    with open(gaades_csv, 'r', encoding='utf-8') as f:
        gaades = list(csv.DictReader(f))
    print(f"Loaded {len(gaades)} canonical gaades from {gaades_csv}")
    
    # 2. Load canonical situations (NEVER HELDOUT!)
    situations_csv = os.path.join(DATA_DIR, 'situations.csv')
    with open(situations_csv, 'r', encoding='utf-8') as f:
        situations = list(csv.DictReader(f))
    print(f"Loaded {len(situations)} situations from {situations_csv} (Held-out set strictly excluded)")
    
    # Map gaade_id -> list of situations
    gaade_sits = {}
    for s in situations:
        gid = s['gaade_id']
        gaade_sits.setdefault(gid, []).append(s)
        
    gaade_ids = [g['gaade_id'] for g in gaades]
    
    # Construct texts
    gaade_composite_texts = []
    all_situation_texts = []
    situation_meta = []  # (sit_id, gid)
    bm25_corpus_texts = []
    
    for g in gaades:
        gid = g['gaade_id']
        sits = gaade_sits.get(gid, [])
        sit_texts = " ".join([f"{s['situation_text']} {s['situation_kn']}" for s in sits])
        
        comp_text = (
            f"{g['english']}. Meaning: {g['meaning']}. Theme: {g['theme']}. "
            f"Proverb: {g['gaade']}. Context situations: {sit_texts}"
        )
        gaade_composite_texts.append(comp_text)
        bm25_corpus_texts.append(comp_text)
        
        for s in sits:
            all_situation_texts.append(f"{s['situation_text']} {s['situation_kn']} {g['english']}")
            situation_meta.append({'situation_id': s['situation_id'], 'gaade_id': gid})
            
    # 3. Fit or Load Embedding Provider
    if backend_name == "tfidf":
        provider = TfidfEmbeddingProvider()
        print("Fitting TF-IDF vectorizer on composite + situation texts...")
        train_texts = gaade_composite_texts + all_situation_texts
        provider.fit(train_texts)
        vec_path = os.path.join(out_dir, "vectorizer.joblib")
        provider.save(vec_path)
    else:
        provider, actual = get_embedding_provider(backend_name)
        if actual != backend_name:
            print(f"Warning: Requested backend '{backend_name}' not available. Active: '{actual}'. Skipping.")
            return False
            
    # 4. Generate Embeddings
    print("Computing gaade composite embeddings...")
    t0 = time.time()
    gaade_vectors = provider.embed_texts(gaade_composite_texts)
    print(f"Computed gaade vectors: shape {gaade_vectors.shape} in {time.time()-t0:.2f}s")
    
    print("Computing individual situation embeddings...")
    t1 = time.time()
    situation_vectors = provider.embed_texts(all_situation_texts)
    print(f"Computed situation vectors: shape {situation_vectors.shape} in {time.time()-t1:.2f}s")
    
    # Save vectors (compressed for git and uncompressed for legacy compatibility)
    np.save(os.path.join(out_dir, "gaade_vectors.npy"), gaade_vectors)
    np.save(os.path.join(out_dir, "situation_vectors.npy"), situation_vectors)
    np.savez_compressed(os.path.join(out_dir, "gaade_vectors.npz"), vectors=gaade_vectors)
    np.savez_compressed(os.path.join(out_dir, "situation_vectors.npz"), vectors=situation_vectors)
    
    # 5. Build BM25 Index
    print("Building BM25 index over proverbs and situations...")
    tokenized_corpus = [tokenize_for_bm25(doc) for doc in bm25_corpus_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    joblib.dump(bm25, os.path.join(out_dir, "bm25.joblib"))
    print("Saved BM25 model.")
    
    # 6. Save Metadata
    meta = {
        "backend": backend_name,
        "num_gaades": len(gaade_ids),
        "num_situations": len(situation_meta),
        "dimension": int(gaade_vectors.shape[1]),
        "gaade_ids": gaade_ids,
        "situations": situation_meta,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(out_dir, "index_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        
    print(f"Index successfully precomputed and saved in {out_dir}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Precompute semantic index for Gaade Kosha.")
    parser.add_argument("--backend", default="tfidf", choices=["tfidf", "local", "api", "all"], help="Embedding backend.")
    parser.add_argument("--force", action="store_true", help="Force rebuild.")
    args = parser.parse_args()
    
    backends = ["tfidf"] if args.backend == "tfidf" else ([args.backend] if args.backend != "all" else ["tfidf", "local", "api"])
    
    for b in backends:
        try:
            build_index_for_backend(b, force=args.force)
        except Exception as e:
            print(f"Failed to build index for backend {b}: {e}")

if __name__ == "__main__":
    main()

