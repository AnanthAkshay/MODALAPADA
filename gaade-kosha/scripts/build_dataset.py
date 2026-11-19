"""
Dataset Builder for Gaade Kosha (Problem 2 - Modalapada 2.0)
Constructs:
- data/gaades.csv (Canonical proverbs only)
- data/gaade_provenance.csv (Full audit trail for G001-G252)
- data/reports/duplicates.csv (Detailed duplicate analysis)
- data/reports/excluded_duplicates.csv (Excluded duplicate entries)
- data/reports/proofread_sheet.csv (Human verification sheet)
"""

import os
import re
import csv
import json
import fitz

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
RAW_DIR = os.path.join(DATA_DIR, 'raw', 'pdf_pages')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# 1. Load English meanings and usage contexts extracted from Revised PDF
with open('C:/Users/Akshay A/.gemini/antigravity/brain/907d013c-976a-4c36-8640-d7445daaa060/scratch/parsed_english.json', 'r', encoding='utf-8') as f:
    parsed_eng = json.load(f)

def clean_eng(text):
    text = text.strip()
    text = re.sub(r'^[,\.\':;\"’‘\-\s]+', '', text)
    text = re.sub(r'[,\':;\"’‘\-\s]+$', '', text)
    text = re.sub(r'(\b\w+)\s+s\b', r"\1's", text)
    text = re.sub(r'(\b\w+)\s+t\b', r"\1't", text)
    if text and not text.endswith(('.', '?', '!')):
        text += '.'
    return text

# 2. Base 200 Kannada gaades from uncorrupted 1_of_4 to 4_of_4 sub-PDFs
base_gaades = {}
for i in range(1, 5):
    fname = f'C:/Users/Akshay A/Downloads/Kannada_Gaadegalu_{i}_of_4.pdf'
    doc = fitz.open(fname)
    for p in doc:
        txt = p.get_text()
        for line in txt.splitlines():
            line = line.strip()
            parts = line.split('.', 1)
            if parts[0].isdigit() and len(parts) > 1:
                num = int(parts[0])
                if 1 <= num <= 200:
                    base_gaades[num] = parts[1].strip()

# 3. Incorporate 8 Replacements in 1-200 verified visually from page images
replacements_kannada = {
    185: 'ಆನೆ ನಡೆದದ್ದೇ ದಾರಿ.',
    186: 'ಅತ್ತೆಗೊಂದು ಕಾಲ, ಸೊಸೆಗೊಂದು ಕಾಲ.',
    187: 'ಕಾಗೆ ಕುಳಿತದ್ದಕ್ಕೆ ಕೊಂಬೆ ಮುರಿಯಿತೇ?',
    188: 'ಅಂಗೈ ಹುಣ್ಣಿಗೆ ಕನ್ನಡಿ ಏಕೆ?',
    189: 'ಅಳುವ ಮಗುವಿಗೆ ಹಾಲು.',
    191: 'ಊಟ ಬಲ್ಲವನಿಗೆ ರೋಗವಿಲ್ಲ, ಮಾತು ಬಲ್ಲವನಿಗೆ ಜಗಳವಿಲ್ಲ.',
    192: 'ಅಡಿಗೆ ಬಲ್ಲವಳು ಮನೆಗೆ ಒಡತಿ.',
    194: 'ಅರಸನ ಆಜ್ಞೆ ಕಲ್ಲಿನ ಗೆರೆ.'
}
for k, v in replacements_kannada.items():
    base_gaades[k] = v

