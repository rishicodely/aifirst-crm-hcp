from fastapi import FastAPI
from sqlalchemy import inspect
from agent.graph import build_graph
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware
from db.models import Base, Interaction
from db.session import engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()

graph = build_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/save")
def save_interaction(data: dict):
    allowed = {c.key for c in inspect(Interaction).mapper.column_attrs}
    payload = {k: v for k, v in data.items() if k in allowed}

    db = SessionLocal()
    try:
        interaction = Interaction(**payload)
        db.add(interaction)
        db.commit()
    finally:
        db.close()

    return {"message": "Saved successfully"}