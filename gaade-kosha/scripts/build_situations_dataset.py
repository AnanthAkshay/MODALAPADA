# -*- coding: utf-8 -*-
"""
Generator for Situations Dataset (Gaade Kosha - Problem 2, Modalapada 2.0)
Constructs:
- data/situations.csv (Exactly 2 situations per canonical gaade = 452 rows)
- data/eval/heldout_situations.csv (1 new held-out situation per 40 selected canonical gaades)
- Validates token overlap < 60%
"""

import os
import csv
import json
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EVAL_DIR = os.path.join(DATA_DIR, 'eval')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# 1. Load canonical gaades
gaades_csv_path = os.path.join(DATA_DIR, 'gaades.csv')
with open(gaades_csv_path, 'r', encoding='utf-8') as f:
    canonical_gaades = list(csv.DictReader(f))

canonical_ids = [g['gaade_id'] for g in canonical_gaades]
print(f"Loaded {len(canonical_ids)} canonical gaades from {gaades_csv_path}.")

# 2. Load the 5 JSON parts from scratch
scratch_dir = r"C:\Users\Akshay A\.gemini\antigravity\brain\907d013c-976a-4c36-8640-d7445daaa060\scratch"
part_files = ['data_part1.json', 'data_part2.json', 'data_part3.json', 'data_part4.json', 'data_part5.json']

situations_dict = {}
for pfn in part_files:
    full_p = os.path.join(scratch_dir, pfn)
    with open(full_p, 'r', encoding='utf-8') as f:
        d = json.load(f)
        situations_dict.update(d)

print(f"Loaded {len(situations_dict)} gaades from part files.")
assert set(canonical_ids) == set(situations_dict.keys()), "Mismatch between canonical gaades and situations JSONs!"

# 3. Build data/situations.csv
situations_rows = []
for gid in canonical_ids:
    item = situations_dict[gid]
    # Sxxx_1 and Sxxx_2
    num_part = gid[1:]  # e.g. '001'
    sid_1 = f"S{num_part}_1"
    sid_2 = f"S{num_part}_2"
    
    situations_rows.append({
        'situation_id': sid_1,
        'gaade_id': gid,
        'situation_text': item['sit_a'],
        'situation_kn': item['sit_a_kn'],
        'language': 'en',
        'situation_source': 'team_drafted'
    })
    situations_rows.append({
        'situation_id': sid_2,
        'gaade_id': gid,
        'situation_text': item['sit_b'],
        'situation_kn': item['sit_b_kn'],
        'language': 'en',
        'situation_source': 'team_drafted'
    })

situations_csv_path = os.path.join(DATA_DIR, 'situations.csv')
fieldnames = ['situation_id', 'gaade_id', 'situation_text', 'situation_kn', 'language', 'situation_source']

