# -*- coding: utf-8 -*-
"""
Gaade Kosha Matcher Facade.
Provides backward compatibility for scripts referencing backend/app/matcher.py.
Delegates to the modern modular backend.app.matcher package.
"""

from backend.app.matcher import (
    MatcherService,
    LLMMatcher,
    get_llm_matcher,
    LLMCandidateRegistry,
    SYSTEM_INSTRUCTION
)

__all__ = [
    "MatcherService",
    "LLMMatcher",
    "get_llm_matcher",
    "LLMCandidateRegistry",
    "SYSTEM_INSTRUCTION"
]
