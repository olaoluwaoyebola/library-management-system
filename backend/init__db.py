from database import engine, Base, SessionLocal
from models import Section

SECTIONS = [
    "SCIENCES",
    "ARTS",
    "SOCIALS",
    "ECONOMICS",
    "RELIGION",
    "GENERAL STUDIES"
]

Base.metadata.create_all(bind=engine)

db = SessionLocal()

for sec in SECTIONS:
    if not db.query(Section).filter(Section.name == sec).first():
        db.add(Section(name=sec))

db.commit()
db.close()

print("Database initialized successfully.")