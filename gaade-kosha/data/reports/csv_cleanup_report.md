# CSV Standardization & Spacing Cleanup Report

**Project**: Gaade Kosha (ಗಾದೆ ಕೋಶ) – Modalapada 2.0 (Problem 2)  
**Department**: Department of CSE&E, Ramaiah Institute of Technology  
**Generated Date**: 2026-11-20  
**Scope**: All submission CSV files (`gaades.csv`, `situations.csv`, `consent/consent_register.csv`, and `docs/utf8_no_bom/*.csv`)  

---

## 1. Executive Summary & Schema Upgrade

In accordance with Hackathon specifications, all submission CSVs were audited and standardized for clean rendering across Microsoft Excel, Google Sheets, and standard Unix tooling:
1. **Schema Upgrade (`situations.csv`)**:
   - A new column `gaade` was inserted into `situations.csv` by joining on `gaade_id` against `data/gaades.csv`.
   - **New Column Sequence**: `situation_id`, `gaade_id`, `gaade`, `situation_text`, `situation_kn`, `language`, `situation_source`.
   - **Data Fidelity**: 100% of situations (452 rows) matched canonical gaades. The Kannada proverb strings were copied verbatim, byte-for-byte, without any normalisation or rewriting.
2. **Spacing & Cleanliness**:
   - Leading and trailing whitespace stripped across all cells.
   - Zero internal double spaces or unescaped tabs in Kannada text.
   - Punctuation spacing in free-text fields standardized.
   - Minimal standard quoting (`csv.QUOTE_MINIMAL`) with embedded quotes doubled.
3. **Encoding & Line Endings**:
   - Primary submission CSVs encoded in **UTF-8 with BOM (`utf-8-sig`)** and **CRLF (`\r\n`)** line endings so Excel on Windows opens Kannada text cleanly without encoding prompts.
   - Plain UTF-8 copies (**no BOM**, **LF `\n`**) maintained in `submission/docs/utf8_no_bom/` for POSIX/headless data loaders.
4. **Convenience Excel Workbooks**:
   - Full Excel workbooks generated at `submission/extras/gaades.xlsx` and `submission/extras/situations.xlsx` featuring frozen headers, bold titles, column width auto-fitting, and Noto Sans Kannada font.

---

## 2. Rule-by-Rule Audit Breakdown

| Rule | Description | `gaades.csv` | `situations.csv` | `consent_register.csv` |
| :---: | :--- | :---: | :---: | :---: |
| **Rule A** | Strip leading/trailing whitespace (`spaces`, `\t`, `\r`, `\n`, `\u00A0`, `\u200B`) | 0 cells | 0 cells | 0 cells |
| **Rule B** | Free-text normalization (collapse runs of spaces, fix spacing around `, . ; : ? !`, remove inner linebreaks) | 0 cells | 0 cells | 0 cells |
| **Rule C** | Kannada `gaade` column integrity (only trim ends, log internal odd spaces, preserve ZWJ/ZWNJ) | 0 anomalies | 0 anomalies | N/A |
| **Rule D** | Remove blank rows & trailing empty rows | 0 removed | 0 removed | 0 removed |
| **Rule E** | Standard minimal quoting (`QUOTE_MINIMAL`, RFC 4180 quote escaping) | 226 rows formatted | 452 rows formatted | 9 rows formatted |
| **Rule F** | Encoding & line endings (BOM + CRLF in root, no BOM + LF in docs) | 226 rows formatted | 452 rows formatted | 9 rows formatted |
| **Rule G** | Consistent sorting (`gaades` by `gaade_id`, `situations` by `gaade_id` then `situation_id`) | Verified (sorted) | Verified (sorted) | Verified (sorted) |
| **Rule H** | Join `gaade` into `situations.csv` | N/A | 452 cells populated | N/A |

*Note: All original datasets were pre-validated and clean; standardization strictly maintained character fidelity while formatting delimiters, line endings, quoting, and joining the `gaade` text.*

---

## 3. Cryptographic Gaade Column Verification

To prove that zero Kannada characters, conjuncts, or letters were modified:
- **Source `data/gaades.csv` Gaade Column SHA-256**: `12fbec2e9d077c5eb977791d7b9baafda9ffb221d8ad06f7fdd67faa8ec93b4b`
- **Submission `submission/gaades.csv` Gaade Column SHA-256**: `12fbec2e9d077c5eb977791d7b9baafda9ffb221d8ad06f7fdd67faa8ec93b4b`
- **Joined `submission/situations.csv` Gaade Column Match**: 452 / 452 rows (100.0%) identical to source.
- **Unicode Replacement Characters (`U+FFFD`)**: **0** detected across all CSV files.

---

## 4. 10 Representative Before / After Samples

### Sample 1: `situations.csv` — `S001_1` (Gaade text column added)
- **Before Columns**: `situation_id`, `gaade_id`, `situation_text`, `situation_kn`, `language`, `situation_source`
- **Before Data**: `S001_1,G001,"Ramesh had a profitable spice stall...", "ರಮೇಶ್ ಉತ್ತಮ ಲಾಭದಾಯಕ...",en,team_drafted`
- **After Columns**: `situation_id`, `gaade_id`, `gaade`, `situation_text`, `situation_kn`, `language`, `situation_source`
- **After Data**: `S001_1,G001,"ಅಕ್ಕಿ ಮೇಲೆ ಆಸೆ, ನೆಂಟರ ಮೇಲೆ ಪ್ರೀತಿ.","Ramesh had a profitable spice stall...","ರಮೇಶ್ ಉತ್ತಮ ಲಾಭದಾಯಕ...",en,team_drafted`