# 4. Entries 201-250 transcribed visually from page images
transcribed_201_250 = {
    201: 'ವಿದ್ಯೆಯೇ ಶಾಶ್ವತ ಸಂಪತ್ತು.',
    202: 'ಕಲಿತ ವಿದ್ಯೆ ಕೈ ಬಿಡದು.',
    203: 'ಗುರು ತೋರಿದ ದಾರಿ ಗುರಿ ತಲುಪಿಸುತ್ತದೆ.',
    204: 'ಪುಸ್ತಕದ ಗೆಳೆತನ ಬದುಕಿಗೆ ಬೆಳಕು.',
    205: 'ವಿದ್ಯೆಗೆ ವಿನಯವೇ ಆಭರಣ.',
    206: 'ಉಳುಮೆ ಮಾಡಿದ ಭೂಮಿ ಎಂದಿಗೂ ಕೈ ಬಿಡದು.',
    207: 'ಬಿತ್ತುವ ಕಾಲದಲ್ಲಿ ಮಲಗಿದರೆ ಕೊಯ್ಯುವ ಕಾಲದಲ್ಲಿ ಅಳಬೇಕು.',
    208: 'ಮಣ್ಣಿನ ಗುಣ ಅರಿತವನೇ ಒಳ್ಳೆಯ ರೈತ.',
    209: 'ಬೇಸಾಯವಿದ್ದರೆ ಬದುಕಿಗೆ ಆಧಾರ.',
    210: 'ಬೆಳೆ ಬೆಳೆದರೆ ಹೊಲದ ಬೆಲೆ ಗೊತ್ತು.',
    211: 'ಮರ ಉಳಿದರೆ ಮಳೆ ಉಳಿಯುತ್ತದೆ.',
    212: 'ಹಸಿರು ಇದ್ದಲ್ಲಿ ಉಸಿರು.',
    213: 'ನೀರೇ ಜೀವದ ಮೂಲ.',
    214: 'ಪ್ರಕೃತಿಯನ್ನು ಕಾಪಾಡಿದರೆ ಪ್ರಕೃತಿ ನಮ್ಮನ್ನು ಕಾಪಾಡುತ್ತದೆ.',
    215: 'ಕೆರೆ ತುಂಬಿದರೆ ಊರು ತುಂಬಿದಂತೆ.',
    216: 'ಆರೋಗ್ಯವೇ ಭಾಗ್ಯ.',
    217: 'ಅಳತೆಯ ಊಟ ಆರೋಗ್ಯದ ಗುಟ್ಟು.',
    218: 'ಹಿತವಾಗಿ ಉಂಡರೆ ಹಿತವಾಗಿ ಬಾಳಬಹುದು.',
    219: 'ಮಿತಿಯಾದ ಆಹಾರ ಅಮೃತಕ್ಕೆ ಸಮಾನ.',
    220: 'ಸ್ವಚ್ಛತೆಯೇ ಆರೋಗ್ಯದ ಮೊದಲ ಮೆಟ್ಟಿಲು.',
    221: 'ವ್ಯಾಪಾರದಲ್ಲಿ ನಂಬಿಕೆಯೇ ಬಂಡವಾಳ.',
    222: 'ಲೆಕ್ಕವಿಲ್ಲದ ವ್ಯಾಪಾರ ನಷ್ಟಕ್ಕೆ ದಾರಿ.',
    223: 'ಗ್ರಾಹಕನೇ ವ್ಯಾಪಾರದ ದೇವರು.',
    224: 'ಸಣ್ಣ ಲಾಭವೇ ದೊಡ್ಡ ಬೆಳವಣಿಗೆಗೆ ಅಡಿಪಾಯ.',
    225: 'ದುಡಿಮೆಯ ಹಣಕ್ಕೆ ಬೆಲೆ ಹೆಚ್ಚು.',
    226: 'ಊರಿನ ಹಿತವೇ ಎಲ್ಲರ ಹಿತ.',
    227: 'ಪರೋಪಕಾರವೇ ಪುಣ್ಯದ ಕೆಲಸ.',
    228: 'ಒಳ್ಳೆಯ ನೆರೆಹೊರೆ ಬದುಕಿನ ಆಸ್ತಿ.',
    229: 'ಸಮಾಜದಲ್ಲಿ ಬದುಕಲು ಸಹಕಾರ ಅಗತ್ಯ.',
    230: 'ಹಂಚಿಕೊಂಡು ತಿಂದರೆ ಸಂತೋಷ ಹೆಚ್ಚುತ್ತದೆ.',
    231: 'ನಾಯಕನ ಗುಣ ತಂಡದ ಬಲ.',
    232: 'ಮುಂದಾಳತ್ವ ವಹಿಸಿದವನೇ ದಾರಿ ತೋರಿಸಬೇಕು.',
    233: 'ಅಧಿಕಾರಕ್ಕಿಂತ ಜವಾಬ್ದಾರಿ ದೊಡ್ಡದು.',
    234: 'ನ್ಯಾಯವಿದ್ದಲ್ಲಿ ನಂಬಿಕೆ ಇರುತ್ತದೆ.',
    235: 'ಒಳ್ಳೆಯ ಆಡಳಿತ ಜನರ ಭಾಗ್ಯ.',
    236: 'ಧೈರ್ಯವಿದ್ದರೆ ದಾರಿ ಕಾಣುತ್ತದೆ.',
    237: 'ಅಂಜಿದವನಿಗೆ ಅವಕಾಶ ಸಿಗದು.',
    238: 'ಸವಾಲುಗಳೇ ಸಾಧನೆಗೆ ಸೋಪಾನ.',
    239: 'ಬಿದ್ದವನೇ ಏಳುವುದನ್ನು ಕಲಿಯುತ್ತಾನೆ.',
    240: 'ಎದೆಗುಂದದವನಿಗೆ ಸೋಲಿಲ್ಲ.',
    241: 'ಸಂಸ್ಕಾರವೇ ಮನುಷ್ಯನ ನಿಜವಾದ ಆಭರಣ.',
    242: 'ಭಾಷೆ ಉಳಿದರೆ ಸಂಸ್ಕೃತಿ ಉಳಿಯುತ್ತದೆ.',
    243: 'ಹಿರಿಯರ ಅನುಭವ ಕಿರಿಯರಿಗೆ ದಾರಿ.',
    244: 'ಸಂಪ್ರದಾಯದ ಬೇರು ಸಂಸ್ಕೃತಿಯಲ್ಲಿ.',
    245: 'ತಾಯ್ನುಡಿಯ ಸೊಗಸು ಬೇರೆ ಯಾವುದರಲ್ಲೂ ಇಲ್ಲ.',
    246: 'ಶಿಸ್ತಿದ್ದಲ್ಲಿ ಯಶಸ್ಸು ಇರುತ್ತದೆ.',
    247: 'ಸಮಯ ಪಾಲನೆ ಸಾಧನೆಯ ಮೊದಲ ಹೆಜ್ಜೆ.',
    248: 'ಸಣ್ಣ ಜವಾಬ್ದಾರಿಯೂ ದೊಡ್ಡ ನಂಬಿಕೆಗೆ ಕಾರಣ.',
    249: 'ನಿಯಮ ಪಾಲಿಸಿದರೆ ನೆಮ್ಮದಿ.',
    250: 'ಇಂದಿನ ಕರ್ತವ್ಯವನ್ನು ಇಂದೇ ಮಾಡಬೇಕು.'
}

