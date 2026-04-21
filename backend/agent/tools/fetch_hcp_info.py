from langchain.tools import tool
from db.session import SessionLocal
from db.models import HCP


@tool
def fetch_hcp_info(name: str):
    """
    Fetch HCP details from database by name (fuzzy match).
    """
    db = SessionLocal()
    try:
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{name}%")).first()

        if not hcp:
            return {"hcp_lookup_status": f"No HCP found matching '{name}'"}

        return {
            "hcp_name": hcp.name,
            "specialty": hcp.specialty,
            "last_interaction": hcp.last_interaction,
            "hcp_lookup_status": f"Found {hcp.name} ({hcp.specialty})",
        }
    finally:
        db.close()