### Sample 2: `situations.csv` — `S001_2` (Gaade text column added)
- **Before**: `S001_2,G001,"A mango orchard owner stripped every unripened fruit...","ಮಾವಿನ ತೋಟದ ಮಾಲೀಕನು...",en,team_drafted`
- **After**: `S001_2,G001,"ಅಕ್ಕಿ ಮೇಲೆ ಆಸೆ, ನೆಂಟರ ಮೇಲೆ ಪ್ರೀತಿ.","A mango orchard owner stripped every unripened fruit...","ಮಾವಿನ ತೋಟದ ಮಾಲೀಕನು...",en,team_drafted`

### Sample 3: `situations.csv` — `S007_1` (Gaade text column added)
- **Before**: `S007_1,G007,"A subcontractor collected full advance...","ಉಪಗುತ್ತಿಗೆದಾರನು ಕೆಲಸ ಪೂರ್ಣಗೊಳಿಸುವುದಾಗಿ...",en,team_drafted`
- **After**: `S007_1,G007,"ಅಟ್ಟದ ಮೇಲಿನ ಮೂಟೆ ಇಳಿಸೋಕೆ ಹೋದರೆ, ಕಂಕುಳಲ್ಲಿರೋ ಗಂಟು ಕಳಚಿಬಿತ್ತು.","A subcontractor collected full advance...","ಉಪಗುತ್ತಿಗೆದಾರನು ಕೆಲಸ ಪೂರ್ಣಗೊಳಿಸುವುದಾಗಿ...",en,team_drafted`

### Sample 4: `situations.csv` — `S039_1` (Gaade text column added)
- **Before**: `S039_1,G039,"A farmer worked relentlessly through drought...","ರೈತನೊಬ್ಬ ಬರಗಾಲದಲ್ಲೂ ಶ್ರಮವಹಿಸಿ...",en,team_drafted`
- **After**: `S039_1,G039,"ಕಷ್ಟಪಟ್ಟರೆ ಫಲ ಸಿಗುತ್ತದೆ.","A farmer worked relentlessly through drought...","ರೈತನೊಬ್ಬ ಬರಗಾಲದಲ್ಲೂ ಶ್ರಮವಹಿಸಿ...",en,team_drafted`

### Sample 5: `situations.csv` — `S125_1` (Gaade text column added)
- **Before**: `S125_1,G125,"An inexperienced coder tried refactoring core payments...","ಅನುಭವವಿಲ್ಲದ ಡೆವಲಪರ್ ಒಬ್ಬರು...",en,team_drafted`
- **After**: `S125_1,G125,"ತುಂಬಿದ ಕೊಡ ತುಳುಕುವುದಿಲ್ಲ.","An inexperienced coder tried refactoring core payments...","ಅನುಭವವಿಲ್ಲದ ಡೆವಲಪರ್ ಒಬ್ಬರು...",en,team_drafted`

### Sample 6: `situations.csv` — `S226_2` (Gaade text column added)
- **Before**: `S226_2,G226,"An ambitious entrepreneur launched a luxury boutique...","ಮಾರುಕಟ್ಟೆಯ ಆರ್ಥಿಕ ಸ್ಥಿತಿಯನ್ನು ಅರಿಯದೆ...",en,team_drafted`
- **After**: `S226_2,G226,"ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು.","An ambitious entrepreneur launched a luxury boutique...","ಮಾರುಕಟ್ಟೆಯ ಆರ್ಥಿಕ ಸ್ಥಿತಿಯನ್ನು ಅರಿಯದೆ...",en,team_drafted`

### Sample 7: `gaades.csv` — `G001` (BOM and CRLF standardized)
- **Before Encoding**: UTF-8 without BOM, LF (`\n`)
- **After Encoding**: UTF-8 with BOM (`\xef\xbb\xbf`), CRLF (`\r\n`), minimal quote formatting.

### Sample 8: `gaades.csv` — `G039` (BOM and CRLF standardized)
- **Before Data**: `G039,ಕಷ್ಟಪಟ್ಟರೆ ಫಲ ಸಿಗುತ್ತದೆ.,ಕಷ್ಟಪಟ್ಟು ಕೆಲಸ ಮಾಡಿದರೆ ಉತ್ತಮ ಫಲ ದೊರೆಯುತ್ತದೆ.,Hard work can bring results.,ರೈತರು ಕಷ್ಟಪಟ್ಟು ದುಡಿದಾಗ ಉತ್ತಮ ಬೆಳೆ ಬರುತ್ತದೆ.,UNVERIFIED,Work,audio/wav/G039.wav`
- **After Data**: Identical content, UTF-8 with BOM, CRLF line termination.

### Sample 9: `consent_register.csv` — `G01` (Grandmother Shantha B M)
- **Before Data**: `G01,Shantha B M,elder,Grandmother,Hassan,docs/consent/signatures/Shantha_Signature.jpeg,125,1-125,no,19/11/2026,yes,In-person signed paper form,Pranav H M`
- **After Data**: Standardized quotes, UTF-8 with BOM, CRLF line termination.

### Sample 10: `consent_register.csv` — `A01` (Voice Contributor H M Pranav)
- **Before Data**: `A01,H M Pranav,voice_contributor,Grandson,Bengaluru,docs/consent/signatures/Pranav_Signature.jpeg,50,1-50,yes,19/11/2026,yes,In-person signed paper form,Akshay A`
- **After Data**: Standardized quotes, UTF-8 with BOM, CRLF line termination.

---

## 5. Artifact Verification

- **Submission Package Location**: `gaade-kosha/submission/`
- **Excel Extras**: `gaade-kosha/submission/extras/gaades.xlsx`, `gaade-kosha/submission/extras/situations.xlsx`
- **No-BOM Documentation Mirrors**: `gaade-kosha/submission/docs/utf8_no_bom/`
