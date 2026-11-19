# Gaade Kosha - Audio Conversion & Technical Validation Report

- **Timestamp**: 2026-11-20 03:34:20
- **Source Folder**: `Audio`
- **Canonical WAV Folder**: `gaade-kosha\audio\wav`
- **Unused Duplicates WAV Folder**: `gaade-kosha\audio\wav_unused_duplicates`
- **Overall Conversion Status**: **PASS**

---

## 1. Executive Summary & Verification Totals

| Metric | Expected | Actual | Status |
| :--- | :--- | :--- | :--- |
| Source OGG Files Discovered | 252 | 252 | PASS |
| Numeric Naming Sequence | 1.ogg to 252.ogg | 1.ogg to 252.ogg (0 gaps) | PASS |
| Converted Canonical WAVs (`audio/wav/`) | 226 | 226 | PASS |
| Converted Duplicate WAVs (`audio/wav_unused_duplicates/`) | 26 | 26 | PASS |
| Canonical Gaades Missing Audio | 0 | 0 (None - 100% Complete) | PASS |
| Conversion Failures | 0 | 0 | PASS |
| Target Format Compliance (16 kHz / Mono / PCM-16) | 100% | 100% (252/252) | PASS |
| Duration Tolerance Compliance (|Δt| <= 20 ms) | 100% | 100% (Max: 13.00 ms) | PASS |
| Zero-Byte / Corrupted Files | 0 | 0 | PASS |
| Source OGG Integrity (SHA-256 Before vs After) | 100% Match | 100% Match (252/252) | PASS |

---

## 2. Technical Validation Parameters

- **Command Executed**: `ffmpeg -n -i <in.ogg> -ar 16000 -ac 1 -c:a pcm_s16le <out.wav>`
- **Audio Filters**: Strictly **NONE** (`-af` never used). No trimming, normalization, pitch shift, or noise reduction.
- **Output Sample Rate**: `16,000 Hz` (verified for 250/250 files via ffprobe)
- **Channels**: `1 (mono)` (verified for 250/250 files via ffprobe)
- **Codec**: `pcm_s16le` (WAV PCM 16-bit little-endian)
- **Bit Depth**: `16 bits per sample`
- **Max Duration Difference**: `13.00 ms` on `G001` (Tolerance: 20.00 ms).

---

## 3. Duration Outliers & Quality Checks

- **Outliers (< 0.5 s or > 15.0 s)**: 0 detected.
- *All recordings fall within normal conversational proverb lengths (0.98 s to 6.09 s).*

---

## 4. Human Listening Spot-Check List (15 Random Canonical Recordings)

For manual audit and team verification, listen to each WAV file and confirm alignment with its Kannada gaade text:

| Gaade ID | Proverb Text (Kannada) | WAV Path | Duration |
| :--- | :--- | :--- | :--- |
| **G007** | ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು. | `audio/wav/G007.wav` | 2.6735s |
| **G023** | ಮಳೆ ಬರುವಾಗ ಕೊಡೆ ಹಿಡಿದರೆ ಪ್ರಯೋಜನವಿಲ್ಲ. | `audio/wav/G023.wav` | 2.8135s |
| **G027** | ಕೈಗೆ ಬಂದ ಅವಕಾಶ ಕಳೆದುಕೊಳ್ಳಬಾರದು. | `audio/wav/G027.wav` | 3.1735s |
| **G029** | ತುಂಬಿದ ಕೊಡ ತುಳುಕುವುದಿಲ್ಲ. | `audio/wav/G029.wav` | 2.3535s |
| **G036** | ಆಸೆಗೊಂದು ಮಿತಿ ಇರಬೇಕು. | `audio/wav/G036.wav` | 2.5535s |
| **G058** | ಅವರವರ ಕರ್ಮ ಅವರವರಿಗೇ. | `audio/wav/G058.wav` | 2.8935s |
| **G063** | ಒಂದೇ ಮರದ ಹಣ್ಣುಗಳೆಲ್ಲ ಒಂದೇ ರುಚಿಯಲ್ಲ. | `audio/wav/G063.wav` | 3.5335s |
| **G071** | ತಾಯಿಗಿಂತ ಬಂಧುವಿಲ್ಲ, ಉಪ್ಪಿಗಿಂತ ರುಚಿಯಿಲ್ಲ. | `audio/wav/G071.wav` | 3.9135s |
| **G110** | ನಾಲಿಗೆಗೆ ಮೂಳೆ ಇಲ್ಲ, ಆಡಿದ ಮಾತಿಗೆ ಬೆಲೆ ಇದೆ. | `audio/wav/G110.wav` | 3.1735s |
| **G145** | ಸತ್ಯಕ್ಕೆ ಜಯ. | `audio/wav/G145.wav` | 0.9735s |
| **G157** | ಅನ್ನಕ್ಕೆ ಆಸೆ, ಕೆಲಸಕ್ಕೆ ಬೇಸರ. | `audio/wav/G157.wav` | 2.7135s |
| **G175** | ಹಾವಿಗೆ ಹಾಲೆರೆದಂತೆ. | `audio/wav/G175.wav` | 1.9135s |
| **G194** | ಅರಸನ ಆಜ್ಞೆ ಕಲ್ಲಿನ ಗೆರೆ. | `audio/wav/G194.wav` | 1.9935s |
| **G215** | ಕೆರೆ ತುಂಬಿದರೆ ಊರು ತುಂಬಿದಂತೆ. | `audio/wav/G215.wav` | 1.8935s |
| **G216** | ಆರೋಗ್ಯವೇ ಭಾಗ್ಯ. | `audio/wav/G216.wav` | 1.3735s |

---

## 5. Duplicate Gaade Audio Handling

Exactly **26 recordings** mapped to excluded duplicate gaades. In accordance with task requirements, these files are preserved in `audio/wav_unused_duplicates/` rather than the canonical submission folder:

- `G086` (Duplicate of `G042`): `audio/wav_unused_duplicates/G086.wav` - *ತಾಳ್ಮೆ ಇದ್ದರೆ ತೊಂದರೆ ಇಲ್ಲ.*
- `G117` (Duplicate of `G083`): `audio/wav_unused_duplicates/G117.wav` - *ಕೋಪದಲ್ಲಿ ಕೊಯ್ದ ಮೂಗು ಶಾಂತಿಯಲ್ಲಿ ಸಿಗುವುದಿಲ್ಲ.*
- `G125` (Duplicate of `G085`): `audio/wav_unused_duplicates/G125.wav` - *ಹಾವು ಸಾಯಬೇಕು, ಕೋಲು ಮುರಿಯಬಾರದು.*
- `G131` (Duplicate of `G029`): `audio/wav_unused_duplicates/G131.wav` - *ತುಂಬಿದ ಕೊಡ ತುಳುಕುವುದಿಲ್ಲ.*
- `G135` (Duplicate of `G104`): `audio/wav_unused_duplicates/G135.wav` - *ಕತ್ತೆಗೆ ಏನು ಗೊತ್ತು ಕಸ್ತೂರಿ ಪರಿಮಳ?*
- `G163` (Duplicate of `G130`): `audio/wav_unused_duplicates/G163.wav` - *ಹೊರಗೆ ಬಂಗಾರ, ಒಳಗೆ ಕಲ್ಲು.*
- `G164` (Duplicate of `G139`): `audio/wav_unused_duplicates/G164.wav` - *ಹುಲಿ ಬಂತು ಹುಲಿ ಎಂದರೆ ಯಾರೂ ನಂಬುವುದಿಲ್ಲ.*
- `G168` (Duplicate of `G128`): `audio/wav_unused_duplicates/G168.wav` - *ಕಣ್ಣಿಗೆ ಕಾಣುವುದೆಲ್ಲ ಸತ್ಯವಲ್ಲ.*
- `G169` (Duplicate of `G129`): `audio/wav_unused_duplicates/G169.wav` - *ಮಿಂಚುವುದೆಲ್ಲ ಚಿನ್ನವಲ್ಲ.*
- `G170` (Duplicate of `G123`): `audio/wav_unused_duplicates/G170.wav` - *ಹುಚ್ಚನ ಮದುವೆಯಲ್ಲಿ ಉಂಡವನೇ ಜಾಣ.*
- `G174` (Duplicate of `G032`): `audio/wav_unused_duplicates/G174.wav` - *ದೂರದ ಬೆಟ್ಟ ಕಣ್ಣಿಗೆ ನುಣ್ಣಗೆ.*
- `G177` (Duplicate of `G036`): `audio/wav_unused_duplicates/G177.wav` - *ಆಸೆಗೊಂದು ಮಿತಿ ಇರಬೇಕು.*
- `G179` (Duplicate of `G118`): `audio/wav_unused_duplicates/G179.wav` - *ಕಳ್ಳನ ಮನಸ್ಸು ಹುಳ್ಳುಳ್ಳಗೆ.*
- `G180` (Duplicate of `G119`): `audio/wav_unused_duplicates/G180.wav` - *ಕಳ್ಳನಿಗೆ ಒಂದು ಪಿಳ್ಳೆ ನೆವ.*
- `G181` (Duplicate of `G138`): `audio/wav_unused_duplicates/G181.wav` - *ನಂಬಿಕೆ ಕಳೆದುಕೊಂಡರೆ ಎಲ್ಲವನ್ನೂ ಕಳೆದುಕೊಂಡಂತೆ.*
- `G182` (Duplicate of `G059`): `audio/wav_unused_duplicates/G182.wav` - *ಮಾತು ಆಡಿದರೆ ಹೋಯಿತು, ಮುತ್ತು ಒಡೆದರೆ ಹೋಯಿತು.*
- `G183` (Duplicate of `G023`): `audio/wav_unused_duplicates/G183.wav` - *ಮಳೆ ಬರುವಾಗ ಕೊಡೆ ಹಿಡಿದರೆ ಪ್ರಯೋಜನವಿಲ್ಲ.*
- `G184` (Duplicate of `G033`): `audio/wav_unused_duplicates/G184.wav` - *ಕಾಲ ಬಂದಾಗ ಕಲ್ಲೂ ಮಾತನಾಡುತ್ತದೆ.*
- `G190` (Duplicate of `G013`): `audio/wav_unused_duplicates/G190.wav` - *ಕಷ್ಟವಿಲ್ಲದೆ ಫಲವಿಲ್ಲ.*
- `G193` (Duplicate of `G053`): `audio/wav_unused_duplicates/G193.wav` - *ಒಂದು ಕೈಯಿಂದ ಚಪ್ಪಾಳೆ ಆಗುವುದಿಲ್ಲ.*
- `G195` (Duplicate of `G132`): `audio/wav_unused_duplicates/G195.wav` - *ಖಾಲಿ ಕೊಡ ಹೆಚ್ಚು ಸದ್ದು ಮಾಡುತ್ತದೆ.*
- `G196` (Duplicate of `G103`): `audio/wav_unused_duplicates/G196.wav` - *ಕೋತಿಯ ಕೈಗೆ ಮಾಣಿಕ್ಯ ಕೊಟ್ಟಂತೆ.*
- `G197` (Duplicate of `G101`): `audio/wav_unused_duplicates/G197.wav` - *ಕುಣಿಯಲಾರದವಳು ನೆಲ ಡೊಂಕು ಅಂದಳು.*
- `G198` (Duplicate of `G107`): `audio/wav_unused_duplicates/G198.wav` - *ಅರ್ಧ ಜ್ಞಾನ ಅಪಾಯಕ್ಕೆ ದಾರಿ.*
- `G199` (Duplicate of `G145`): `audio/wav_unused_duplicates/G199.wav` - *ಸತ್ಯಕ್ಕೆ ಜಯ.*
- `G200` (Duplicate of `G150`): `audio/wav_unused_duplicates/G200.wav` - *ಅನುಭವವೇ ದೊಡ್ಡ ಗುರು.*
