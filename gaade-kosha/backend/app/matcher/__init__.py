# -*- coding: utf-8 -*-
"""
Gaade Kosha Matcher Package.
Provides LLM-based semantic understanding as the primary matcher with resilient
offline TF-IDF + BM25 hybrid retrieval fallback.
"""

from backend.app.matcher.llm_matcher import (
    LLMMatcher,
    get_llm_matcher,
    LLMCandidateRegistry,
    SYSTEM_INSTRUCTION
)

import os
import re
import json
import joblib
import logging
import unicodedata
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from backend.app.config import settings
from backend.app.embeddings import get_embedding_provider, EmbeddingProvider
from backend.app.db import get_db_connection, get_gaade_by_id
from scripts.build_index import tokenize_for_bm25

logger = logging.getLogger("gaade_kosha_matcher")

# Common Kanglish (Kannada in Latin script) phonetic markers
KANGLISH_PATTERNS = re.compile(
    r'\b(beku|madu|mado|illa|gothilla|gottilla|yaaru|tumba|hege|idu|adu|nanna|nimma|'
    r'kelasa|mane|ooda|hogi|banni|haage|gaade|ivattu|naale|kannada|avaru|ivaru|'
    r'ellara|ella|beda|aytu|agalla|bantu|koti|huli|nodu|helu)\b',
    re.IGNORECASE
)

# Greetings
GREETINGS_PATTERNS = re.compile(
    r'^\s*(hello|hi|hey|namaskara|namaskaram|namaste|good\s+morning|good\s+evening|good\s+afternoon|vanakkam|hai)\s*[.!?]*\s*$',
    re.IGNORECASE
)

# Profanity / Abusive terms (basic filter)
PROFANITY_PATTERNS = re.compile(
    r'\b(bastard|bitch|asshole|idiot|stupid|fuck|shit|bloody|bolimakkle|sulemakkle)\b',
    re.IGNORECASE
)

# Theme keyword dictionaries for lightweight query classification
THEME_KEYWORDS = {
    'Agriculture': ['crop', 'farm', 'soil', 'harvest', 'plow', 'field', 'seed', 'paddy', 'grain', 'orchard', 'farmer', 'vanilla', 'orchid', 'pollinating', 'bakeries', 'organic', 'ಕೃಷಿ', 'ಬೆಳೆ', 'ಭೂಮಿ', 'ಹೊಲ', 'ರೈತ', 'ಉಳುಮೆ', 'ಕೃಷಿಕ'],
    'Money': ['money', 'earn', 'spend', 'loan', 'debt', 'salary', 'rupee', 'rich', 'poor', 'cost', 'expensive', 'bank', 'cash', 'credit', 'budget', 'afford', 'cope', 'bill', 'bills', 'rent', 'groceries', 'luxury', 'saving', 'borrow', 'emi', 'financial', 'poverty', 'income', 'outings', 'smartphone', 'ವೇತನ', 'ಖರ್ಚು', 'ದುಡ್ಡು', 'ಹಣ', 'ಸಾಲ', 'ಕಾಸು'],
    'Health': ['health', 'sick', 'hospital', 'doctor', 'fever', 'medicine', 'diet', 'food', 'eat', 'exercise', 'disease', 'hygiene', 'clean', 'reagent', 'chemical', 'ಆರೋಗ್ಯ', 'ಊಟ', 'ರೋಗ', 'ಸ್ವಚ್ಛತೆ'],
    'Work': ['work', 'effort', 'hard', 'sweat', 'lazy', 'tired', 'task', 'job', 'skill', 'practice', 'diligent', 'sample', 'research', 'experiment', 'ಕೆಲಸ', 'ಶ್ರಮ', 'ದುಡಿಮೆ'],
    'Time': ['time', 'punctual', 'late', 'hurry', 'delay', 'wait', 'clock', 'today', 'tomorrow', 'haste', 'rush', 'hurrying', 'rapidly', 'last-minute', 'deadline', 'ಸಮಯ', 'ಕಾಲ', 'ಆತುರ', 'ಅವಸರ', 'ಧಾವಂತ'],
    'Family': ['family', 'mother', 'father', 'son', 'daughter', 'household', 'home', 'relative', 'parent', 'influencer', 'social media', 'glamour', 'vacation', 'ಮನೆ', 'ತಾಯಿ', 'ಕುಟುಂಬ', 'ಅತ್ತೆ', 'ಸೊಸೆ'],
    'Friends': ['friend', 'trust', 'help', 'companion', 'neighbor', 'mutual', 'cooperation', 'ಸ್ನೇಹ', 'ಗೆಳೆಯ', 'ನೆಂಟ', 'ನೆರೆಹೊರೆ'],
    'Character': ['pride', 'arrogant', 'honest', 'truth', 'lie', 'deceit', 'humble', 'respect', 'greed', 'foolish', 'flawless', 'envious', 'ಸತ್ಯ', 'ಸುಳ್ಳು', 'ಅಹಂಕಾರ', 'ವಿನಯ'],
    'Nature': ['nature', 'tree', 'rain', 'water', 'lake', 'flood', 'forest', 'animal', 'stream', 'drain', 'drains', 'stormwater', 'monsoon', 'basement', 'pumps', 'suction', 'ಮಳೆ', 'ನೀರು', 'ಮರ', 'ಕಾಡು', 'ಕೆರೆ', 'ಪ್ರಕೃತಿ', 'ಪ್ರವಾಹ', 'ಕಾಲುವೆ'],
    'Education': ['school', 'study', 'teacher', 'book', 'exam', 'student', 'learn', 'knowledge', 'wisdom', 'ವಿದ್ಯೆ', 'ಶಾಲೆ', 'ಪುಸ್ತಕ', 'ಗುರು'],
    'Leadership': ['leader', 'rule', 'king', 'order', 'govern', 'guide', 'captain', 'authority', 'responsibility', 'municipal', 'authorities', 'council', 'ನ್ಯಾಯ', 'ನಾಯಕ', 'ಆಡಳಿತ', 'ಅಧಿಕಾರ'],
    'Business': ['business', 'shop', 'customer', 'trade', 'merchant', 'profit', 'loss', 'accounting', 'ledger', 'contract', 'contracts', 'ವ್ಯಾಪಾರ', 'ಗ್ರಾಹಕ', 'ಲಾಭ', 'ನಷ್ಟ'],
    'Society': ['society', 'village', 'public', 'people', 'community', 'cooperation', 'neighbors', 'ಸಮಾಜ', 'ಊರು', 'ಜನ']
}