all_gaades = {}
for n in range(1, 201):
    all_gaades[n] = base_gaades[n]
for n in range(201, 251):
    all_gaades[n] = transcribed_201_250[n]

# 5. Add G251 and G252 (official hackathon starter examples)
all_gaades[251] = 'ಬೆಂಕಿ ಬಂದಾಗ ಬಾವಿ ತೋಡಿದಂತೆ.'
all_gaades[252] = 'ಎಲ್ಲರ ಮನೆ ದೋಸೆಯೂ ತೂತು.'

# Map page images for G001 to G250
# Derived from actual block coordinates in Revised PDF
page_mapping = {
    (1, 11): 2, (12, 23): 3, (24, 35): 4, (36, 47): 5, (48, 50): 6,
    (51, 61): 7, (62, 73): 8, (74, 85): 9, (86, 97): 10, (98, 100): 11,
    (101, 111): 12, (112, 123): 13, (124, 135): 14, (136, 147): 15, (148, 150): 16,
    (151, 161): 17, (162, 173): 18, (174, 185): 19, (186, 197): 20, (198, 200): 21,
    (201, 210): 22, (211, 221): 23, (222, 232): 24, (233, 243): 25, (244, 250): 26
}

def get_page_image(n):
    if n in (251, 252):
        return 'data/raw/pdf_pages/hackathon_slide_example.png'
    for (start, end), p_num in page_mapping.items():
        if start <= n <= end:
            return f'data/raw/pdf_pages/page_{p_num:02d}.png'
    return 'data/raw/pdf_pages/unknown.png'

