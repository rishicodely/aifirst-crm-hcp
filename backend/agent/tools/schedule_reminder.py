from langchain.tools import tool

@tool
def schedule_reminder(text: str):
    """
    Extract reminder date from text.
    """
    return {"reminder": "2026-04-25"}  # placeholder for now