import os, sys
sys.path.insert(0, os.path.abspath("gaade-kosha"))
from scripts.asr_compare import main

if __name__ == "__main__":
    sys.exit(main())
