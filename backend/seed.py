"""
Seed script for HCPs table.
Run: python -m db.seed
"""
from db.session import SessionLocal, engine
from db.models import Base, HCP

Base.metadata.create_all(bind=engine)

HCPS = [
    {"name": "Dr. Sarah Smith", "specialty": "Cardiologist", "last_interaction": "2026-04-10"},
    {"name": "Dr. John Smith", "specialty": "General Physician", "last_interaction": "2026-03-22"},
    {"name": "Dr. Rajesh Patel", "specialty": "Endocrinologist", "last_interaction": "2026-04-05"},
    {"name": "Dr. Priya Sharma", "specialty": "Oncologist", "last_interaction": "2026-02-18"},
    {"name": "Dr. Michael Kim", "specialty": "Neurologist", "last_interaction": "2026-04-15"},
    {"name": "Dr. Anjali Reddy", "specialty": "Pediatrician", "last_interaction": "2026-03-30"},
    {"name": "Dr. David Lee", "specialty": "Dermatologist", "last_interaction": "2026-04-12"},
    {"name": "Dr. Fatima Khan", "specialty": "Psychiatrist", "last_interaction": "2026-04-08"},
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(HCP).count()
        if existing > 0:
            print(f"HCPs table already has {existing} rows. Skipping seed.")
            return

        for hcp_data in HCPS:
            db.add(HCP(**hcp_data))
        db.commit()
        print(f"✓ Seeded {len(HCPS)} HCPs")
    finally:
        db.close()


if __name__ == "__main__":
    seed()