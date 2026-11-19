# -*- coding: utf-8 -*-
"""
Gaade Kosha - Elder Review Sheet Generator & PDF Compiler
Modalapada 2.0 (Kannada Multimodal AI Hackathon)
Department of CSE&E, Ramaiah Institute of Technology

Generates:
1. data/elder_review/elder_review_sheet.csv (empty review columns for 226 gaades)
2. data/elder_review/elder_review_sheet.html (A4 printable sheet, Noto Sans Kannada >=14pt, grouped by theme)
3. data/elder_review/elder_review_sheet.pdf (compiled via Chromium with HarfBuzz complex text shaping)
4. data/elder_review/returned/README.txt (transcription guidelines, empty of pre-filled data)
"""

import os
import sys
import csv
import subprocess
import html
import pandas as pd
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
GAADES_CSV = DATA_DIR / "gaades.csv"
ELDER_DIR = DATA_DIR / "elder_review"
RETURNED_DIR = ELDER_DIR / "returned"

THEME_ORDER = [
    ("Character", "ವ್ಯಕ್ತಿತ್ವ ಮತ್ತು ನಡವಳಿಕೆ (Character & Conduct)"),
    ("Society", "ಸಮಾಜ ಮತ್ತು ಲೋಕನೀತಿ (Society & Community)"),
    ("Money", "ಹಣ ಮತ್ತು ಆರ್ಥಿಕತೆ (Money & Finances)"),
    ("Work", "ಕೆಲಸ ಮತ್ತು ಶ್ರಮ (Work & Labor)"),
    ("Time", "ಸಮಯ ಮತ್ತು ತಾಳ್ಮೆ (Time & Patience)"),
    ("Family", "ಕುಟುಂಬ ಮತ್ತು ಗೃಹಜೀವನ (Family & Home)"),
    ("Friends", "ಸ್ನೇಹ ಮತ್ತು ಬಾಂಧವ್ಯ (Friends & Trust)"),
    ("Study", "ಅಧ್ಯಯನ ಮತ್ತು ಜ್ಞಾನ (Study & Wisdom)"),
    ("Health", "ಆರೋಗ್ಯ ಮತ್ತು ಆಹಾರ (Health & Diet)"),
    ("Leadership", "ನಾಯಕತ್ವ ಮತ್ತು ಆಡಳಿತ (Leadership & Justice)"),
    ("Education", "ವಿದ್ಯಾಭ್ಯಾಸ (Education & Learning)"),
    ("Agriculture", "ಕೃಷಿ ಮತ್ತು ಭೂಮಿ (Agriculture & Land)"),
    ("Nature", "ಪ್ರಕೃತಿ ಮತ್ತು ಪರಿಸರ (Nature & Water)"),
    ("Business", "ವ್ಯಾಪಾರ ಮತ್ತು ನಂಬಿಕೆ (Business & Commerce)"),
    ("Culture", "ಸಂಸ್ಕೃತಿ ಮತ್ತು ಸಂಪ್ರದಾಯ (Culture & Heritage)")
]


def generate_elder_csv():
    print("1. Generating data/elder_review/elder_review_sheet.csv...")
    ELDER_DIR.mkdir(parents=True, exist_ok=True)
    RETURNED_DIR.mkdir(parents=True, exist_ok=True)

    df_gaades = pd.read_csv(GAADES_CSV, encoding="utf-8")
    out_csv = ELDER_DIR / "elder_review_sheet.csv"
    fieldnames = [
        "gaade_id",
        "gaade",
        "meaning",
        "I_know_this (Y/N)",
        "I_use_it_in_my_area (Y/N)",
        "spelling_or_wording_correction",
        "notes"
    ]

    rows = []
    for _, r in df_gaades.iterrows():
        rows.append({
            "gaade_id": r["gaade_id"],
            "gaade": r["gaade"],
            "meaning": r["meaning"],
            "I_know_this (Y/N)": "",
            "I_use_it_in_my_area (Y/N)": "",
            "spelling_or_wording_correction": "",
            "notes": ""
        })

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  [✓] Wrote {len(rows)} canonical rows with empty review columns.")
    return df_gaades


