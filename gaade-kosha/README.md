# Gaade Kosha (ಗಾದೆ ಕೋಶ) – Proverbs for Every Situation

<div align="center">

![Modalapada 2.0](https://img.shields.io/badge/Modalapada%202.0-Hackathon%20Track%202-red?style=for-the-badge&logo=target)
[![Live Frontend](https://img.shields.io/badge/Live%20App-modalapada.vercel.app-brightgreen?style=for-the-badge&logo=vercel)](https://modalapada.vercel.app)
[![API Server](https://img.shields.io/badge/API%20Server-modalapada.onrender.com-blue?style=for-the-badge&logo=render)](https://modalapada.onrender.com)
[![API Docs](https://img.shields.io/badge/Swagger-OpenAPI%20Interactive%20Docs-orange?style=for-the-badge&logo=fastapi)](https://modalapada.onrender.com/docs)
[![Tests Passing](https://img.shields.io/badge/Tests-51%2F51%20Passing%20(100%25)-success?style=for-the-badge&logo=pytest)](docs/TEST_REPORT.md)
[![Audio Coverage](https://img.shields.io/badge/Elder%20Audio-100%25%20(226%2F226%20Canonical)-purple?style=for-the-badge&logo=waveform)](audio/wav/)

**An intelligent, multimodal conversational companion that bridges centuries-old Kannada folk wisdom with modern daily dilemmas.**

*Built for the **Modalapada 2.0 Hackathon** by Department of Computer Science & Engineering, Ramaiah Institute of Technology, Bengaluru.*

[Live Web Application](https://modalapada.vercel.app) • [Interactive API Docs](https://modalapada.onrender.com/docs) • [System Architecture](#system-architecture) • [Benchmark Evaluation](#benchmark-evaluation-the-17-golden-cases) • [Quickstart Guide](#quickstart--developer-guide)

---

</div>

## Visual Showcase & Screenshots

<div align="center">

### 1. Modern Web Application (Light & Dark Theme with Kannada Typography)
| Light Mode (Heritage Cream & Kumkum Red) | Dark Mode (Deep Charcoal & Gold Accent) |
| :---: | :---: |
| ![Home Light](gaade-kosha/docs/screenshots/ui_home_light.png) | ![Home Dark](gaade-kosha/docs/screenshots/ui_home_dark.png) |

---

### 2. Semantic Proverb Matching & Grounded Bilingual Explanations
| Real-time Match Result & Audio Player | Mobile-First Responsive UI (360px) |
| :---: | :---: |
| ![Result Card](gaade-kosha/docs/screenshots/ui_result_match.png) | ![Mobile UI](gaade-kosha/docs/screenshots/ui_mobile_view.png) |

---

### 3. Cultural Heritage Archive & Cloud Infrastructure
| 226 Proverb Archive & Thematic Filter | Live Cloud Container Deployment on Render |
| :---: | :---: |
| ![Browse Catalog](gaade-kosha/docs/screenshots/ui_browse_catalog.png) | ![Render Deploy](gaade-kosha/docs/screenshots/render_deploy_live.jpg) |

</div>

---

## Executive Summary & The "Why"

In Kannada folklore, proverbs (*ಗಾದೆಗಳು*) are not merely rhetorical flourishes; they represent centuries of distilled ethical heuristics, conflict resolution principles, and social wisdom. However, modern speakers and younger generations often struggle to connect their lived experiences (e.g., student burnout, consumer EMI traps, office credit stealing, online scams) with the traditional metaphoric vocabulary of their grandparents.

**Gaade Kosha solves this cultural transmission gap:**
1. **Multimodal Ingestion**: Users type or speak their real-life dilemma in English, standard Kannada, or colloquial **Kanglish** (Latin-scripted Kannada).
2. **Philosophical Semantic Resonance**: Unlike simple keyword matchers that look for literal word overlaps, Gaade Kosha employs a **Zero-Shot Philosophical Reasoner** (Google Gemini 2.5 Flash / Groq LLM) that maps modern human conflicts to the timeless folk truths underlying the proverbs.
3. **100% Authentic Elder Audio**: Every canonical proverb is voiced by authentic human speakers (226 of 226 canonical proverbs with standardized 16 kHz mono WAV audio).
4. **Bilingual Grounded Justifications**: The system provides situational reasons in both Kannada (*ಯಾಕೆ ಈ ಗಾದೆ ಹೊಂದುತ್ತದೆ?*) and English, explaining the philosophical metaphor clearly.
5. **Strict Ethical Archival Standards**: Zero fabrication of regional origins (marked truthfully as `UNVERIFIED`), verifiable signed contributor consent registers, and explicit machine-voice disclosure.

---

## System Architecture

Gaade Kosha is engineered as a cloud-native, decoupled, multi-tier system designed for ultra-low latency, robust error recovery, and strict data integrity.

```mermaid
flowchart TD
    subgraph Client ["Client Browser (Mobile & Desktop)"]
        UI["React 18 + Vite Web Interface<br/>(Tailwind CSS • Noto Serif Kannada)"]
        ASR_Client["Web Speech API (Chrome / Edge)<br/>Native In-Browser Voice Input"]
        AudioPlayer["HTML5 / Web Audio Player<br/>(16 kHz Mono Archival Stream)"]
        TTS["Web SpeechSynthesis<br/>('machine voice' Tagged Narration)"]
        
        UI <--> ASR_Client
        UI <--> AudioPlayer
        UI <--> TTS
    end

    subgraph Edge ["Edge CDN (Vercel)"]
        VercelEdge["Vercel Edge Proxy & Routing<br/>(modalapada.vercel.app)"]
        ASR_Fallback["Brave/Privacy Fallback Handler<br/>(Serverless Audio Pipe)"]
    end

    subgraph Backend ["Production Backend Service (Render - Port 8000)"]
        FastAPI["FastAPI High-Performance Async Gateway<br/>(Pydantic v2 • CORS • Sliding Rate Limiter)"]
        
        subgraph Intelligence ["Multi-Tier Semantic Matching Pipeline"]
            Guardrail["Input Sanitizer & Prompt-Injection Guardrail<br/>(Token Normalizer • Length Clamping)"]
            
            subgraph PrimaryEngine ["Primary: Zero-Shot Philosophical Engine"]
                Gemini["Google Gemini 2.5 Flash<br/>(226 Proverb Reasoning Context)"]
                Groq["Groq Cloud Failover<br/>(openai/gpt-oss-120b • qwen3.8-27b)"]
                FailoverRouter{"Dynamic Multi-Model<br/>Failover Router"}
            end
            
            subgraph SecondaryEngine ["Secondary: Resilient Offline Engine"]
                TFIDF["Subword (2-5) & Word (1-2) TF-IDF<br/>(Scikit-Learn Sparse Vectorizer)"]
                BM25["BM25Okapi Lexical Ranker<br/>(Morphological Kannada Tokenizer)"]
                RRF["Reciprocal Rank Fusion (RRF)<br/>k = 60 Score Aggregator"]
            end
        end

        subgraph AudioService ["Audio & Archival Engine"]
            ASR_Backend["Groq Whisper Large-v3<br/>(Dual-Language Speech-to-Text)"]
            AudioStreamer["Static WAV Streaming Engine<br/>(G001.wav - G252.wav)"]
        end

        subgraph DataStore ["Canonical Data Layer"]
            DB_Gaades[("gaades.csv / SQLite<br/>226 Canonical Proverbs")]
            DB_Situations[("situations.csv<br/>452 Balanced Situations")]
            DB_Consent[("consent_register.csv<br/>Signed Contributor Ledger")]
            AudioStore[("audio/wav/<br/>226 16 kHz Mono Master WAVs")]
        end
    end

    UI -->|HTTPS Request| VercelEdge
    VercelEdge -->|Proxy API Requests| FastAPI
    UI -.->|Brave ASR Fallback| ASR_Fallback
    ASR_Fallback -->|Transcribe Audio| ASR_Backend

    FastAPI --> Guardrail
    Guardrail --> FailoverRouter
    FailoverRouter -->|Primary| Gemini
    Gemini -.->|On 404/429/Timeout| Groq
    FailoverRouter -.->|Fallback on Network Cut| RRF
    RRF --> TFIDF
    RRF --> BM25

    Gemini -->|Proverb ID & Bilingual Reasons| DB_Gaades
    Groq -->|Proverb ID & Bilingual Reasons| DB_Gaades
    RRF -->|Ranked Proverb IDs| DB_Gaades
    
    FastAPI --> AudioStreamer
    AudioStreamer --> AudioStore
    AudioStreamer -->|Stream WAV Audio| AudioPlayer
```

---

## Benchmark Evaluation: The 17 Golden Cases

To validate the philosophical depth of Gaade Kosha over simple keyword searches, the system was benchmarked against 17 challenging real-world scenarios representing money, study, workplace, relationships, causation fallacies, and vernacular idioms.

| # | Scenario & Dilemma | Input Text Snippet | Expected Gaade | Gaade Kosha Output | Confidence | Status |
|:---:|:---|:---|:---|:---|:---:|:---:|
| **1** | **The EMI Trap** | *Divya earns ₹22k, bought ₹70k phone on EMI, now skipping outings...* | `G007` / `G152` | **G152** ಸಾಲ ಮಾಡಿ ತುಪ್ಪ ತಿನ್ನಬೇಡ | **0.95** |  **Exact** |
| **2** | **Show-off Without Savings** | *Suresh arrives in rented luxury car, shop rent unpaid for 2 months...* | `G155` / `G156` | **G155** ಕೈಯಲ್ಲಿ ಕಾಸಿಲ್ಲ, ಜೇಬಿನಲ್ಲಿ ಜಂಬ | **0.95** |  **Exact** |
| **3** | **Last-Minute Panic** | *Ananya ignored DS all semester; night before lab exam tries to learn linked lists...* | `G251` / `G023` | **G251** ಬೆಂಕಿ ಬಂದಾಗ ಬಾವಿ ತೋಡಿದಂತೆ | **0.95** |  **Exact** |
| **4** | **The Office Boaster** | *Kiran promises dashboard by tomorrow, teammates secretly cover for him...* | `G132` / `G114` | **G132** ಖಾಲಿ ಕೊಡ ಹೆಚ್ಚು ಸದ್ದು ಮಾಡುತ್ತದೆ | **0.95** |  **Exact** |
| **5** | **Forgetting Who Helped** | *Meghana coached by senior for dream job, now ignores messages and claims sole credit...* | `G038` | **G038** ಹತ್ತಿದ ಏಣಿ ಒದೆಯಬಾರದು | **0.95** |  **Exact** |
| **6** | **Fight That Went Too Far** | *Rohit proved he was right with receipts, friend walked out, hasn't spoken in a month...* | `G077` | **G077** ಜಗಳದಲ್ಲಿ ಗೆದ್ದರೂ ಸ್ನೇಹ ಕಳೆದುಕೊಳ್ಳಬೇಡ | **0.95** |  **Exact** |
| **7** | **Kind Outside, Harsh Inside** | *Mahesh helps neighbourhood weddings, but short-tempered with aged parents...* | `G065` | **G065** ಮನೆಗೆ ಮಾರಿ, ಊರಿಗೆ ಉಪಕಾರಿ | **0.95** |  **Exact** |
| **8** | **Quick to Judge Others** | *Pooja complains roommate leaves dishes; her own clothes scattered everywhere...* | `G081` | **G081** ಪರರ ಕಣ್ಣಿನ ಹುಲ್ಲು ಕಾಣುತ್ತದೆ, ತನ್ನ ಕಣ್ಣಿನ ಮರ ಕಾಣುವುದಿಲ್ಲ | **0.95** |  **Exact** |
| **9** | **The Boy Who Cried Wolf** | *Nikhil faked emergencies 3 times; manager refuses leave when dad is really ill...* | `G139` | **G139** ಹುಲಿ ಬಂತು ಹುಲಿ ಎಂದರೆ ಯಾರೂ ನಂಬುವುದಿಲ್ಲ | **0.95** |  **Exact** |
| **10** | **Looks Good, Isn't Good** | *Glossy website promised premium tailor; clothes arrived badly stitched...* | `G129` / `G130` | **G130** ಹೊರಗೆ ಬಂಗಾರ, ಒಳಗೆ ಕಲ್ಲು | **0.95** |  **Exact** |
| **11** | **Missed the Season** | *Basavaraj postponed sowing ragi due to relative's wedding; neighbours fields green...* | `G207` | **G207** ಬಿತ್ತುವ ಕಾಲದಲ್ಲಿ ಮಲಗಿದರೆ ಕೊಯ್ಯುವ ಕಾಲದಲ್ಲಿ ಅಳಬೇಕು | **0.95** |  **Exact** |
| **12** | **The Village Lake** | *Villagers cleaned lake and repaired bunds; all farms have abundant summer water...* | `G215` | **G215** ಕೆರೆ ತುಂಬಿದರೆ ಊರು ತುಂಬಿದಂತೆ | **0.95** |  **Exact** |
| **13** | **Correlation vs Causation** | *Rumour says new teacher is bad luck because school tree fell day she joined...* | `G187` | **G187** ಕಾಗೆ ಕುಳಿತದ್ದಕ್ಕೆ ಕೊಂಬೆ ಮುರಿಯಿತೇ? | **0.95** |  **Exact** |
| **14** | **Advice Ignored Again** | *Father warned Arjun 5 times not to lend money to friend; Arjun lends again...* | `G113` / `G102` | **G113** ಹಿತ್ತಾಳೆ ಕಿವಿಗೆ ಶಂಖ ಊದಿದಂತೆ | **0.95** |  **Exact** |
| **15** | **Burnt Once, Too Careful** | *Sneha cheated in scam last year; now refuses even genuine bank fixed deposits...* | `G142` | **G142** ಹಾಲು ಕುಡಿದ ಮಗು ಬೆಕ್ಕಿಗೆ ಹೆದರುತ್ತದೆ | **0.95** |  **Exact** |
| **16** | **Kanglish Preparation** | *nanna friend exam ge ondu thingala munche matra odoke start madida, ega blame madthane...* | `G023` / `G251` | **G251** ಬೆಂಕಿ ಬಂದಾಗ ಬಾವಿ ತೋಡಿದಂತೆ | **0.95** |  **Exact** |
| **17** | **Kannada Family Conflict** | *ನಮ್ಮ ಅಜ್ಜಿ ಮನೆಯಲ್ಲಿ ಎಲ್ಲರೂ ಅಭಿಪ್ರಾಯ ಬೇರೆ ಬೇರೆ ಹೇಳುತ್ತಾರೆ, ಒಬ್ಬರು ಇದು ಅಂದರೆ ಇನ್ನೊಬ್ಬರು ಬೇಡ...* | `G062` / `G073` | **G073** ಮನೆಯೊಂದು ಮನಸ್ಸು ನೂರು | **0.95** |  **Exact** |

> **Key Finding**: Pure lexical TF-IDF matchers scored only **35.3% Top-1** on these cases because user dilemmas rarely repeat the exact words of proverbs (e.g. *tree falling on teacher* does not contain the word *crow* or *branch*). Gaade Kosha's LLM reasoning engine achieves **100.0% Top-1 accuracy** by recognizing philosophical metaphors.

---

## Key Technical Innovations

### 1. 100% Authentic Elder Audio Coverage
- Every canonical proverb (`G001` to `G226`) has a verified 16 kHz Mono, 16-bit PCM master WAV recording voiced by native Kannada speakers.
- Standardized file paths (`audio/wav/G001.wav` .. `G226.wav`) with zero corruptions, zero duplicate hashes, and consistent loudness normalization.

### 2. Dual-Engine Multi-Model Failover
- **Primary Model**: Google Gemini 2.5 Flash (`gemini-2.5-flash`) providing sub-second semantic matching with deep Kannada vernacular grounding.
- **Auto-Failover 1**: Google Gemini Flash Latest (`gemini-flash-latest`) / Gemini 2.0.
- **Auto-Failover 2**: Groq High-Speed Inference (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `llama-3.3-70b-versatile`).
- **Resilient Fallback**: If internet connectivity is completely lost, the system automatically degrades to offline Hybrid TF-IDF + BM25Okapi with 0 HTTP 500 errors.

### 3. Dual-Mode Speech Recognition (Brave & Privacy Resilient)
- Native Chrome / Edge: Instant, zero-cost in-browser `webkitSpeechRecognition` for `kn-IN` and `en-IN`.
- Brave Browser / Firefox: Automatically detects Brave Shields / Google ASR network blocks and switches to a server-side **Groq Whisper Large-v3** audio pipeline via `MediaRecorder`.

### 4. Anti-Hallucination & Anti-Fabrication Architecture
- **ID-Only Inference**: The LLM outputs only the canonical Proverb ID (`G001` - `G226`) and situational reasons. All Kannada script, English translations, audio links, and metadata are hydrated directly from the local authoritative database. The model can never invent a non-existent proverb.
- **Honest Regional Attribution**: All 226 proverbs have their region recorded as `"UNVERIFIED"`. We refuse to invent regional origins without physical signed verification forms.

---

## Dataset & Archival Metrics

All metrics are validated directly against [data/gaades.csv](data/gaades.csv), [data/situations.csv](data/situations.csv), and [data/gaade_provenance.csv](data/gaade_provenance.csv):

| Metric | Measured Value | Verification Method |
|:---|:---:|:---|
| **Canonical Proverbs** | `226` | 100% unique IDs (`G001`–`G226`), zero missing fields |
| **Contextual Situations** | `452` | Exactly 2 per proverb (1 Kannada, 1 English) |
| **Thematic Categories** | `15` | Character, Society, Money, Work, Family, etc. |
| **Master WAV Audio Files** | `226` | 16 kHz, Mono, 16-bit PCM (100% full coverage) |
| **Duplicate Audio Hashes** | `0` | Verified unique SHA-256 digital audio signatures |
| **Unicode Errors (`U+FFFD`)** | `0` | Byte-level UTF-8 Kannada script preservation |
| **Informed Consent Records** | `9` | Signed contributor agreements (Hassan, Shivamogga, Bengaluru) |

---

## Quickstart & Developer Guide

### Option A: Run Full Stack Locally in 2 Commands

```bash
# 1. Clone repository and install dependencies
git clone https://github.com/AnanthAkshay/MODALAPADA.git
cd MODALAPADA
pip install -r requirements.txt

# 2. Start unified server (serves FastAPI + React Web UI on port 8000)
python -m uvicorn backend.app.main:app --port 8000
```
- Open **`http://localhost:8000/index.html`** in your browser.
- Interactive API documentation: **`http://localhost:8000/docs`**.

### Option B: Development Mode (Hot Reloading)

```bash
# Terminal 1: Backend
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```
- Vite Dev Server runs at `http://localhost:5173/` and proxies all `/api` calls directly to port 8000.

### Option C: Run Automated Test Suite

```bash
# Run all 51 backend unit, integration, and security tests
python -m pytest gaade-kosha/backend/tests -v
```

---

## Production API Endpoints

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/health` | System health check, database status, and catalog counts |
| `POST` | `/api/match` | Accepts text/voice situation and returns best proverb with bilingual reasons |
| `GET` | `/api/gaades` | Searchable and filterable catalog of all 226 canonical proverbs |
| `GET` | `/api/gaades/{id}` | Detailed proverb metadata, usage contexts, and audio references |
| `GET` | `/api/gaades/{id}/audio` | Streams standardized 16 kHz mono WAV authentic elder audio |
| `POST` | `/api/transcribe` | High-speed server-side ASR for voice input on privacy browsers |
| `GET` | `/api/debug-llm` | Diagnostic endpoint inspecting configured LLM providers and live API status |
| `GET` | `/docs` | Interactive Swagger UI for live API testing |

---

## Team & Credits

**Built for Modalapada 2.0 Hackathon (Department of CSE, Ramaiah Institute of Technology, Bengaluru)**

### Team Members
- **Akshay A** – Full-Stack Architecture, LLM Matcher & Multi-Model Failover
- **Tejas M** – Frontend UI/UX, Typography & Responsive Redesign
- **H M Pranav** – Audio Engineering, ASR Fallback Pipeline & Voice Contributor
- **Aaditya V** – Data Engineering, Kannada Unicode Normalization & Voice Contributor

### Contributor Attributions (Recorded in Consent Register)
- **Shantha B M** (Grandmother, Hassan) – Contributor for 125 Folk Proverbs
- **Kumaraswamy H** (Grandfather, Shivamogga) – Contributor for 125 Folk Proverbs
- **Akshatha A** (Bengaluru) – Audio Contributor for 150 Master Recordings

---

## Submission Checklist Compliance

- [x] **226 Canonical Proverbs** verified in `gaades.csv` with zero missing values.
- [x] **452 Situations** verified in `situations.csv` with paired Kannada & English contexts.
- [x] **100% Authentic Elder Audio** verified in `audio/wav/` (226 16 kHz mono WAV files).
- [x] **Zero Fabricated Regions**: All 226 regions documented honestly as `"UNVERIFIED"`.
- [x] **Trilingual & Multimodal**: Seamless voice and text input in Kannada, English, and Kanglish.
- [x] **Zero Hallucination Guarantee**: Strict ID-only LLM resolution hydrated from database.
- [x] **51/51 Tests Passing** in official Pytest test suite.
- [x] **Live Deployed**: Accessible globally at [modalapada.vercel.app](https://modalapada.vercel.app).
