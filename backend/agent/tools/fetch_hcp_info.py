from langchain.tools import tool

@tool
def fetch_hcp_info(name: str):
    """
    Fetch HCP details by name.
    """
    db = {
        "Dr Sarah Smith": {
            "specialty": "Cardiologist",
            "last_interaction": "2026-04-10"
        }
    }

    return db.get(name, {})