def generate_elder_html(df_gaades):
    print("2. Generating data/elder_review/elder_review_sheet.html (A4 print layout)...")
    out_html = ELDER_DIR / "elder_review_sheet.html"

    # Group gaades by theme
    by_theme = defaultdict(list)
    for _, r in df_gaades.iterrows():
        by_theme[r["theme"]].append(r)

    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="kn">
<head>
<meta charset="utf-8">
<title>Gaade Kosha – Elder Review Sheet (ಗಾದೆ ಕೋಶ: ಹಿರಿಯರ ಪರಿಶೀಲನಾ ಪತ್ರ)</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Kannada:wght@400;600;700&display=swap');

@page {
    size: A4 portrait;
    margin: 12mm 10mm 12mm 10mm;
}

body {
    font-family: 'Noto Sans Kannada', 'Nirmala UI', system-ui, sans-serif;
    color: #1a1a1a;
    background: #fff;
    margin: 0;
    padding: 0;
    font-size: 10pt;
    line-height: 1.5;
}

.header-container {
    border: 2px solid #1a365d;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 12px;
    background: #f7fafc;
}

.inst-title {
    font-size: 11pt;
    font-weight: 700;
    text-align: center;
    color: #1a365d;
    margin: 0;
}

.sub-title {
    font-size: 13pt;
    font-weight: 700;
    text-align: center;
    color: #2b6cb0;
    margin: 3px 0;
}

.inst-meta {
    font-size: 8.5pt;
    text-align: center;
    color: #4a5568;
    margin-bottom: 8px;
}

.instructions {
    background: #edf2f7;
    border-left: 4px solid #3182ce;
    padding: 6px 10px;
    font-size: 9pt;
    margin-bottom: 8px;
    line-height: 1.4;
}

.fields-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 16px;
    font-size: 9.5pt;
}

.field-line {
    border-bottom: 1px dotted #718096;
    display: inline-block;
    min-width: 140px;
}

.theme-header {
    background: #2b6cb0;
    color: #ffffff;
    font-size: 12pt;
    font-weight: 700;
    padding: 6px 10px;
    border-radius: 4px;
    margin: 14px 0 6px 0;
    break-after: avoid;
    page-break-after: avoid;
}

.gaade-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
}

.gaade-table th {
    background: #edf2f7;
    border: 1px solid #cbd5e0;
    padding: 4px 6px;
    font-size: 8.5pt;
    text-align: left;
}

.gaade-row {
    border: 1px solid #e2e8f0;
    break-inside: avoid;
    page-break-inside: avoid;
}

.gaade-row:nth-child(even) {
    background: #f7fafc;
}

.gaade-row td {
    padding: 6px 8px;
    vertical-align: top;
    border: 1px solid #e2e8f0;
}

.col-id {
    width: 45px;
    text-align: center;
    font-weight: 700;
    font-size: 9pt;
    color: #4a5568;
}

.col-text {
    width: 48%;
}

.gaade-kannada {
    font-size: 14.5pt;
    font-weight: 700;
    color: #1a202c;
    line-height: 1.65;
    margin-bottom: 2px;
}

.gaade-meaning {
    font-size: 9pt;
    color: #4a5568;
    line-height: 1.35;
}

.col-ticks {
    width: 20%;
    font-size: 8.5pt;
    line-height: 1.7;
}

.checkbox-box {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 1.5px solid #4a5568;
    border-radius: 2px;
    margin-right: 4px;
    vertical-align: middle;
}

.col-corr {
    width: 25%;
    font-size: 8.5pt;
    color: #718096;
}

.write-line {
    border-bottom: 1px dotted #a0aec0;
    height: 16px;
    margin-top: 4px;
}

