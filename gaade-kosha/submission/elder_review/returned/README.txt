================================================================================
Modalapada 2.0 – Gaade Kosha (Problem 2)
Elder Review Sheet Data Entry Guidelines
Folder: data/elder_review/returned/
================================================================================

1. Purpose:
-----------
This directory stores digital entry files transcribed directly from physical
paper Elder Review Sheets (elder_review_sheet.pdf) completed by community elders.
The responses in these files provide authentic field evidence for populating
the `region` column in `data/gaades.csv` and updating provenance records without
fabricating any elder identities or geographical distributions.

2. File Naming Convention:
--------------------------
Each completed elder review paper form must be transcribed into a separate CSV
file named sequentially:
  - elder_1.csv
  - elder_2.csv
  - elder_3.csv
  ... and so on.

Do NOT name files with personal elder names. Use the sequential identifier to
preserve contributor anonymity.

3. File Format & Structure:
---------------------------
Each returned CSV file must strictly follow this structure:

Line 1 (Metadata Header Row):
elder_place_or_district=<Village, Town, or District Name>
Example: elder_place_or_district=Mandya
(If unknown or unstated, write: elder_place_or_district=UNVERIFIED)

Line 2 (Column Headers):
gaade_id,I_know_this,I_use_it_in_my_area,correction

Lines 3 to 228 (Data Rows):
- gaade_id: The canonical ID (e.g., G001, G002, etc.)
- I_know_this: Y if elder checked YES; N if elder checked NO; leave empty if skipped
- I_use_it_in_my_area: Y if elder confirmed usage in their region; N if not; leave empty if skipped
- correction: Any local dialectal variant, pronunciation spelling, or phrasing note written by the elder (e.g., "ಕೈ ಕೆಸರಾದ್ರೆ ಬಾಯಿ ಮೊಸ್ರು")

Example of a valid elder_1.csv:
--------------------------------
elder_place_or_district=Dharwad
gaade_id,I_know_this,I_use_it_in_my_area,correction
G001,Y,Y,
G002,Y,Y,ಕೈ ಕೆಸ್ರಾದ್ರ ಬಾಯಿ ಮೊಸ್ರು
G003,Y,N,ಮಾಡಿದ್ದಣ್ಣೋ ಮಹಾರಾಯ
G004,N,N,
...

4. Data Integrity & Ethical Rules:
----------------------------------
- NEVER pre-fill, simulate, or fabricate responses.
- Transcribe ONLY what the elder has physically marked on the verified paper sheet.
- Keep the signed physical paper consent form filed safely in accordance with
  docs/consent/CONSENT_TEMPLATE.md.
- Link the assigned contributor ID with docs/consent/consent_register.csv.
- Leave this folder empty (except for this README.txt) until authentic field review
  sheets are collected and returned by team researchers.
================================================================================

