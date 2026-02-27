import sys
from pathlib import Path

# Support running this file directly: `python backend/init__db.py`.
if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.crud import ensure_sections
from backend.database import Base, SessionLocal, engine


def initialize_database() -> None:
    # Create all tables first, then seed fixed sections.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_sections(db)
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully with default sections.")