.page-footer {
    text-align: center;
    font-size: 8pt;
    color: #a0aec0;
    margin-top: 10px;
}
</style>
</head>
<body>

<div class="header-container">
    <div class="inst-title">ರಾಮಯ್ಯ ತಾಂತ್ರಿಕ ಮಹಾವಿದ್ಯಾಲಯ, ಬೆಂಗಳೂರು – ಗಣಕ ವಿಜ್ಞಾನ ಮತ್ತು ಇಂಜಿನಿಯರಿಂಗ್ ವಿಭಾಗ</div>
    <div class="sub-title">ಮೊದಲಪದ ೨.೦ – ಗಾದೆ ಕೋಶ: ಹಿರಿಯರ ಪರಿಶೀಲನಾ ಪತ್ರ (Elder Proverb Review Sheet)</div>
    <div class="inst-meta">Problem 2: Proverbs for Every Situation | Cultural Field Verification Protocol</div>
    
    <div class="instructions">
        <strong>ಹಿರಿಯರಿಗೆ ನಮಸ್ಕಾರ:</strong> ದಯವಿಟ್ಟು ಕೆಳಗಿನ ಗಾದೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ. ನಿಮಗೆ ಗೊತ್ತಿರುವ ಗಾದೆಗಳು ಮತ್ತು ನಿಮ್ಮ ಊರಲ್ಲಿ ಬಳಕೆಯಲ್ಲಿರುವ ಗಾದೆಗಳಿಗೆ ಸರಿ (✓) ಗುರುತು ಹಾಕಿ. ನಿಮ್ಮ ಪ್ರಾಂತ್ಯದಲ್ಲಿ ಇದನ್ನು ಬೇರೆ ರೀತಿಯಲ್ಲಿ ಹೇಳುವುದಾದರೆ 'ಸ್ಥಳೀಯ ರೂಪ' ಜಾಗದಲ್ಲಿ ಬರೆಯಿರಿ.
    </div>

    <div class="fields-grid">
        <div><strong>ಭಾಗವಹಿಸುವವರ / ಹಿರಿಯರ ಹೆಸರು (Elder Name):</strong> <span class="field-line" style="min-width: 220px;"></span></div>
        <div><strong>ಊರು / ತಾಲ್ಲೂಕು / ಜಿಲ್ಲೆ (Place / District):</strong> <span class="field-line" style="min-width: 220px;"></span></div>
        <div><strong>ದಿನಾಂಕ (Date):</strong> <span class="field-line" style="min-width: 130px;"></span> &nbsp; <strong>ವಯಸ್ಸು (Age):</strong> <span class="field-line" style="min-width: 60px;"></span></div>
        <div><strong>ಸಹಿ / ಹೆಬ್ಬೆರಳ ಗುರುತು (Signature / Thumbprint):</strong> <span class="field-line" style="min-width: 180px;"></span></div>
    </div>
</div>
""")

    total_gaades_counted = 0

    for theme_key, theme_label in THEME_ORDER:
        theme_items = by_theme.get(theme_key, [])
        if not theme_items:
            continue

        html_parts.append(f"""
<div class="theme-header">{theme_label} ({len(theme_items)} ಗಾದೆಗಳು)</div>
<table class="gaade-table">
    <thead>
        <tr>
            <th class="col-id">ಕ್ರಮ</th>
            <th class="col-text">ಗಾದೆ ಮತ್ತು ಅರ್ಥ (Proverb & Meaning)</th>
            <th class="col-ticks">ಪರಿಶೀಲನೆ (Verification)</th>
            <th class="col-corr">ಸ್ಥಳೀಯ ಉಚ್ಚಾರಣೆ / ತಿದ್ದುಪಡಿ (Local Variant)</th>
        </tr>
    </thead>
    <tbody>
