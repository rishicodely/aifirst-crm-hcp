from datetime import datetime
from langchain.tools import tool
from agent.llm import llm
from db.session import SessionLocal
from db.models import Reminder


@tool
def schedule_reminder(text: str):
    """
    Parse a reminder date from natural language and save it to the database.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""Extract the reminder date from the following text.

Text: {text}

RULES:
- Today's date is {current_date}
- Return ONLY the date in YYYY-MM-DD format
- No explanation, no extra text
- Resolve relative dates (e.g., "next Tuesday", "in 3 days") based on today's date
- If unclear, return the string: null
"""

    response = llm.invoke(prompt)
    parsed_date = (response.content or "").strip()

    if not parsed_date or parsed_date.lower() == "null":
        return {"reminder_status": "Could not parse reminder date"}

    # Persist to DB
    db = SessionLocal()
    try:
        reminder = Reminder(
            reminder_date=parsed_date,
            note=text,
            created_at=current_date,
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        reminder_id = reminder.id
    finally:
        db.close()

    return {
        "reminder_date": parsed_date,
        "reminder_id": reminder_id,
        "reminder_status": f"Reminder scheduled for {parsed_date}",
    }