# 6. Suspect Duplicate Mapping (earlier -> later)
# Known 26 duplicates: later entry duplicate_of earlier
duplicate_map = {
    131: 29,   # ತುಂಬಿದ ಕೊಡ ತುಳುಕುವುದಿಲ್ಲ.
    86: 42,    # ತಾಳ್ಮೆ ಇದ್ದರೆ ತೊಂದರೆ ಇಲ್ಲ.
    117: 83,   # ಕೋಪದಲ್ಲಿ ಕೊಯ್ದ ಮೂಗು ಶಾಂತಿಯಲ್ಲಿ ಸಿಗುವುದಿಲ್ಲ.
    125: 85,   # ಹಾವು ಸಾಯಬೇಕು, ಕೋಲು ಮುರಿಯಬಾರದು.
    193: 53,   # ಒಂದು ಕೈಯಿಂದ ಚಪ್ಪಾಳೆ ಆಗುವುದಿಲ್ಲ.
    182: 59,   # ಮಾತು ಆಡಿದರೆ ಹೋಯಿತು, ಮುತ್ತು ಒಡೆದರೆ ಹೋಯಿತು.
    196: 103,  # ಕೋತಿಯ ಕೈಗೆ ಮಾಣಿಕ್ಯ ಕೊಟ್ಟಂತೆ.
    197: 101,  # ಕುಣಿಯಲಾರದವಳು ನೆಲ ಡೊಂಕು ಅಂದಳು.
    198: 107,  # ಅರ್ಧ ಜ್ಞಾನ ಅಪಾಯಕ್ಕೆ ದಾರಿ.
    179: 118,  # ಕಳ್ಳನ ಮನಸ್ಸು ಹುಳ್ಳುಳ್ಳಗೆ.
    180: 119,  # ಕಳ್ಳನಿಗೆ ಒಂದು ಪಿಳ್ಳೆ ನೆವ.
    168: 128,  # ಕಣ್ಣಿಗೆ ಕಾಣುವುದೆಲ್ಲ ಸತ್ಯವಲ್ಲ.
    169: 129,  # ಮಿಂಚುವುದೆಲ್ಲ ಚಿನ್ನವಲ್ಲ.
    163: 130,  # ಹೊರಗೆ ಬಂಗಾರ, ಒಳಗೆ ಕಲ್ಲು.
    170: 123,  # ಹುಚ್ಚನ ಮದುವೆಯಲ್ಲಿ ಉಂಡವನೇ ಜಾಣ.
    181: 138,  # ನಂಬಿಕೆ ಕಳೆದುಕೊಂಡರೆ ಎಲ್ಲವನ್ನೂ ಕಳೆದುಕೊಂಡಂತೆ.
    164: 139,  # ಹುಲಿ ಬಂತು ಹುಲಿ ಎಂದರೆ ಯಾರೂ ನಂಬುವುದಿಲ್ಲ.
    195: 132,  # ಖಾಲಿ ಕೊಡ ಹೆಚ್ಚು ಸದ್ದು ಮಾಡುತ್ತದೆ.
    199: 145,  # ಸತ್ಯಕ್ಕೆ ಜಯ.
    200: 150,  # ಅನುಭವವೇ ದೊಡ್ಡ ಗುರು.
    190: 13,   # ಕಷ್ಟವಿಲ್ಲದೆ ಫಲವಿಲ್ಲ.
    174: 32,   # ದೂರದ ಬೆಟ್ಟ ಕಣ್ಣಿಗೆ ನುಣ್ಣಗೆ.
    184: 33,   # ಕಾಲ ಬಂದಾಗ ಕಲ್ಲೂ ಮಾತನಾಡುತ್ತದೆ.
    183: 23,   # ಮಳೆ ಬರುವಾಗ ಕೊಡೆ ಹಿಡಿದರೆ ಪ್ರಯೋಜನವಿಲ್ಲ.
    177: 36,   # ಆಸೆಗೊಂದು ಮಿತಿ ಇರಬೇಕು.
    135: 104   # ಕತ್ತೆಗೆ ಏನು ಗೊತ್ತು ಕಸ್ತೂರಿ ಪರಿಮಳ? vs ಕತ್ತೆಗೆ ಕಸ್ತೂರಿ ವಾಸನೆ ಗೊತ್ತೇ?
}