with open(situations_csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(situations_rows)

print(f"Successfully wrote {len(situations_rows)} rows to {situations_csv_path}.")

# 4. Heldout test set for 40 selected canonical gaades
heldout_data = {
    "G002": {
        "text": "After sweating for months in high humidity pollinating vanilla orchid vines by hand, the young agriculturalist secured lucrative harvest contracts from organic bakeries.",
        "kn": "ಕೈಯಾರೆ ವೆನಿಲ್ಲಾ ಬಳ್ಳಿಗಳನ್ನು ಶ್ರಮಪಟ್ಟು ಪರಾಗಸ್ಪರ್ಶ ಮಾಡಿದ ಕೃಷಿಕ, ಕೊನೆಗೆ ಸಮೃದ್ಧ ಇಳುವರಿ ಪಡೆದು ಬೇಕರಿಗಳಿಂದ ಹೆಚ್ಚಿನ ಬೆಲೆ ಗಳಿಸಿದನು."
    },
    "G007": {
        "text": "Instead of buying three commercial delivery trucks on bank loans, the startup courier rented one second-hand tempo until daily order volumes became steady.",
        "kn": "ಬ್ಯಾಂಕ್ ಸಾಲದಲ್ಲಿ ಹೊಸ ಲಾರಿಗಳನ್ನು ಖರೀದಿಸುವ ಬದಲು, ಕೊರಿಯರ್ ಸಂಸ್ಥೆಯು ವ್ಯಾಪಾರ ಸ್ಥಿರವಾಗುವವರೆಗೂ ಕೇವಲ ಒಂದು ಹಳೆಯ ಟೆಂಪೋ ಬಾಡಿಗೆಗೆ ಪಡೆದು ಮಿತವಾಗಿ ವ್ಯವಹಾರ ನಡೆಸಿತು."
    },
    "G008": {
        "text": "Hurrying to leave for the weekend bus, the research fellow poured reagent too rapidly into the beaker, causing a volatile chemical boil-over that ruined weeks of samples.",
        "kn": "ವಾರಾಂತ್ಯದ ಊರಿಗೆ ಹೊರಡುವ ಆತುರದಲ್ಲಿ ರಾಸಾಯನಿಕ ದ್ರಾವಣವನ್ನು ವೇಗವಾಗಿ ಸುರಿದ ಸಂಶೋಧಕ, ಕುದಿತದಿಂದ ದ್ರಾವಣ ಚೆಲ್ಲಿ ವಾರಗಳ ಶ್ರಮವನ್ನು ಹಾಳುಮಾಡಿದನು."
    },
    "G009": {
        "text": "By planting heirloom shade-tolerant coffee bushes and nurturing the soil with leaf mulch, the planter produced award-winning specialty beans ten years later.",
        "kn": "ಆರಂಭದಲ್ಲೇ ಉತ್ತಮ ತಳಿಯ ಕಾಫಿ ಗಿಡಗಳನ್ನು ನೆಟ್ಟು ಎಲೆಗೊಬ್ಬರದಿಂದ ಪೋಷಿಸಿದ ಬೆಳೆಗಾರ, ಹತ್ತು ವರ್ಷಗಳ ನಂತರ ಅತ್ಯುತ್ತಮ ಗುಣಮಟ್ಟದ ಕಾಫಿ ಬೆಳೆದು ಅಂತಾರಾಷ್ಟ್ರೀಯ ಪ್ರಶಸ್ತಿ ಪಡೆದನು."
    },
    "G023": {
        "text": "The hospital clinic only considered purchasing cloud backup subscriptions after ransomware encrypted all patient medical records overnight.",
        "kn": "ಹ್ಯಾಕರ್‌ಗಳು ರೋಗಿಗಳ ಎಲ್ಲಾ ಕಂಪ್ಯೂಟರ್ ದಾಖಲೆಗಳನ್ನು ಲಾಕ್ ಮಾಡಿದ ನಂತರ ಆಸ್ಪತ್ರೆಯು ಬ್ಯಾಕ್‌ಅಪ್ ತಂತ್ರಾಂಶ ಖರೀದಿಸಲು ಮುಂದಾಗಿದ್ದು ವ್ಯರ್ಥವಾಯಿತು."
    },
    "G024": {
        "text": "The breakdown towing crane arrived four hours after passing motorists had already cleared the jackknifed truck and restored highway traffic.",
        "kn": "ಹಾದಿಹೋಕರೇ ರಸ್ತೆಗೆ ಅಡ್ಡಲಾಗಿದ್ದ ಲಾರಿಯನ್ನು ಪಕ್ಕಕ್ಕೆ ಸರಿಸಿ ಸಂಚಾರ ಸುಗಮಗೊಳಿಸಿದ ನಾಲ್ಕು ಗಂಟೆಗಳ ನಂತರ ಕ್ರೇನ್ ವಾಹನ ಸ್ಥಳಕ್ಕೆ ಬಂದಿತು."
    },
    "G027": {
        "text": "When the headline singer fell hoarse at the last minute, the young accompanist took the microphone boldly and delivered a performance that launched his career.",
        "kn": "ಪ್ರಧಾನ ಗಾಯಕನಿಗೆ ಗಂಟಲು ಸರಿ ಇಲ್ಲದಿದ್ದಾಗ ಸಿಕ್ಕ ಅವಕಾಶವನ್ನು ಸದುಪಯೋಗಪಡಿಸಿಕೊಂಡ ಯುವ ಶಿಷ್ಯ, ಅದ್ಭುತವಾಗಿ ಹಾಡಿ ಪ್ರಸಿದ್ಧಿ ಗಳಿಸಿದನು."
    },
    "G029": {
        "text": "While amateur enthusiasts bickered noisily about space theories, the Nobel laureate quietly answered complex mathematical inquiries with polite brevity.",
        "kn": "ವೇದಿಕೆಯಲ್ಲಿ ಹೊಸಬರು ಬೊಬ್ಬಿಡುತ್ತಿದ್ದಾಗ, ನೊಬೆಲ್ ಪ್ರಶಸ್ತಿ ವಿಜೇತ ಹಿರಿಯ ವಿಜ್ಞಾನಿ ಮೌನವಾಗಿ ಕೇಳಿಸಿಕೊಂಡು ಸೌಮ್ಯವಾಗಿ ಸಂಕ್ಷಿಪ್ತ ಉತ್ತರ ನೀಡಿದರು."
    },
    "G036": {
        "text": "Seeking to maximize catch profits, the trawler skipper overloaded his vessel with sixty extra crates of mackerel, causing the boat to capsize in harbor swells.",
        "kn": "ಹೆಚ್ಚಿನ ಲಾಭದ ದುರಾಸೆಯಿಂದ ದೋಣಿಯ ಮಿತಿ ಮೀರಿ ಮೀನಿನ ಬಾಕ್ಸ್‌ಗಳನ್ನು ತುಂಬಿದ ನಾವಿಕ, ಬಂದರಿನ ಅಲೆಗಳಿಗೆ ದೋಣಿ ಮಗುಚಿ ಎಲ್ಲಾ ಸರಕುಗಳನ್ನು ಕಳೆದುಕೊಂಡನು."
    },
    "G041": {
        "text": "The surgeon ignored incoming phone buzzes and focused entirely on suturing the arterial valve before attending to any other hospital ward updates.",
        "kn": "ಶಸ್ತ್ರಚಿಕಿತ್ಸೆಯ ವೇಳೆ ಮೊಬೈಲ್ ಕರೆಗಳನ್ನು ಲೆಕ್ಕಿಸದ ವೈದ್ಯರು, ರಕ್ತನಾಳದ ಹೊಲಿಗೆಯನ್ನು ಪೂರ್ಣಗೊಳಿಸುವುದರ ಕಡೆಗಷ್ಟೇ ಸಂಪೂರ್ಣ ಗಮನಹರಿಸಿದರು."
    },
    "G051": {
        "text": "When their car tire burst on a deserted forest road, an unknown auto-rickshaw driver stopped, shared his spare wheel, and guided them to the nearest town.",
        "kn": "ನಿರ್ಜನ ಕಾಡಿನಲ್ಲಿ ಕಾರಿನ ಟೈರ್ ಪಂಕ್ಚರ್ ಆದಾಗ, ಅಪರಿಚಿತ ಆಟೋ ಚಾಲಕನೊಬ್ಬ ನಿಂತು ತನ್ನ ಸ್ಪೇರ್ ಚಕ್ರ ನೀಡಿ ಹತ್ತಿರದ ಊರಿಗೆ ದಾರಿ ತೋರಿಸಿ ನೆರವಾದನು."
    },
    "G056": {
        "text": "During his prime athletic years, Anand had no sponsorship to train abroad, and when generous funding arrived at age forty-two, his knees could no longer sprint.",
        "kn": "ಪ್ರಾಯದಲ್ಲಿದ್ದಾಗ ಆನಂದ್‌ಗೆ ವಿದೇಶಿ ತರಬೇತಿಗೆ ಹಣವಿರಲಿಲ್ಲ, ಆದರೆ ನಲವತ್ತೆರಡರ ಹರೆಯದಲ್ಲಿ ದೊಡ್ಡ ಪ್ರಾಯೋಜಕತ್ವ ಬಂದಾಗ ಓಡಲು ಮೊಣಕಾಲು ಸಾಥ್ ನೀಡಲಿಲ್ಲ."
    },
    "G057": {
        "text": "In the crowded junction waiting hall, a student stressed over exam admit cards, a farmer worried about drought, and an executive feared pending layoffs.",
        "kn": "ರೈಲ್ವೆ ನಿಲ್ದಾಣದ ವಿಶ್ರಾಂತಿ ಕೊಠಡಿಯಲ್ಲಿ ವಿದ್ಯಾರ್ಥಿ ಪರೀಕ್ಷೆಯ ಬಗ್ಗೆ ಕೊರಗುತ್ತಿದ್ದರೆ, ರೈತ ಮಳೆಯ ಬಗ್ಗೆ ಮತ್ತು ಅಧಿಕಾರಿ ಉದ್ಯೋಗ ಕಡಿತದ ಚಿಂತೆಯಲ್ಲಿ ಮುಳುಗಿದ್ದರು."
    },
    "G058": {
        "text": "The smuggler who had laid illegal electric fences for wild boars accidentally tripped on his own wire in the dark, suffering severe shocks.",
        "kn": "ಕಾಡುಪ್ರಾಣಿಗಳಿಗೆ ಅಕ್ರಮ ವಿದ್ಯುತ್ ಬೇಲಿ ಹಾಕಿದ ಬೇಟೆಗಾರ, ಕತ್ತಲಿನಲ್ಲಿ ತಾನೇ ಆ ತಂತಿಗೆ ಸಿಲುಕಿ ಆಸ್ಪತ್ರೆ ಸೇರುವಂತಾಯಿತು."
    },
    "G060": {
        "text": "Even after paying hefty fines and attending mandatory traffic counseling, Kiran was caught speeding recklessly through pedestrian crossings the very next week.",
        "kn": "ಸಂಚಾರ ನಿಯಮ ಉಲ್ಲಂಘನೆಗೆ ದಂಡ ಕಟ್ಟಿ ತರಬೇತಿಗೆ ಹಾಜರಾದರೂ, ಕಿರಣ್ ಮುಂದಿನ ವಾರವೇ ಮತ್ತೆ ಪಾದಚಾರಿ ಮಾರ್ಗದಲ್ಲಿ ಅತಿವೇಗವಾಗಿ ವಾಹನ ಚಲಾಯಿಸಿ ಸಿಕ್ಕಿಬಿದ್ದನು."
    },
    "G063": {
        "text": "While the elder son took up intricate handloom silk weaving with deep patience, his younger brother preferred repairing high-speed diesel engines.",
        "kn": "ನೇಕಾರ ಕುಟುಂಬದಲ್ಲಿ ಹಿರಿಯ ಮಗ ಶ್ರದ್ಧೆಯಿಂದ ರೇಷ್ಮೆ ಸೀರೆ ನೇಯ್ದರೆ, ಕಿರಿಯ ಮಗನಿಗೆ ಡೀಸೆಲ್ ಇಂಜಿನ್ ರಿಪೇರಿ ಮಾಡುವುದರಲ್ಲೇ ಆಸಕ್ತಿಯಿತ್ತು."
    },
    "G071": {
        "text": "Living far away in a corporate hostel, Santosh missed nothing more than his mother sitting beside him and feeding him warm rice during fever.",
        "kn": "ದೂರದ ನಗರದ ಹಾಸ್ಟೆಲ್‌ನಲ್ಲಿ ಜ್ವರದಿಂದ ಬಳಲುತ್ತಿದ್ದ ಸಂತೋಷ್‌ಗೆ, ಪ್ರೀತಿಯಿಂದ ಪಕ್ಕದಲ್ಲೇ ಕುಳಿತು ತುತ್ತು ಅನ್ನ ಉಣಿಸುತ್ತಿದ್ದ ತಾಯಿಯ ಮಮತೆ ನೆನಪಾಗಿ ಕಣ್ಣೀರು ಬಂತು."
    },
    "G072": {
        "text": "Before investing his lifetime savings into a bakery franchise, Girish inspected five existing outlets and spoke with current operators about genuine monthly costs.",
        "kn": "ಬೇಕರಿ ಫ್ರಾಂಚೈಸಿ ತೆಗೆದುಕೊಳ್ಳುವ ಮುನ್ನ ಗಿರೀಶ್ ಇತರ ಐದು ಮಳಿಗೆಗಳಿಗೆ ಭೇಟಿ ನೀಡಿ ಮಾಲೀಕರೊಂದಿಗೆ ಮಾತನಾಡಿ ವಾಸ್ತವ ಖರ್ಚು-ವೆಚ್ಚಗಳನ್ನು ಕೂಲಂಕಷವಾಗಿ ಪರಿಶೀಲಿಸಿದನು."
    },
    "G089": {
        "text": "Smallholder wheat farmers shared a single combined harvester across twenty contiguous plots, saving fuel and finishing before unseasonal hail struck.",
        "kn": "ಸಣ್ಣ ರೈತರೆಲ್ಲರೂ ಒಗ್ಗೂಡಿ ಒಂದೇ ಕಟಾವು ಯಂತ್ರವನ್ನು ಬಳಸಿಕೊಂಡು, ವೆಚ್ಚ ಕಡಿಮೆ ಮಾಡಿ ಮಳೆ ಬರುವ ಮುನ್ನವೇ ಗೋಧಿ ಫಸಲನ್ನು ಮನೆ ಸೇರಿಸಿದರು."
    },
    "G109": {
        "text": "An argumentative resident kept debating trivial water meter font sizes for three hours, causing neighbors to walk out of the meeting without passing maintenance budgets.",
        "kn": "ಅಪಾರ್ಟ್‌ಮೆಂಟ್ ಸಭೆಯಲ್ಲಿ ನಿವಾಸಿ ಒಬ್ಬ ಸಣ್ಣಪುಟ್ಟ ವಿಷಯಗಳಿಗೆ ತಾಸುಗಟ್ಟಲೆ ವಾದಿಸಿ ಗದ್ದಲವೆಬ್ಬಿಸಿದ್ದರಿಂದ, ಯಾವುದೇ ಮುಖ್ಯ ನಿರ್ಧಾರ ಕೈಗೊಳ್ಳಲಾಗದೆ ಸಭೆ ರದ್ದಾಯಿತು."
    },
    "G110": {
        "text": "In a fit of frustration, the departing supervisor hurled insults at his former management, permanently losing his professional recommendation letter.",
        "kn": "ಕೆಲಸ ಬಿಡುವಾಗ ಕೋಪದಲ್ಲಿ ಆಡಳಿತ ಮಂಡಳಿಯನ್ನು ನಿಂದಿಸಿದ ಉಸ್ತುವಾರಿಯು, ತನ್ನ ಅನುಭವದ ಪ್ರಮಾಣಪತ್ರ ಮತ್ತು ಶಿಫಾರಸು ಪತ್ರವನ್ನು ಕಳೆದುಕೊಂಡನು."
    },
    "G116": {
        "text": "A technician casually discussed satellite antenna testing frequencies at a noisy tea stall, triggering an immediate security audit and suspension.",
        "kn": "ಚಹಾ ಅಂಗಡಿಯಲ್ಲಿ ಉಪಗ್ರಹ ಯೋಜನೆಯ ಸೂಕ್ಷ್ಮ ರಹಸ್ಯಗಳನ್ನು ಅಜಾಗರೂಕತೆಯಿಂದ ಮಾತನಾಡಿದ ತಂತ್ರಜ್ಞ, ತನಿಖೆಗೆ ಒಳಗಾಗಿ ಅಮಾನತುಗೊಂಡನು."
    },
    "G134": {
        "text": "The ranger station left the emergency drone control unit with an untrained novice, who promptly crashed the expensive machine into a cliffside.",
        "kn": "ಅರಣ್ಯ ಇಲಾಖೆಯ ದುಬಾರಿ ತುರ್ತು ಡ್ರೋನ್ ನಿಯಂತ್ರಣವನ್ನು ಅನನುಭವಿ ಹುಡುಗನಿಗೆ ನೀಡಿದ್ದರಿಂದ, ಆತ ಅದನ್ನು ಕಡಿದಾದ ಬಂಡೆಗೆ ಡಿಕ್ಕಿ ಹೊಡೆಸಿ ಪುಡಿಮಾಡಿದನು."
    },
    "G145": {
        "text": "Despite smear campaigns launched by dishonest executives, the junior auditor's ledger filings were verified by statutory regulators, vindicating her findings.",
        "kn": "ಭ್ರಷ್ಟ ಅಧಿಕಾರಿಗಳು ಎಷ್ಟೇ ಅಪಪ್ರಚಾರ ಮಾಡಿದರೂ, ಪ್ರಾಮಾಣಿಕ ಆಡಿಟರ್ ದಾಖಲಿಸಿದ ಲೆಕ್ಕಗಳು ಸರ್ಕಾರಿ ತನಿಖೆಯಲ್ಲಿ ನಿಜವೆಂದು ಸಾಬೀತಾಗಿ ನ್ಯಾಯ ದೊರೆಯಿತು."
    },
    "G149": {
        "text": "After turning a brass gear axle three millimeters too short, the machinist recalibrated his lathe and recut a replacement matching exact specifications.",
        "kn": "ಇಂಜಿನಿಯರಿಂಗ್ ಬಿಡಿಭಾಗದಲ್ಲಿ ಅಳತೆ ತಪ್ಪಿದಾಗ, ಕುಶಲಕರ್ಮಿ ತಕ್ಷಣವೇ ಲೇತ್ ಯಂತ್ರವನ್ನು ಮರುಹೊಂದಿಸಿ ಸರಿಯಾದ ಅಳತೆಯಲ್ಲಿ ಹೊಸ ಭಾಗವನ್ನು ತಯಾರಿಸಿದನು."
    },
    "G156": {
        "text": "The school trust had no funds to repair leaky roof tiles in classrooms, yet spent hundreds of thousands of rupees erecting an ornate welcome gateway.",
        "kn": "ಶಾಲೆಯ ಕೊಠಡಿಗಳ ಸೋರುವ ಛಾವಣಿ ರಿಪೇರಿ ಮಾಡಲು ಹಣವಿಲ್ಲದ ಆಡಳಿತ ಮಂಡಳಿ, ಲಕ್ಷಾಂತರ ರೂಪಾಯಿ ಖರ್ಚು ಮಾಡಿ ಭವ್ಯ ಸ್ವಾಗತ ಕಮಾನು ಕಟ್ಟಿಸಿತು."
    },
    "G157": {
        "text": "A university student demanded equal co-author credit on the term paper, despite refusing to attend literature searches or write a single paragraph.",
        "kn": "ಪ್ರಾಜೆಕ್ಟ್‌ನಲ್ಲಿ ಒಂದು ಸಾಲೂ ಬರೆಯದೆ ಅಥವಾ ಸಂಶೋಧನೆಗೆ ಕೈಜೋಡಿಸದೆ, ಸಂಶೋಧನಾ ಪ್ರಬಂಧದಲ್ಲಿ ತನ್ನ ಹೆಸರೂ ಮೊದಲಿಗೆ ಇರಬೇಕೆಂದು ವಿದ್ಯಾರ್ಥಿ ಹಠ ಹಿಡಿದನು."
    },
    "G160": {
        "text": "A reputable chemist was caught re-labeling expired pediatric syrups for quick cash; though he closed the shop, villagers refused to buy even toothpaste from him.",
        "kn": "ಅವಧಿ ಮೀರಿದ ಮಕ್ಕಳ ಔಷಧಕ್ಕೆ ಹೊಸ ಲೇಬಲ್ ಅಂಟಿಸಿ ಸಿಕ್ಕಿಬಿದ್ದ ಮೆಡಿಕಲ್ ಅಂಗಡಿಯವನು, ಊರಿನ ಜನರ ವಿಶ್ವಾಸ ಮತ್ತು ಗೌರವವನ್ನು ಶಾಶ್ವತವಾಗಿ ಕಳೆದುಕೊಂಡನು."
    },
    "G175": {
        "text": "Out of pity, the homeowner waived deposit and lowered rent for an acquaintance, who later forged property papers and claimed tenancy rights.",
        "kn": "ಕರುಣೆಯಿಂದ ಉಚಿತವಾಗಿ ಆಶ್ರಯ ನೀಡಿದ ಮನೆ ಮಾಲೀಕನ ವಿರುದ್ಧವೇ ನಕಲಿ ದಾಖಲೆ ಸೃಷ್ಟಿಸಿ ಜಾಗ ಕಬಳಿಸಲು ಯತ್ನಿಸಿದ ಬಾಡಿಗೆದಾರ ಕೃತಘ್ನತೆ ಮೆರೆದನು."
    },
    "G185": {
        "text": "When the legendary tactical manager adopted high-pressing wing backs, every youth academy and league club redesigned their defensive line to match.",
        "kn": "ದಿಗ್ಗಜ ಕೋಚ್ ಹೊಸ ಮಾದರಿಯ ರಕ್ಷಣಾ ತಂತ್ರವನ್ನು ಅಳವಡಿಸಿಕೊಂಡ ತಕ್ಷಣ, ದೇಶದ ಎಲ್ಲಾ ಫುಟ್‌ಬಾಲ್ ಕ್ಲಬ್‌ಗಳು ಅದೇ ತಂತ್ರವನ್ನು ಅನುಸರಿಸಿದವು."
    },
    "G194": {
        "text": "Following the aviation regulator's safety grounding decree, all sixty commercial flights of that aircraft model remained parked on tarmac nationwide.",
        "kn": "ಸುರಕ್ಷತೆಯ ದೃಷ್ಟಿಯಿಂದ ನಾಗರಿಕ ವಿಮಾನಯಾನ ಪ್ರಾಧಿಕಾರ ಹೊರಡಿಸಿದ ಆದೇಶಕ್ಕೆ ತಲೆಬಾಗಿ, ದೇಶಾದ್ಯಂತ ಎಲ್ಲಾ ವಿಮಾನಗಳ ಹಾರಾಟವನ್ನು ತಕ್ಷಣವೇ ಸ್ಥಗಿತಗೊಳಿಸಲಾಯಿತು."
    },
    "G205": {
        "text": "An octogenarian scholar who authored twenty definitive dictionaries bowed respectfully to young village students asking basic grammatical queries.",
        "kn": "ಇಪ್ಪತ್ತು ಮಹಾನ್ ನಿಘಂಟುಗಳನ್ನು ರಚಿಸಿದ ಹಿರಿಯ ವಿದ್ವಾಂಸರು, ಸಂಶಯ ಕೇಳಲು ಬಂದ ಪುಟ್ಟ ವಿದ್ಯಾರ್ಥಿಗಳ ಮುಂದೆಯೂ ಅತ್ಯಂತ ವಿನಯದಿಂದ ನಮ್ರವಾಗಿ ಉತ್ತರಿಸಿದರು."
    },
    "G206": {
        "text": "Tilling compost into the saline beach sand and digging deep mulched trenches enabled Narayana to harvest bumper bunches of sweet coconuts.",
        "kn": "ಮರಳು ಮಿಶ್ರಿತ ಭೂಮಿಯನ್ನೂ ಆಳವಾಗಿ ಹಸನು ಮಾಡಿ ಸಾವಯವ ಗೊಬ್ಬರ ನೀಡಿದ ನಾರಾಯಣ, ಸಮೃದ್ಧ ಎಳನೀರು ಬೆಳೆದು ಉತ್ತಮ ಆದಾಯ ಕಂಡನು."
    },
    "G210": {
        "text": "Neighboring farmers laughed when Ahmed leased a dry mountain slope, but were astonished when purple saffron blossoms blanketed the hillside at harvest.",
        "kn": "ಬೆಟ್ಟದ ಒಣ ಜಮೀನನ್ನು ಗುತ್ತಿಗೆ ಪಡೆದಾಗ ಗೇಲಿ ಮಾಡಿದ ಜನರಿಗೆ, ಅಹ್ಮದ್ ಅಲ್ಲಿ ಅಪರೂಪದ ಕೇಸರಿ ಬೆಳೆದು ಆ ಭೂಮಿಯ ಅಸಲಿ ಮೌಲ್ಯವನ್ನು ಸಾಬೀತುಪಡಿಸಿದನು."
    },
    "G215": {
        "text": "When the checkdam behind the village filled during the monsoon, women no longer walked four kilometers for potable well water and farms remained green.",
        "kn": "ಚೆಕ್‌ಡ್ಯಾಂ ತುಂಬಿ ಹರಿದ ಪರಿಣಾಮ, ಹಳ್ಳಿಯ ಮಹಿಳೆಯರಿಗೆ ನೀರಿಗಾಗಿ ದೂರ ಅಲೆಯುವ ಕಷ್ಟ ತಪ್ಪಿತು ಮತ್ತು ಊರ ಜನಜೀವನ ಹಸನಾಯಿತು."
    },
    "G216": {
        "text": "With high pay and foreign postings, the senior commander could not board the aircraft cockpit due to unaddressed hypertension and vertigo.",
        "kn": "ಲಕ್ಷಾಂತರ ರೂಪಾಯಿ ಸಂಬಳವಿದ್ದರೂ ತೀವ್ರ ರಕ್ತದೊತ್ತಡ ಮತ್ತು ತಲೆಸುತ್ತಿನ ಕಾರಣದಿಂದ ಹಿರಿಯ ಪೈಲಟ್‌ಗೆ ವಿಮಾನ ಹಾರಿಸಲು ಸಾಧ್ಯವಾಗದೆ ಮನೆಯಲ್ಲೇ ಉಳಿಯಬೇಕಾಯಿತು."
    },
    "G237": {
        "text": "Paralyzed by the thought of deep open water, Vinod abandoned the underwater welding exam, forfeiting high-paying harbor pipeline contracts.",
        "kn": "ಆಳವಾದ ಸಮುದ್ರದ ನೀರಿಗೆ ಹೆದರಿ ಮುಳುಗು ತರಬೇತಿಯ ಪರೀಕ್ಷೆ ಬಿಟ್ಟು ಓಡಿದ ವಿನೋದ್, ಉತ್ತಮ ಆದಾಯದ ಉದ್ಯೋಗಾವಕಾಶವನ್ನು ಕಳೆದುಕೊಂಡನು."
    },
    "G240": {
        "text": "Even after mulberry leaves dried and two cocoon batches were lost to heat, the sericulturist insulated her sheds with straw and raised a prize-winning batch.",
        "kn": "ಬಿಸಿಲಿಗೆ ರೇಷ್ಮೆ ಬೆಳೆ ನಾಶವಾದರೂ ಧೃತಿಗೆಡದ ರೈತ ಮಹಿಳೆ, ಹುಲ್ಲಿನ ಮಾಡು ನಿರ್ಮಿಸಿ ತಂಪಾದ ವಾತಾವರಣ ಸೃಷ್ಟಿಸಿ ಉತ್ತಮ ರೇಷ್ಮೆ ಗೂಡು ಬೆಳೆದಳು."
    },
    "G249": {
        "text": "By keeping immaculate daily spray logs and adhering to national bio-standards, the spice exporter cleared international customs without a single seizure.",
        "kn": "ಸರ್ಕಾರದ ಎಲ್ಲಾ ಸಾವಯವ ನಿಯಮಗಳನ್ನು ಕಟ್ಟುನಿಟ್ಟಾಗಿ ಪಾಲಿಸಿದ ಸಾಂಬಾರ ಪದಾರ್ಥಗಳ ರಫ್ತುದಾರ, ಬಂದರಿನ ತಪಾಸಣೆಯಲ್ಲಿ ಯಾವುದೇ ಕಿರಿಕಿರಿಯಿಲ್ಲದೆ ವ್ಯಾಪಾರ ಮುಂದುವರಿಸಿದನು."
    },
    "G250": {
        "text": "The irrigation guard greased the mechanical hoist gears on Monday as scheduled, allowing gates to open smoothly when flood surges arrived that evening.",
        "kn": "ಅಣೆಕಟ್ಟಿನ ಗೇಟುಗಳನ್ನು ನಿಗದಿತ ವೇಳಾಪಟ್ಟಿಯಂತೆ ಅಂದೇ ಸರಿಪಡಿಸಿಟ್ಟಿದ್ದ ಕಾವಲುಗಾರನ ಕಾರ್ಯಪ್ರಜ್ಞೆಯಿಂದಾಗಿ, ರಾತ್ರಿ ದಿಢೀರ್ ಪ್ರವಾಹ ಬಂದಾಗ ಸುಲಭವಾಗಿ ನೀರು ಹೊರಬಿಡಲಾಯಿತು."
    }
}

heldout_rows = []
for idx, (gid, item) in enumerate(heldout_data.items(), 1):
    eval_id = f"E{idx:03d}"
    heldout_rows.append({
        'eval_id': eval_id,
        'gaade_id': gid,
        'situation_text': item['text'],
        'situation_kn': item['kn'],
        'language': 'en',
        'split': 'heldout_test'
    })

heldout_csv_path = os.path.join(EVAL_DIR, 'heldout_situations.csv')
heldout_fieldnames = ['eval_id', 'gaade_id', 'situation_text', 'situation_kn', 'language', 'split']

with open(heldout_csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=heldout_fieldnames)
    writer.writeheader()
    writer.writerows(heldout_rows)

print(f"Successfully wrote {len(heldout_rows)} heldout rows to {heldout_csv_path}.")

# 5. Overlap verification
def tokenize(text):
    return set(re.findall(r'\b\w+\b', text.lower()))

token_sets = [(r['situation_id'], tokenize(r['situation_text'])) for r in situations_rows]
max_jaccard = 0.0
worst_pair = None

for i in range(len(token_sets)):
    for j in range(i + 1, len(token_sets)):
        s1_id, t1 = token_sets[i]
        s2_id, t2 = token_sets[j]
        inter = len(t1 & t2)
        union = len(t1 | t2)
        if union == 0: continue
        jaccard = inter / union
        if jaccard > max_jaccard:
            max_jaccard = jaccard
            worst_pair = (s1_id, s2_id, jaccard)

print(f"Pairwise token overlap verification: Max Jaccard = {max_jaccard:.4f} between {worst_pair[0]} and {worst_pair[1]}.")
assert max_jaccard < 0.60, f"Token overlap exceeded 60%! {max_jaccard}"
print("All diversity and token overlap constraints verified successfully!")