class MatcherService:
    """
    Multimodal Semantic Matcher for Kannada Proverbs.
    Primary matcher uses deep LLM understanding (Gemini | Groq) to comprehend the
    underlying moral dilemma, with automatic fallback to offline TF-IDF + BM25.
    """
    _instance = None
    _loaded = False

    def __init__(self):
        self.backend_name = "tfidf"
        self.provider = None
        self.index_meta = None
        self.gaade_vectors = None
        self.situation_vectors = None
        self.bm25 = None
        self.gaade_ids = []
        self.situations = []
        self._load_index()

    @classmethod
    def get_instance(cls) -> "MatcherService":
        if cls._instance is None:
            cls._instance = MatcherService()
        return cls._instance

    def _load_index(self):
        index_root = os.path.join(settings.DATA_DIR, "index")
        configured_backend = os.environ.get("EMBEDDING_BACKEND", "tfidf").lower().strip()
        
        backend_dir = os.path.join(index_root, configured_backend)
        active_backend = configured_backend

        if not os.path.isdir(backend_dir) or not os.path.isfile(os.path.join(backend_dir, "index_meta.json")):
            logger.warning(f"Index for '{configured_backend}' not found at {backend_dir}. Falling back to 'tfidf'.")
            active_backend = "tfidf"
            backend_dir = os.path.join(index_root, "tfidf")
            
        if not os.path.isdir(backend_dir) or not os.path.isfile(os.path.join(backend_dir, "index_meta.json")):
            logger.error(f"Missing index directory: {backend_dir}. Run scripts/build_index.py first.")
            return

        try:
            meta_path = os.path.join(backend_dir, "index_meta.json")
            with open(meta_path, "r", encoding="utf-8") as f:
                self.index_meta = json.load(f)
            self.gaade_ids = self.index_meta["gaade_ids"]
            self.situations = self.index_meta["situations"]
            
            gaade_vec_npz = os.path.join(backend_dir, "gaade_vectors.npz")
            if os.path.isfile(gaade_vec_npz):
                with np.load(gaade_vec_npz) as d:
                    self.gaade_vectors = d["vectors"]
            else:
                self.gaade_vectors = np.load(os.path.join(backend_dir, "gaade_vectors.npy"))

            situation_vec_npz = os.path.join(backend_dir, "situation_vectors.npz")
            if os.path.isfile(situation_vec_npz):
                with np.load(situation_vec_npz) as d:
                    self.situation_vectors = d["vectors"]
            else:
                self.situation_vectors = np.load(os.path.join(backend_dir, "situation_vectors.npy"))
            
            bm25_path = os.path.join(backend_dir, "bm25.joblib")
            if os.path.isfile(bm25_path):
                self.bm25 = joblib.load(bm25_path)
                
            self.provider, self.backend_name = get_embedding_provider(active_backend, index_dir=index_root)
            self._loaded = True
            logger.info(f"MatcherService loaded offline index: '{self.backend_name}' ({len(self.gaade_ids)} gaades)")
        except Exception as e:
            logger.error(f"Failed to load MatcherService index: {e}")
            self._loaded = False

    @staticmethod
    def normalize_query(text: str) -> str:
        """Apply Unicode NFC normalization for matching only."""
        if not text:
            return ""
        return unicodedata.normalize("NFC", text).strip()

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect whether input is Kannada script, English, or Kanglish."""
        has_kannada = bool(re.search(r'[\u0C80-\u0CFF]', text))
        has_latin = bool(re.search(r'[a-zA-Z]', text))

        if has_kannada and has_latin:
            return "mixed"
        if has_kannada:
            return "kn"
        if has_latin:
            if KANGLISH_PATTERNS.search(text):
                return "kanglish"
            return "en"
        return "unknown"

    @staticmethod
    def detect_theme(text: str) -> Optional[str]:
        """Detect dominant thematic category from query."""
        text_lower = text.lower()
        counts = {}
        for theme, kws in THEME_KEYWORDS.items():
            cnt = sum(1 for kw in kws if re.search(r'\b' + re.escape(kw), text_lower))
            if cnt > 0:
                counts[theme] = cnt
        if not counts:
            return None
        return max(counts.items(), key=lambda x: x[1])[0]

    def generate_explanation(self, gaade_item: Dict[str, Any], query: str, closest_situation: str) -> str:
        """Synthesize grounded, human-friendly explanation connecting user scenario to proverb."""
        meaning = gaade_item.get("meaning", "").strip()
        english = gaade_item.get("english", "").strip()
        theme = gaade_item.get("theme", "").strip()

        explanation = (
            f"This proverb highlights that {english.rstrip('.')}. "
            f"In your described situation, the dilemma reflects this exact principle of {theme.lower()}. "
            f"Just as in the real-world example: '{closest_situation}', "
            f"this Kannada gaade offers timeless wisdom on how to approach the situation."
        )
        return explanation

    @classmethod
    def match(
        cls,
        text: str,
        lang: str = "auto",
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        instance = cls.get_instance()
        return instance._execute_match(text, lang, client_ip=client_ip)

    def _execute_match(
        self,
        raw_text: str,
        lang_hint: str = "auto",
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Normalization
        text = self.normalize_query(raw_text)
        
        # 2. Edge Case: Empty or too short
        if len(text) < 4 or not re.search(r'\w', text):
            return {
                "status": "invalid_input",
                "matcher_backend": self.backend_name,
                "detected_lang": "unknown",
                "message": "Please describe a life situation or dilemma with at least a few words.",
                "best": None,
                "alternatives": []
            }

        # 3. Edge Case: Greetings (Always return no_good_match per specification)
        if GREETINGS_PATTERNS.match(text):
            return {
                "status": "no_good_match",
                "matcher_backend": self.backend_name,
                "detected_lang": self.detect_language(text),
                "message": "Namaskara! Please describe an experience, event, or problem you are facing, and I will find the right Kannada proverb for it.",
                "best": None,
                "alternatives": []
            }

        # 4. Edge Case: Profanity
        if PROFANITY_PATTERNS.search(text):
            return {
                "status": "inappropriate_input",
                "matcher_backend": self.backend_name,
                "detected_lang": self.detect_language(text),
                "message": "Please use polite and courteous language to describe your situation.",
                "best": None,
                "alternatives": []
            }

        detected_lang = self.detect_language(text) if lang_hint == "auto" else lang_hint

        # 5. PRIMARY STEP: LLM-Based Semantic Understanding Matcher
        llm_matcher = get_llm_matcher()
        llm_attempted = False

        if llm_matcher.is_configured():
            llm_attempted = True
            try:
                llm_result = llm_matcher.match(
                    text=text,
                    lang=detected_lang,
                    client_ip=client_ip
                )
                if llm_result is not None:
                    return llm_result
                logger.info("LLM matcher call returned None. Activating offline TF-IDF fallback.")
            except Exception as e:
                logger.error(f"Error during LLM matcher execution: {e}. Falling back to TF-IDF.")

        # 6. SECONDARY STEP: Offline Hybrid TF-IDF / BM25 Fallback Matcher
        return self._execute_tfidf_match(text, detected_lang, is_fallback=llm_attempted)

    def get_top_candidate_prompt_text(self, text: str, top_k: int = 35) -> str:
        """
        Produce a compact catalog snippet of top-K candidate proverbs for the LLM prompt.
        Reduces prompt token count from ~16,000 down to ~850 tokens, staying well within
        Groq's 6,000 TPM limit and achieving ~350ms latency.
        """
        if not self._loaded or self.gaade_vectors is None or not self.gaade_ids:
            return ""

        try:
            truncated = text[:1000]
            q_vec = self.provider.embed_texts([truncated])
            sim_gaades = (self.gaade_vectors @ q_vec.T).flatten()
            sim_situations = (self.situation_vectors @ q_vec.T).flatten()

            max_sit_sim = np.zeros(len(self.gaade_ids), dtype=np.float32)
            for idx, s_info in enumerate(self.situations):
                gid = s_info['gaade_id']
                if gid in self.gaade_ids:
                    g_idx = self.gaade_ids.index(gid)
                    if sim_situations[idx] > max_sit_sim[g_idx]:
                        max_sit_sim[g_idx] = sim_situations[idx]

            scores = (0.35 * sim_gaades) + (0.45 * max_sit_sim)
            ranked_indices = np.argsort(-scores)[:top_k]
            top_ids = [self.gaade_ids[i] for i in ranked_indices]

            llm_matcher = get_llm_matcher()
            lines = []
            for gid in top_ids:
                item = llm_matcher.registry.canonical_gaades.get(gid)
                if item:
                    lines.append(
                        f"{gid}: {item['gaade']} | Meaning: {item['meaning']} | English: {item['english']} | Theme: {item['theme']}"
                    )
            return "\n".join(lines)
        except Exception as e:
            logger.warning(f"Could not generate candidate snippet: {e}")
            return ""

    def _execute_tfidf_match(
        self,
        text: str,
        detected_lang: str,
        is_fallback: bool = False
    ) -> Dict[str, Any]:
        active_backend_label = "tfidf-fallback" if is_fallback else self.backend_name

        if not self._loaded or self.gaade_vectors is None:
            logger.error("Matcher index not loaded.")
            return {
                "status": "error",
                "matcher_backend": active_backend_label,
                "detected_lang": detected_lang,
                "message": "Semantic matcher index is not built. Please run scripts/build_index.py.",
                "best": None,
                "alternatives": []
            }

        truncated_query = text[:1000]

        # Dense / TF-IDF Retrieval
        try:
            q_vec = self.provider.embed_texts([truncated_query])
            sim_gaades = (self.gaade_vectors @ q_vec.T).flatten()
            sim_situations = (self.situation_vectors @ q_vec.T).flatten()
        except Exception as e:
            logger.error(f"Error computing query vector: {e}")
            sim_gaades = np.zeros(len(self.gaade_ids), dtype=np.float32)
            sim_situations = np.zeros(len(self.situations), dtype=np.float32)

        # Max-situation similarity per gaade
        max_sit_sim = np.zeros(len(self.gaade_ids), dtype=np.float32)
        closest_sit_idx_per_gaade = {}
        for idx, s_info in enumerate(self.situations):
            gid = s_info['gaade_id']
            if gid in self.gaade_ids:
                g_idx = self.gaade_ids.index(gid)
                if sim_situations[idx] > max_sit_sim[g_idx]:
                    max_sit_sim[g_idx] = sim_situations[idx]
                    closest_sit_idx_per_gaade[g_idx] = idx

        # BM25 Lexical Retrieval
        if self.bm25:
            tokens = tokenize_for_bm25(truncated_query)
            bm_scores = np.array(self.bm25.get_scores(tokens), dtype=np.float32)
            bm_max = np.max(bm_scores)
            bm_norm = (bm_scores / (bm_max + 1e-6)) if bm_max > 0 else bm_scores
        else:
            bm_norm = np.zeros(len(self.gaade_ids), dtype=np.float32)

        # Theme Signal Boost
        detected_theme = self.detect_theme(truncated_query)

        # Hybrid Fusion: situational match weight emphasized for real-world scenarios
        w_dense = float(os.environ.get("WEIGHT_DENSE", "0.35"))
        w_max_sit = float(os.environ.get("WEIGHT_MAX_SIT", "0.45"))
        w_bm25 = float(os.environ.get("WEIGHT_BM25", "0.20"))

        final_scores = (w_dense * sim_gaades) + (w_max_sit * max_sit_sim) + (w_bm25 * bm_norm)

        # Apply theme boost if detected
        if detected_theme:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT gaade_id, theme FROM gaades;")
            for r in cur.fetchall():
                if r['theme'] and r['theme'].lower() == detected_theme.lower():
                    if r['gaade_id'] in self.gaade_ids:
                        idx = self.gaade_ids.index(r['gaade_id'])
                        final_scores[idx] += 0.12
            conn.close()

        # Rank candidates
        ranked_indices = np.argsort(-final_scores)
        top_k = 3
        top_indices = ranked_indices[:top_k]

        top_score = float(final_scores[top_indices[0]])
        second_score = float(final_scores[top_indices[1]]) if len(top_indices) > 1 else 0.0

        # Fetch Proverb Details from DB
        conn = get_db_connection()
        top_candidates = []
        for i in top_indices:
            gid = self.gaade_ids[i]
            score_val = float(final_scores[i])
            g_item = get_gaade_by_id(conn, gid)
            if g_item:
                g_item['confidence'] = round(min(score_val, 1.0), 4)
                sit_idx = closest_sit_idx_per_gaade.get(i)
                closest_text = ""
                if sit_idx is not None and sit_idx < len(self.situations):
                    closest_text = self.situations[sit_idx].get('situation_id', '')
                g_item['closest_situation_id'] = closest_text
                # Default explanation fields for fallback
                g_item['reason_en'] = self.generate_explanation(g_item, truncated_query, g_item.get("english", ""))
                g_item['reason_kn'] = f"ಈ ಗಾದೆಯು ನೀವು ವಿವರಿಸಿದ ಸಂದರ್ಭಕ್ಕೆ ಸರಿಯಾದ ನೀತಿ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತದೆ."
                top_candidates.append(g_item)
        conn.close()

        # Confidence and Ambiguity Rules
        min_threshold = float(os.environ.get("MATCHER_MIN_THRESHOLD", "0.14"))
        ambiguity_margin = float(os.environ.get("MATCHER_AMBIGUITY_MARGIN", "0.015"))

        if top_score < min_threshold:
            return {
                "status": "no_good_match",
                "matcher_backend": active_backend_label,
                "detected_lang": detected_lang,
                "message": "No Kannada proverb in the collection closely matched this situation. Try adding more specific details or actions.",
                "best": None,
                "alternatives": []
            }

        is_ambiguous = (
            len(top_candidates) > 1
            and (top_score - second_score) < ambiguity_margin
            and top_score < 0.45
        )

        best_item = top_candidates[0]
        explanation = self.generate_explanation(
            best_item,
            truncated_query,
            best_item.get("english", "")
        )
        best_item["explanation"] = explanation

        alternatives = top_candidates[1:]

        status_label = "ambiguous" if is_ambiguous else "ok"
        message_label = (
            "Multiple proverbs could fit this situation closely. Here are the top alternatives."
            if is_ambiguous else
            "Successfully matched the best Kannada proverb for your situation."
        )

        return {
            "status": status_label,
            "matcher_backend": active_backend_label,
            "detected_lang": detected_lang,
            "message": message_label,
            "best": best_item,
            "alternatives": alternatives
        }


__all__ = [
    "MatcherService",
    "LLMMatcher",
    "get_llm_matcher",
    "LLMCandidateRegistry",
    "SYSTEM_INSTRUCTION"
]

