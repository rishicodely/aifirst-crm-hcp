from langchain.tools import tool

@tool
def suggest_followup(topics: list, sentiment: str):
    """
    Suggest next action based on interaction.
    """
    if sentiment == "positive":
        return {"follow_up": "Share detailed product information"}
    elif sentiment == "neutral":
        return {"follow_up": "Schedule follow-up meeting"}
    else:
        return {"follow_up": "Address concerns with more data"}