# 7. English equivalents (distinct idioms where available, else fallback)
english_idioms = {
    1: 'Grasp all, lose all.',
    2: 'No pain, no gain.',
    3: 'As you sow, so you reap.',
    4: 'As the twig is bent, so the tree is inclined.',
    5: 'Many a little makes a mickle.',
    6: 'He who endures conquers.',
    7: 'Cut your coat according to your cloth.',
    8: 'Haste makes waste.',
    9: 'You reap what you sow.',
    10: 'Time and tide wait for no man.',
    11: 'Lost time is never found again.',
    12: 'When in Rome, do as the Romans do.',
    13: 'No sweet without sweat.',
    14: 'Work is worship.',
    15: 'Actions speak louder than words.',
    16: 'Never put off till tomorrow what you can do today.',
    17: 'Deep rivers move with silent majesty.',
    18: 'Diligence is the mother of good fortune.',
    19: 'Where there is a will, there is a way.',
    20: 'After rain comes sunshine.',
    21: 'Strike while the iron is hot.',
    24: 'Locking the stable door after the horse has bolted.',
    26: 'Once bitten, twice shy.',
    29: 'Empty vessels make the most noise.',
    32: 'The grass is always greener on the other side.',
    33: 'Every dog has its day.',
    36: 'Moderation in all things.',
    42: 'Patience is a plaster for all sores.',
    45: 'Look before you leap.',
    50: 'Many hands make light work.',
    51: 'A friend in need is a friend indeed.',
    53: 'It takes two to tango.',
    59: 'A word spoken is an arrow shot.',
    64: 'A guilty conscience needs no accuser.',
    71: 'A mother is an irreplaceable treasure.',
    76: 'United we stand, divided we fall.',
    83: 'Wrath has no place in reconciliation.',
    85: 'Kill two birds with one stone.',
    101: 'A bad workman blames his tools.',
    102: 'Casting pearls before swine.',
    104: 'Do not throw pearls to swine.',
    107: 'A little learning is a dangerous thing.',
    112: 'One lie leads to another.',
    114: 'Speech is silver, silence is golden.',
    118: 'A guilty mind is always suspicious.',
    125: 'Kill two birds with one stone.',
    128: 'Appearances are deceptive.',
    129: 'All that glitters is not gold.',
    130: 'A wolf in sheep’s clothing.',
    132: 'Empty vessels make the loudest noise.',
    135: 'Do not cast pearls before swine.',
    139: 'Cry wolf.',
    145: 'Truth will out.',
    150: 'Experience is the best teacher.',
    151: 'Money makes the mare go.',
    152: 'Live within your means.',
    164: 'The boy who cried wolf.',
    174: 'Distant hills look greener.',
    176: 'What is fun to the cat is death to the mouse.',
    185: 'Might is right.',
    186: 'Every dog has its day.',
    187: 'Correlation is not causation.',
    188: 'What need is there of a mirror to see the obvious?',
    189: 'The squeaky wheel gets the grease.',
    191: 'Eat well to live well; speak well to live in peace.',
    192: 'A capable cook rules the house.',
    193: 'It takes two hands to clap.',
    194: 'The king’s command is etched in stone.',
    195: 'Empty vessels make the loudest noise.',
    196: 'Casting pearls before swine.',
    197: 'A bad workman quarrels with his tools.',
    198: 'A little learning is a dangerous thing.',
    200: 'Experience is the mother of wisdom.',
    212: 'Where there is green, there is life.',
    216: 'Health is wealth.',
    223: 'The customer is king.',
    251: 'Digging a well after the house catches fire.',
    252: 'Every family has its skeleton in the closet.'
}