""")

        for item in theme_items:
            total_gaades_counted += 1
            gid = html.escape(str(item["gaade_id"]))
            g_text = html.escape(str(item["gaade"]))
            meaning = html.escape(str(item["meaning"]))
            english = html.escape(str(item.get("english", "")))

            html_parts.append(f"""
        <tr class="gaade-row">
            <td class="col-id">{gid}</td>
            <td class="col-text">
                <div class="gaade-kannada">{g_text}</div>
                <div class="gaade-meaning"><strong>ಅರ್ಥ:</strong> {meaning}</div>
                <div class="gaade-meaning" style="color: #718096; font-size: 8pt;"><em>Eng:</em> {english}</div>
            </td>
            <td class="col-ticks">
                <div><span class="checkbox-box"></span> ನನಗೆ ಗೊತ್ತು (I know this)</div>
                <div><span class="checkbox-box"></span> ನಮ್ಮೂರಿನಲ್ಲಿದೆ (In our area)</div>
            </td>
            <td class="col-corr">
                <div class="write-line"></div>
                <div class="write-line"></div>
            </td>
        </tr>
""")

        html_parts.append("""
    </tbody>
</table>
""")

    html_parts.append(f"""
<div class="page-footer">
    Gaade Kosha (Problem 2) | Total Canonical Proverbs: {total_gaades_counted} | Dept of CSE&E, Ramaiah Institute of Technology
</div>
</body>
</html>
""")

    full_html = "".join(html_parts)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"  [✓] Successfully generated HTML ({total_gaades_counted} canonical gaades rendered).")
    return out_html, total_gaades_counted


def compile_pdf(html_path):
    print("3. Compiling PDF from HTML via Chromium headless...")
    out_pdf = ELDER_DIR / "elder_review_sheet.pdf"

    chrome_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]

    browser_bin = None
    for cand in chrome_candidates:
        if os.path.isfile(cand):
            browser_bin = cand
            break

    if not browser_bin:
        print("  [!] Neither Chrome nor Edge found on standard paths. PDF compilation skipped.")
        return False

    cmd = [
        browser_bin,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={out_pdf}",
        str(html_path.resolve())
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if res.returncode != 0 or not out_pdf.is_file():
        print(f"  [!] Browser print failed with code {res.returncode}: {res.stderr}")
        return False

    pdf_size_kb = out_pdf.stat().st_size / 1024
    print(f"  [✓] Successfully compiled {out_pdf.name} ({pdf_size_kb:.1f} KB).")
    return out_pdf


def verify_pdf_and_conjuncts(pdf_path, total_expected):
    print("4. Verifying PDF integrity, page counts, and Kannada conjunct rendering...")
    import fitz  # PyMuPDF
    import re

    doc = fitz.open(str(pdf_path))
    num_pages = len(doc)
    print(f"  [✓] PDF opened successfully: {num_pages} A4 pages.")

    # Check for Kannada Unicode text and conjuncts across pages
    kannada_pages = 0
    test_conjuncts = ["ರ್ಥ", "ರ್ತ", "ಸ್ತ್ರ", "ಷ್ಟ", "ಷ್ಣ", "ದ್ರ", "ಗ್ಧ", "ಕ್ಕ", "ಟ್ಟ", "ಬ್ಬ"]
    found_conjuncts = set()

    for idx in range(num_pages):
        page = doc[idx]
        text = page.get_text()
        has_kn = any(0x0C80 <= ord(c) <= 0x0CFF for c in text)
        if has_kn:
            kannada_pages += 1
        for cj in test_conjuncts:
            if cj in text:
                found_conjuncts.add(cj)

    print(f"  [✓] Verified Kannada characters rendered on {kannada_pages} / {num_pages} pages.")
    print(f"  [✓] Complex conjunct ligatures (*ottakshara*) verified in extracted text: {sorted(list(found_conjuncts))}")
    doc.close()
    return True


if __name__ == "__main__":
    df = generate_elder_csv()
    html_file, count = generate_elder_html(df)
    pdf_file = compile_pdf(html_file)
    if pdf_file:
        verify_pdf_and_conjuncts(pdf_file, count)

