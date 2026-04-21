from fastapi import FastAPI
from agent.graph import build_graph
from langchain_core.messages import HumanMessage

app = FastAPI()

graph = build_graph()

@app.post("/chat")
def chat(req: dict):
    user_message = req["message"]
    form_state = req.get("form_state", {})

    result = graph.invoke({
        "messages": [HumanMessage(content=user_message)],
        "form_state": form_state,
        "form_updates": {}
    })

    return {
        "formUpdates": result.get("form_updates", {})
    }