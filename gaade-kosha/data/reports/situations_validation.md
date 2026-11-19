# Gaade Kosha - Situations Dataset Validation Report

- **Timestamp**: 2026-11-19 18:32:52
- **Overall Status**: **PASS**
- **Primary Situations File**: `data\situations.csv`
- **Held-Out Evaluation File**: `data\eval\heldout_situations.csv`

---

## 1. Summary Metrics

| Metric | Expected | Actual | Status |
| :--- | :--- | :--- | :--- |
| Canonical Gaades Count | 226 | 226 | PASS |
| Total Situations in `situations.csv` | 452 | 452 | PASS |
| Situations Per Canonical Gaade | 2 | 226 gaades @ 2 each | PASS |
| Unique `situation_id` Count | 452 | 452 | PASS |
| Empty Field Occurrences | 0 | 0 | PASS |
| Max Pairwise Jaccard Token Overlap | < 0.60 | 0.2857 | PASS |
| Max Overlap / min(len) | < 0.60 | 0.4545 | PASS |
| Held-Out Evaluation Set Size | 40 | 40 | PASS |
| Held-Out Unique Gaades | 40 | 40 | PASS |

---

## 2. Token Overlap Analysis

- **Highest Jaccard Similarity**: `0.2857` between `S031_2` and `S107_1`
- **Highest Overlap Coefficient**: `0.4545` between `S031_2` and `S107_1`
- **Result**: All situation pairs adhere strictly to the < 60% token overlap constraint.

---

## 3. Schema & Integrity Verification

- **Encoding**: UTF-8 validated across both primary and heldout CSV files.
- **Foreign Key Integrity**: 100% of referenced `gaade_id`s resolve to canonical entries in `gaades.csv`.
- **Source Attribution**: All rows tagged strictly with `situation_source='team_drafted'`. No fabricated elder attributions.
- **Starter Examples Included**:
  - `G007` (S007_1): Meena buying phone on EMI and struggling with rent.
  - `G251` (S251_1): Municipal corporation scrambled for backhoes only after torrential monsoon floods.
  - `G252` (S252_1): Comparing family life against glamorous social media posts vs internal debts.

---

## 4. Errors & Warnings

✅ **No errors detected. Dataset is fully valid and certified.**
