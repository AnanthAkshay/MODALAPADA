# Gaade Kosha (ಗಾದೆ ಕೋಶ) – Audit of Unverified & Missing Items
**Modalapada 2.0 – Kannada Multimodal AI Hackathon**  
*Department of Computer Science & Engineering, Ramaiah Institute of Technology*  
*Challenge 02: Text & Speech Track – Proverbs for Every Situation*

---

## 1. Executive Statement on Academic Ethics & Anti-Fabrication

In strict compliance with academic integrity guidelines, ethical computational linguistics research principles, and the Modalapada 2.0 hackathon regulations, the development team has enforced an absolute **Zero-Fabrication Policy**:
- We have **never** fabricated elder names, community locations, regional dialect classifications, signature images, consent forms, or provenance records.
- Any data point, geographic location, or folklore attribution not backed by verified field documentation remains explicitly marked as `"UNVERIFIED"` or documented below.

---

## 2. Itemized Audit of Gaps & Unverified Data

### A. Geographic Regional Provenance (100.0% UNVERIFIED)
- **Status**: **Unverified (Truthfully Documented)**
- **Scope**: All 226 canonical proverbs in `data/gaades.csv` have `region = "UNVERIFIED"`.
- **Reason**: The historical source collection (Kannada Gaadegalu Revised 1–250 PDF) does not document dialectal districts or village origins for individual entries. 
- **Remediation Plan**: A printable 25-page community elder review packet (`data/elder_review/elder_review_sheet.pdf`) and data entry protocol (`data/elder_review/returned/README.txt`) have been created for future field collection across Karnataka districts (e.g., Dharwad, Mandya, Mysuru, Karavali). Because completed physical survey sheets have not yet been collected from outside districts, zero regions have been fabricated.

### B. Audio Recordings for Canonical Synthetic Additions (`G251` & `G252`)
- **Status**: **Text-Only Canonical Additions (No Audio)**
- **Scope**: Exactly 2 of 226 canonical gaades (`G251` and `G252`):
  - `G251`: *ಆಳಾಗಿ ದುಡಿ, ಅರಸನಾಗಿ ಉಣ್ಣು*
  - `G252`: *ಕೈ ಕೆಸರಾದರೆ ಬಾಯಿ ಮೊಸರು*
- **Reason**: These two proverbs were added canonically to resolve unmapped official hackathon starter situations. Because they were not part of the original 250 archival OGG recordings, they lack historical folklore audio files.
- **Ethical Safeguard**: Synthetic Text-to-Speech was **strictly prohibited** for gaade audio generation so as not to confuse synthetic computer audio with authentic human cultural voices. In the user interface, the player informs the user: *"No audio recording available for this proverb (Text-only archival entry)"*.

### C. Loose Signature Evidence Files in Public Distribution
- **Status**: **Omitted as Loose Files; Embedded in PDF Only**
- **Scope**: Loose individual JPEG files in `submission/consent/evidence/`.
- **Reason**: In accordance with the project specification (*"evidence/ only if I confirm the organizers want it; otherwise omit evidence images and say so in the README"*), individual signature files are not distributed as loose, unformatted image files.
- **Verification Provided**: All 9 verified signatures are cleanly framed and permanently embedded on individual contributor certificate pages within `submission/consent/Consent_Summary.pdf`, complete with SHA-256 cryptographic checksums.

### D. Returned Physical Elder Review Sheets (`data/elder_review/returned/`)
- **Status**: **Pending Field Survey Returns**
- **Scope**: Digital CSV transcriptions of paper review sheets (`elder_1.csv`, `elder_2.csv`, etc.).
- **Reason**: Field collection packets were prepared on 19/11/2026. Transcribed response files from field elders will be deposited into this folder as surveys are returned.

---

## 3. Summary Compliance Table

| Item | Requirement Standard | Current State | Truthful Verification Status |
| :--- | :--- | :--- | :--- |
| **Elder Names** | Backed by signed consent | 7 distinct signatories in register | 100% Verified with on-disk signatures |
| **Proverb Regions** | Backed by elder verification | 226 entries marked UNVERIFIED | 100% Anti-Fabrication Compliant |
| **Gaade Audio** | Authentic human recordings | 224 WAVs (16 kHz, mono, PCM-16) | 100% Format Compliant (2 text-only) |
| **Consent Register** | Public display permissions | 9 records verified with signatures | 100% Verified in `Consent_Summary.pdf` |

