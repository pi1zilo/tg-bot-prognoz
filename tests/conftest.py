import sys
from pathlib import Path

# Add project root and src to sys.path so tests can import from src.app and app
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

for directory in (ROOT_DIR, SRC_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
