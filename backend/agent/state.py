from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    form_state: Dict[str, Any]
    form_updates: Dict[str, Any]
    tools_used: List[str]   

