# Gaade Kosha Proverbs Dataset – Formal Validation Report
**Modalapada 2.0 – Kannada Multimodal AI Hackathon (Problem 2)**

**Validation Status**: ✅ PASSED (All Checks Clean)
**Total Proverbs Audited in Provenance**: 252 (G001 – G252)
**Total Canonical (Non-Duplicate) Proverbs**: 226
**Total Excluded Duplicates**: 26
**Total Identified Duplicate Pairs**: 26

---

## 1. Compliance Matrix

| Audit Item | Expected Standard | Observed State | Status |
| :--- | :--- | :--- | :--- |
| **File Existence & UTF-8** | Strict UTF-8 without BOM | 5/5 CSV files clean UTF-8 | ✅ PASS |
| **Unicode Replacement (U+FFFD)** | Zero occurrences | 0 instances across all files | ✅ PASS |
| **Unique Primary Keys** | Format `G[0-9]{3}`, strictly unique | 226 canonical unique IDs | ✅ PASS |
| **Non-Empty Core Fields** | `gaade`, `meaning`, `theme`, `audio_file` present | 0 empty required cells | ✅ PASS |
| **Example Column Rule** | Team-drafted conversational usage example populated | 100% populated in canonical gaades.csv | ✅ PASS |
| **Example Source Rule** | Strictly 'team_drafted' in provenance | 100% team-drafted (no elder claim) | ✅ PASS |
| **Region Column Rule** | Strictly literal `'UNVERIFIED'` | 100% `'UNVERIFIED'` | ✅ PASS |
| **Elder Verification Rule** | No fabricated elder verifications | 100% `'unverified'` | ✅ PASS |
| **Consent Reference Rule** | Strictly empty (no invented consent) | 100% empty | ✅ PASS |
| **Theme Constraint** | Official 16 allowed categories | 100% compliant | ✅ PASS |
| **Duplicate Segregation** | No duplicates in `gaades.csv` | 26 duplicates isolated in reports | ✅ PASS |

---

## 2. Statistical Breakdown

### 2.1 Canonical Proverbs by Official Theme

| Theme | Count | Percentage of Canonical |
| :--- | :--- | :--- |
| **Agriculture** | 5 | 2.2% |
| **Business** | 5 | 2.2% |
| **Character** | 72 | 31.9% |
| **Culture** | 5 | 2.2% |
| **Education** | 5 | 2.2% |
| **Family** | 16 | 7.1% |
| **Friends** | 10 | 4.4% |
| **Health** | 6 | 2.7% |
| **Leadership** | 6 | 2.7% |
| **Money** | 20 | 8.8% |
| **Nature** | 5 | 2.2% |
| **Other** | 0 | 0.0% |
| **Society** | 26 | 11.5% |
| **Study** | 9 | 4.0% |
| **Time** | 18 | 8.0% |
| **Work** | 18 | 8.0% |

### 2.2 Provenance Source Breakdown

| Source Type | Count | Description |
| :--- | :--- | :--- |
| `existing_collection_pdf` | 200 | Base collection (G001–G200) |
| `newly_drafted` | 52 | Additions G201–G250 & Slide Examples G251–G252 |
| `team_collected_from_elder` | 0 | Reserved for future field collections |

### 2.3 Verification Status Breakdown

| Verification Status | Count | Note |
| :--- | :--- | :--- |
| `unverified` | 252 | Pending formal team and elder proofreading |
| `proofread_by_team` | 0 | To be updated via `proofread_sheet.csv` |
| `elder_verified` | 0 | Requires signed consent form |

---

## 3. Duplicate Analysis Summary

A total of **26 duplicate entries** were confirmed and systematically resolved:
- **25 Exact Duplicates**: Re-occurrences in the original collection (e.g., G029/G131, G042/G086, G083/G117, G150/G200, G013/G190).
- **1 Near-Exact Variant**: G104 (*'ಕತ್ತೆಗೆ ಕಸ್ತೂರಿ ವಾಸನೆ ಗೊತ್ತೇ?'*) vs G135 (*'ಕತ್ತೆಗೆ ಏನು ಗೊತ್ತು ಕಸ್ತೂರಿ ಪರಿಮಳ?'*) mapped as a variant duplicate.

All 26 later entries are excluded from `data/gaades.csv` to ensure high retrieval precision, archived in `data/reports/excluded_duplicates.csv`, and cross-referenced in `data/reports/duplicates.csv`.

---

## 4. Human Proofreading Mandate

> [!IMPORTANT]
> As recorded in `data/reports/proofread_sheet.csv`, the dataset remains in **`unverified`** status until a native Kannada speaker completes the visual verification against the rasterised 300 DPI page images in `data/raw/pdf_pages/`.
