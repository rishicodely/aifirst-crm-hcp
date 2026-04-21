from agent.llm import llm
from langchain.tools import tool

@tool
def suggest_followup(text: str):
    """
    Suggest next action using LLM.
    """
    prompt = f"""
Given this interaction:
{text}

Suggest a next best action for a pharma sales rep.
Return short actionable advice.
"""

    response = llm.invoke(prompt)

    return {
        "follow_up": response.content
    }