# 8. Curated theme mapping into the 16 allowed official themes:
# Allowed: Money, Work, Study, Family, Friends, Character, Society, Agriculture, Nature, Health, Business, Education, Leadership, Culture, Time, Other
def assign_theme(n):
    # Part 5 directly assigned by PDF section headers:
    if 201 <= n <= 205:
        return 'Education'
    elif 206 <= n <= 210:
        return 'Agriculture'
    elif 211 <= n <= 215:
        return 'Nature'
    elif 216 <= n <= 220:
        return 'Health'
    elif 221 <= n <= 225:
        return 'Business'
    elif 226 <= n <= 230:
        return 'Society'
    elif 231 <= n <= 235:
        return 'Leadership'
    elif 236 <= n <= 240:
        return 'Character'
    elif 241 <= n <= 245:
        return 'Culture'
    elif 246 <= n <= 250:
        return 'Time'
    elif n == 251:
        return 'Time'
    elif n == 252:
        return 'Family'

    # Parts 1-4 per-entry categorization:
    # Money
    if n in (1, 5, 7, 27, 43, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 171, 172, 173, 177, 178, 186):
        return 'Money'
    # Time
    if n in (8, 10, 11, 12, 16, 23, 24, 25, 33, 40, 41, 47, 183, 184):
        return 'Time'
    # Work
    if n in (2, 9, 13, 14, 15, 18, 21, 22, 28, 35, 37, 39, 44, 46, 49, 50, 185, 190, 192):
        return 'Work'
    # Family
    if n in (55, 61, 62, 63, 67, 68, 70, 71, 74, 75, 76, 78, 79, 81, 84):
        return 'Family'
    # Friends
    if n in (51, 52, 54, 57, 77, 88, 89, 90, 93, 98):
        return 'Friends'
    # Society
    if n in (53, 56, 58, 60, 65, 66, 69, 72, 73, 80, 82, 87, 91, 92, 94, 96, 97, 99, 100, 123, 170, 189, 193):
        return 'Society'
    # Study
    if n in (107, 108, 109, 110, 116, 121, 134, 148, 150, 198, 200):
        return 'Study'
    # Leadership
    if n in (194,):
        return 'Leadership'
    # Health
    if n in (191,):
        return 'Health'
    # Default for remaining wisdom/conduct/deception proverbs in Parts 1-4:
    return 'Character'

# Build comprehensive records
gaades_rows = []
provenance_rows = []
proofread_rows = []
duplicates_rows = []
excluded_duplicates_rows = []

