from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    form_state: Dict[str, Any]
    form_updates: Dict[str, Any]