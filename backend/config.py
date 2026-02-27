import os
from pathlib import Path

# Use an absolute DB path so app behavior is stable from any working directory.
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "library.db"

# Allow override in production deployments.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# Business rules.
FINE_PER_DAY = 500
DEFAULT_BORROW_DAYS = 7
MAX_BORROW_DAYS = 30

# Fixed library sections required by the system.
LIBRARY_SECTIONS = [
    "SCIENCES",
    "ARTS",
    "SOCIALS",
    "ECONOMICS",
    "RELIGION",
    "GENERAL STUDIES",
]