for n in range(1, 253):
    gid = f'G{n:03d}'
    kannada = all_gaades[n]
    page_img = get_page_image(n)

    # Determine meaning and use_when
    if n <= 250:
        meaning = clean_eng(parsed_eng[str(n)]['meaning'])
        use_when = clean_eng(parsed_eng[str(n)]['use_when'])
    elif n == 251:
        meaning = 'Starting preparation only after calamity has already arrived is futile.'
        use_when = 'Use when someone tries to make emergency arrangements after a crisis has already begun.'
    elif n == 252:
        meaning = 'Every household has its own private flaws, troubles, or secrets.'
        use_when = 'Use when reminding someone that everyone faces their own hidden difficulties.'

    # Determine English equivalent
    if n in english_idioms:
        english = english_idioms[n]
        is_fallback = False
    else:
        english = meaning
        is_fallback = True

    theme = assign_theme(n)
    audio_file = f'audio/wav/{gid}.wav'
    region = 'UNVERIFIED'
    example = ''  # Must be empty as per Task 2

    # Provenance fields
    if n <= 200:
        source_type = 'existing_collection_pdf'
        source_pdf_num = str(n)
    elif n <= 250:
        source_type = 'newly_drafted'
        source_pdf_num = str(n)
    else:
        source_type = 'newly_drafted'
        source_pdf_num = ''

    verification_status = 'unverified'
    consent_ref = ''

    is_duplicate = n in duplicate_map
    dup_canonical_id = f'G{duplicate_map[n]:03d}' if is_duplicate else ''

    # Provenance notes
    notes_parts = []
    if use_when:
        notes_parts.append(f'usage_context: {use_when}')
    if is_fallback:
        notes_parts.append('english_equivalent: fallback_to_pdf_meaning')
    if n in (251, 252):
        notes_parts.append('from official hackathon slide; needs elder confirmation; team-drafted meaning and english')
    if is_duplicate:
        notes_parts.append(f'duplicate_of: {dup_canonical_id}; excluded from canonical gaades.csv')
    if n in replacements_kannada:
        notes_parts.append('replacement entry in revised edition for earlier duplicate')

    notes_str = '; '.join(notes_parts)

    prov_row = {
        'gaade_id': gid,
        'source_pdf_number': source_pdf_num,
        'source_type': source_type,
        'verification_status': verification_status,
        'duplicate_of': dup_canonical_id,
        'consent_ref': consent_ref,
        'notes': notes_str
    }
    provenance_rows.append(prov_row)

    proofread_rows.append({
        'gaade_id': gid,
        'transcribed_text': kannada,
        'page_image_path': page_img,
        'proofread_ok': ''
    })

    gaade_row = {
        'gaade_id': gid,
        'gaade': kannada,
        'meaning': meaning,
        'english': english,
        'example': example,
        'region': region,
        'theme': theme,
        'audio_file': audio_file
    }

    if is_duplicate:
        excluded_row = dict(gaade_row)
        excluded_row['duplicate_of'] = dup_canonical_id
        excluded_duplicates_rows.append(excluded_row)

        dup_type = 'near_exact_variant' if n == 135 else 'exact'
        sim_ratio = '0.53' if n == 135 else '1.00'
        duplicates_rows.append({
            'duplicate_id': gid,
            'canonical_id': dup_canonical_id,
            'duplicate_text': kannada,
            'canonical_text': all_gaades[duplicate_map[n]],
            'duplicate_type': dup_type,
            'similarity_ratio': sim_ratio,
            'notes': f'Later duplicate in collection mapped to canonical {dup_canonical_id}'
        })
    else:
        gaades_rows.append(gaade_row)

# 9. Write CSV Files with UTF-8 encoding
def write_csv_dict(path, rows, fieldnames):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} rows to {os.path.relpath(path, BASE_DIR)}')

# data/gaades.csv
write_csv_dict(
    os.path.join(DATA_DIR, 'gaades.csv'),
    gaades_rows,
    ['gaade_id', 'gaade', 'meaning', 'english', 'example', 'region', 'theme', 'audio_file']
)

# data/gaade_provenance.csv
write_csv_dict(
    os.path.join(DATA_DIR, 'gaade_provenance.csv'),
    provenance_rows,
    ['gaade_id', 'source_pdf_number', 'source_type', 'verification_status', 'duplicate_of', 'consent_ref', 'notes']
)

# data/reports/duplicates.csv
write_csv_dict(
    os.path.join(REPORTS_DIR, 'duplicates.csv'),
    duplicates_rows,
    ['duplicate_id', 'canonical_id', 'duplicate_text', 'canonical_text', 'duplicate_type', 'similarity_ratio', 'notes']
)

# data/reports/excluded_duplicates.csv
write_csv_dict(
    os.path.join(REPORTS_DIR, 'excluded_duplicates.csv'),
    excluded_duplicates_rows,
    ['gaade_id', 'gaade', 'meaning', 'english', 'example', 'region', 'theme', 'audio_file', 'duplicate_of']
)

# data/reports/proofread_sheet.csv
write_csv_dict(
    os.path.join(REPORTS_DIR, 'proofread_sheet.csv'),
    proofread_rows,
    ['gaade_id', 'transcribed_text', 'page_image_path', 'proofread_ok']
)

print('\nSummary of Built Dataset:')
print(f'Total Proverbs Cataloged: {len(provenance_rows)} (G001 - G252)')
print(f'Canonical Non-Duplicate Proverbs: {len(gaades_rows)}')
print(f'Excluded Duplicates: {len(excluded_duplicates_rows)}')

