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


def generate_message(updates, tools):
    """Generate a natural-feeling reply based on which tool ran and what it returned."""
    if not tools:
        return "I'm not sure how to help with that. Try describing an interaction, asking about an HCP, or requesting a follow-up."

    tool = tools[0]

    if tool == "log_interaction":
        hcp = updates.get("hcp_name")
        if hcp:
            return f"Logged interaction with {hcp}. Review the form and edit if needed."
        return "Logged interaction. Review the form and edit if needed."

    if tool == "edit_interaction":
        changed = [k for k in updates.keys() if k not in ("hcp_lookup_status", "follow_up", "reminder_date", "reminder_status", "reminder_id")]
        if changed:
            return f"Updated: {', '.join(changed)}."
        return "Updated interaction details."

    if tool == "fetch_hcp_info":
        status = updates.get("hcp_lookup_status", "")
        last = updates.get("last_interaction")
        if last:
            return f"{status}. Last interaction: {last}."
        return status or "Looked up HCP."

    if tool == "suggest_followup":
        follow_up = updates.get("follow_up")
        return follow_up if follow_up else "Here's a suggested next step."

    if tool == "schedule_reminder":
        status = updates.get("reminder_status")
        return status if status else "Reminder scheduled."

    return "Action completed."


@app.post("/chat")
def chat(req: dict):
    user_message = req["message"]
    form_state = req.get("form_state", {})

    result = graph.invoke({
        "messages": [HumanMessage(content=user_message)],
        "form_state": form_state,
        "form_updates": {},
        "tools_used": [],
    })

    form_updates = result.get("form_updates", {})
    tools_used = result.get("tools_used", [])
    assistant_message = generate_message(form_updates, tools_used)

    # Strip non-form keys from form_updates before sending to frontend
    # (keep only fields the form actually displays)
    form_fields = {
        "hcp_name", "interaction_type", "date", "time",
        "topics", "materials_shared", "sentiment", "attendees",
    }
    clean_form_updates = {k: v for k, v in form_updates.items() if k in form_fields}

    return {
        "formUpdates": clean_form_updates,
        "assistantMessage": assistant_message,
        "toolsUsed": tools_used,
    }


@app.post("/save")
def save_interaction(data: dict):
    allowed = {c.key for c in inspect(Interaction).mapper.column_attrs}
    payload = {k: v for k, v in data.items() if k in allowed and k != "id"}

    db = SessionLocal()
    try:
        interaction = Interaction(**payload)
        db.add(interaction)
        db.commit()
    finally:
        db.close()

    return {"message": "Saved successfully"}