# -*- coding: utf-8 -*-
"""
Embedding Provider Interface and Implementations for Gaade Kosha.
Supports three pluggable backends:
1. tfidf: scikit-learn hybrid word + subword char n-grams (2-5) (completely offline, 0 downloads).
2. local: sentence-transformers (LaBSE or multilingual-e5-base) via local path or hub.
3. api: Hosted multilingual API (Gemini text-embedding-004) with backoff retry.
Provides an automatic fallback chain: configured backend -> tfidf.
"""

import os
import re
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import numpy as np
import joblib

from backend.app.config import settings

logger = logging.getLogger("gaade_kosha_embeddings")

class EmbeddingProvider(ABC):
    """Abstract Base Class for text embedding models."""
    name: str = "base"

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of strings into a 2D float32 numpy array.
        Output vectors MUST be L2-normalized so dot product equals cosine similarity.
        """
        pass


class TfidfEmbeddingProvider(EmbeddingProvider):
    """
    Offline Hybrid TF-IDF Embedding Provider.
    Combines word n-grams (1-2) with character n-grams (2-5) for multilingual,
    morphological, and transliterated (Kanglish) matching without any external downloads.
    """
    name: str = "tfidf"

    def __init__(self, vectorizer_path: Optional[str] = None):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import FeatureUnion

        self.vectorizer_path = vectorizer_path
        self.vectorizer = None

        if vectorizer_path and os.path.isfile(vectorizer_path):
            try:
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info(f"Loaded existing TF-IDF vectorizer from {vectorizer_path}")
            except Exception as e:
                logger.warning(f"Failed to load vectorizer from {vectorizer_path}: {e}")

        if self.vectorizer is None:
            word_vec = TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True
            )
            char_vec = TfidfVectorizer(
                analyzer='char',
                ngram_range=(2, 5),
                min_df=1,
                sublinear_tf=True
            )
            self.union = FeatureUnion([
                ('word', word_vec),
                ('char', char_vec)
            ])
            self.vectorizer = self.union

    def fit(self, texts: List[str]):
        """Fit the vectorizer on the corpus."""
        self.vectorizer.fit(texts)

    def save(self, filepath: str):
        """Save fitted vectorizer to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(self.vectorizer, filepath)
        self.vectorizer_path = filepath
        logger.info(f"Saved TF-IDF vectorizer to {filepath}")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype=np.float32)
        X = self.vectorizer.transform(texts).toarray().astype(np.float32)
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return X / norms


class SentenceTransformersProvider(EmbeddingProvider):
    """
    Dense multilingual sentence embedding using sentence-transformers.
    Supports Kannada through models like LaBSE or multilingual-e5-base.
    """
    name: str = "local"

    def __init__(self, model_name_or_path: Optional[str] = None):
        self.model_name = (
            model_name_or_path
            or os.environ.get("MODEL_PATH")
            or os.environ.get("LOCAL_MODEL_NAME", "sentence-transformers/LaBSE")
        )
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            msg = (
                f"Failed to load local sentence-transformers model '{self.model_name}'. "
                f"Network or path error: {e}. If Hugging Face is unreachable, ensure model "
                f"is saved in MODEL_PATH or switch EMBEDDING_BACKEND=tfidf."
            )
            logger.error(msg)
            raise RuntimeError(msg) from e

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not self.model:
            raise RuntimeError("SentenceTransformer model is not loaded.")
        embs = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embs.astype(np.float32)


class ApiEmbeddingProvider(EmbeddingProvider):
    """
    Hosted API Embedding Provider (Google Gemini text-embedding-004).
    Batches texts and applies exponential backoff retry on transient errors.
    """
    name: str = "api"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("EMBEDDING_API_KEY")
        )
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY or EMBEDDING_API_KEY is not set.")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        import httpx
        if not texts:
            return np.empty((0, 768), dtype=np.float32)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={self.api_key}"
        all_embeddings = []
        batch_size = 16

        for i in range(0, len(texts), batch_size):
            chunk = texts[i:i + batch_size]
            requests_payload = [
                {
                    "model": "models/text-embedding-004",
                    "content": {"parts": [{"text": t}]}
                }
                for t in chunk
            ]

            max_retries = 3
            backoff = 1.0
            chunk_vectors = None

            for attempt in range(max_retries):
                try:
                    with httpx.Client(timeout=15.0) as client:
                        resp = client.post(url, json={"requests": requests_payload})
                    if resp.status_code == 200:
                        data = resp.json()
                        chunk_vectors = [e["values"] for e in data.get("embeddings", [])]
                        break
                    elif resp.status_code in (429, 503):
                        time.sleep(backoff)
                        backoff *= 2
                    else:
                        raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Gemini API embedding failed after {max_retries} attempts: {e}") from e
                    time.sleep(backoff)
                    backoff *= 2

            if not chunk_vectors:
                raise RuntimeError("Failed to retrieve embeddings from API response.")
            all_embeddings.extend(chunk_vectors)

        arr = np.array(all_embeddings, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms


def get_embedding_provider(
    requested_backend: Optional[str] = None,
    index_dir: Optional[str] = None
) -> Tuple[EmbeddingProvider, str]:
    """
    Factory creating the requested EmbeddingProvider with automatic fallback to TF-IDF.
    Returns: (provider_instance, actual_backend_name)
    """
    backend = (requested_backend or os.environ.get("EMBEDDING_BACKEND", "tfidf")).lower().strip()
    
    if backend == "local":
        try:
            provider = SentenceTransformersProvider()
            return provider, "local"
        except Exception as e:
            logger.warning(f"Local embedding backend unavailable: {e}. Falling back to 'tfidf'.")
            
    elif backend == "api":
        try:
            provider = ApiEmbeddingProvider()
            return provider, "api"
        except Exception as e:
            logger.warning(f"API embedding backend unavailable: {e}. Falling back to 'tfidf'.")

    # Fallback / Default: TF-IDF
    vec_path = None
    if index_dir:
        candidate = os.path.join(index_dir, "tfidf", "vectorizer.joblib")
        if os.path.isfile(candidate):
            vec_path = candidate

    if not vec_path:
        default_candidate = os.path.join(settings.DATA_DIR, "index", "tfidf", "vectorizer.joblib")
        if os.path.isfile(default_candidate):
            vec_path = default_candidate
    
    provider = TfidfEmbeddingProvider(vectorizer_path=vec_path)
    return provider, "tfidf"

