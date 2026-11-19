# Gaade Kosha - Baseline System & Verification Report
**Modalapada 2.0 (Problem 2: Proverbs for Every Situation)**  
**Generated At**: 2026-11-20 00:31:36

---

## 1. Executive Baseline Metrics

| Metric | Measured Value | Standard / Requirement | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Canonical Proverbs (Gaades)** | `226` | 200+ canonical | **PASS** |
| **Contextual Situations** | `452` | Exactly 2 per gaade (400+) | **PASS** |
| **Provenance Records** | `252` | 226 canonical + 26 duplicates | **PASS** |
| **Canonical WAV Audio Files** | `224` | 16 kHz / Mono / PCM-16 | **PASS** |
| **Source OGG Audio Archives** | `250` | Read-only archival source (250) | **PASS** |
| **Audio Format Errors** | `0` | 0 errors, 0 duplicate hashes | **PASS** |
| **Verified Consent Records** | `9` | Verifiable signatures on disk | **PASS** |
| **Regional Provenance Audit** | `100.0% UNVERIFIED` | Zero fabricated elders/places | **PASS (Anti-Fabrication)** |

---

## 2. Validator Suite Execution Results

| Validator Script | Scope | Result | Details |
| :--- | :--- | :---: | :--- |
| `scripts/validate_gaades.py` | Gaades CSV schema, non-empty text, Kannada Unicode, themes | **PASS** | All 226 gaades valid |
| `scripts/validate_situations.py` | Situations CSV schema, foreign key IDs, 2-per-gaade | **PASS** | 452/452 strictly mapped |
| `scripts/validate_consent.py` | Consent register integrity & signature file verification | **PASS** | 9 records verified against on-disk JPEGs |
| Audio Spec Validator | Channels (1), Rate (16000 Hz), Bit depth (16), Hash uniqueness | **PASS** | 224/224 bit-perfect |

---

## 3. Dataset Distribution Breakdown

### A. Thematic Categories (15 Approved Themes)
- **Character**: 72 (31.9%)
- **Society**: 26 (11.5%)
- **Money**: 20 (8.8%)
- **Work**: 18 (8.0%)
- **Time**: 18 (8.0%)
- **Family**: 16 (7.1%)
- **Friends**: 10 (4.4%)
- **Study**: 9 (4.0%)
- **Health**: 6 (2.7%)
- **Leadership**: 6 (2.7%)
- **Education**: 5 (2.2%)
- **Agriculture**: 5 (2.2%)
- **Nature**: 5 (2.2%)
- **Business**: 5 (2.2%)
- **Culture**: 5 (2.2%)

### B. Geographic Regions (Anti-Fabrication Policy)
- **UNVERIFIED**: 226 / 226 (100.0%)
- *Note: In accordance with academic ethics, all regions remain marked 'UNVERIFIED' pending returned physical elder review forms. Zero region names have been fabricated.*

---

## 4. Repository Structure (Truncated Tree)
```
gaade-kosha/
  .dockerignore
  .env.example
  .gitignore
  Dockerfile
  Makefile
  package.json
  README.md
  requirements.txt
audio/
  original_ogg/
    1.ogg
    10.ogg
    100.ogg
    101.ogg
    102.ogg
    103.ogg
    104.ogg
    105.ogg
    ... (243 more files)
  wav/
    G001.wav
    G002.wav
    G003.wav
    G004.wav
    G005.wav
    G006.wav
    G007.wav
    G008.wav
    ... (216 more files)
  wav_unused_duplicates/
    G086.wav
    G117.wav
    G125.wav
    G131.wav
    G135.wav
    G163.wav
    G164.wav
    G168.wav
    ... (18 more files)
backend/
  app/
    asr.py
    config.py
    db.py
    embeddings.py
    main.py
    matcher.py
    models.py
    __init__.py
  tests/
    test_api.py
    test_asr.py
    test_datasets.py
    test_health.py
    test_loader.py
    __init__.py
data/
  gaades.csv
  gaades.csv.bak
  gaade_kosha.db
  gaade_provenance.csv
  raw_gaades_dump.json
  situations.csv
  backups/
    gaades_before_examples.csv
    gaade_provenance_before_examples.csv
  elder_review/
    elder_review_sheet.csv
    elder_review_sheet.html
```
