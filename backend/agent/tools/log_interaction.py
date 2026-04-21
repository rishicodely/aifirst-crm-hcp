from pydantic import BaseModel
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from agent.llm import llm
from datetime import datetime
from langchain.tools import tool

@tool
def log_interaction(text: str) -> dict:
    """
    Extract structured interaction data from a natural language description.
    """
    return log_interaction_tool(text)

class InteractionData(BaseModel):
    hcp_name: Optional[str]
    interaction_type: Optional[str]
    date: Optional[str]
    time: Optional[str]
    topics: Optional[List[str]]
    materials_shared: Optional[List[str]]
    sentiment: Optional[str]
    attendees: Optional[List[str]]

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a pharma CRM assistant.

Extract structured interaction details from user input.

STRICT RULES:
- Return ONLY valid JSON
- Do NOT include any explanations or extra text

FIELD RULES:
- hcp_name: full name if mentioned, else null
- interaction_type: meeting, call, email, etc.
- date: MUST be in YYYY-MM-DD format (resolve relative dates like "yesterday")
- time: MUST be in HH:MM (24-hour)
- topics: short clean keywords ONLY (e.g. ["Prodo-X"]), NOT phrases
- materials_shared: clean names only (e.g. ["brochure"])
- sentiment: one of [positive, neutral, negative]
- attendees: ONLY include if explicitly mentioned (NOT "I", NOT inferred)

CRITICAL:
- If not explicitly mentioned → return null
- Do NOT infer
- Do NOT hallucinate
"""),
    ("human", "{text}")
])

structured_llm = llm.with_structured_output(InteractionData)

def clean_output(data: dict):
    if data.get("attendees"):

        if data["attendees"] == ["I"]:
            data["attendees"] = None

        elif data["hcp_name"] and data["attendees"] == [data["hcp_name"]]:
            data["attendees"] = None

    if data.get("topics"):
        data["topics"] = [t.replace("discussed ", "").strip() for t in data["topics"]]

    return {k: v for k, v in data.items() if v is not None}

def log_interaction_tool(text: str):
    current_date = datetime.now().strftime("%Y-%m-%d")

    chain = prompt | structured_llm
    result = chain.invoke({
        "text": f"Today's date is {current_date}. \n\n{text}"
    })

    return clean_output(result.model_dump())