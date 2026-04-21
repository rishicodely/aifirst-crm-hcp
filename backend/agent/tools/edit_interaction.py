from langchain.tools import tool
from pydantic import BaseModel
from typing import Optional, List
from agent.llm import llm
from langchain_core.prompts import ChatPromptTemplate


class EditData(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    topics: Optional[List[str]] = None
    materials_shared: Optional[List[str]] = None
    sentiment: Optional[str] = None
    attendees: Optional[List[str]] = None


prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are editing an existing CRM interaction.

IMPORTANT RULES:
- Only update fields explicitly mentioned by the user
- Do NOT modify other fields
- Return ONLY changed fields (partial JSON)
- Do NOT include unchanged fields
- Do NOT hallucinate

Example:
User: "change sentiment to neutral"
Output:
{{ "sentiment": "neutral" }}
"""),
    ("human", "Current form: {form}\n\nEdit request: {text}")
])

structured_llm = llm.with_structured_output(EditData)


@tool
def edit_interaction(text: str, current_form: dict) -> dict:
    """
    Modify specific fields in an existing interaction based on user correction.
    """
    chain = prompt | structured_llm
    result = chain.invoke({
        "text": text,
        "form": current_form
    })

    return {k: v for k, v in result.model_dump().items() if v is not None}