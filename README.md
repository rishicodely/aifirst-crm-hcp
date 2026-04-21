# AI-First CRM — HCP Log Interaction Module

An AI-driven CRM module for pharmaceutical field sales reps to log interactions with Healthcare Professionals (HCPs) via natural conversation instead of manual form-filling. The entire form on the left is populated and edited by an LLM agent on the right — users never type into the form directly.

Built as Round 1 Task 1 of the Masarrati IT Studio assignment.

---

## Demo Flow

> "Met Dr. Sarah Smith yesterday at 3pm, discussed Prodo-X, positive meeting, shared brochure."

The agent calls `log_interaction`, extracts every field, resolves "yesterday" to an ISO date, and the form on the left populates live.

> "Actually change sentiment to neutral."

The agent calls `edit_interaction` — only `sentiment` updates, every other field stays intact.

> "Who is Dr. Rajesh Patel?" → `fetch_hcp_info` queries the DB
> "What should I do next?" → `suggest_followup` generates a recommendation via LLM
> "Remind me next Tuesday to follow up." → `schedule_reminder` parses the date and persists a reminder

---

## Architecture

```
┌───────────────────────────┐           ┌──────────────────────────────┐
│   React + Redux (UI)      │           │   FastAPI Backend            │
│                           │           │                              │
│  ┌─────────────────────┐  │   HTTP    │   POST /chat                 │
│  │ InteractionForm     │  │  ◄─────►  │   POST /save                 │
│  │ (disabled inputs)   │  │           │                              │
│  └─────────────────────┘  │           │   ┌──────────────────────┐   │
│  ┌─────────────────────┐  │           │   │  LangGraph Agent     │   │
│  │ ChatPanel           │  │           │   │  (StateGraph)        │   │
│  │ (sends messages)    │  │           │   │                      │   │
│  └─────────────────────┘  │           │   │  agent_node          │   │
│                           │           │   │      │               │   │
│  Redux Store:             │           │   │      ▼ (tool call?)  │   │
│  - interactionSlice       │           │   │  tool_node           │   │
│  - chatSlice              │           │   │      │               │   │
│                           │           │   │      ▼               │   │
└───────────────────────────┘           │   │   END                │   │
                                        │   └──────────┬───────────┘   │
                                        │              │               │
                                        │     ┌────────┴────────┐      │
                                        │     │  5 LangGraph    │      │
                                        │     │  Tools (LLM     │      │
                                        │     │  + DB)          │      │
                                        │     └────────┬────────┘      │
                                        │              │               │
                                        │     ┌────────┴────────┐      │
                                        │     │  Groq LLM       │      │
                                        │     │  (llama-3.3)    │      │
                                        │     └─────────────────┘      │
                                        │                              │
                                        │     ┌─────────────────┐      │
                                        │     │  SQLite DB      │      │
                                        │     │  - hcps         │      │
                                        │     │  - interactions │      │
                                        │     │  - reminders    │      │
                                        │     └─────────────────┘      │
                                        └──────────────────────────────┘
```

**How a message flows:**

1. User types into `ChatPanel` → POST `/chat` with `{message, form_state}`
2. LangGraph `agent_node` calls the LLM with bound tools and the system prompt
3. LLM picks one of 5 tools and produces a tool call with structured args
4. `tool_node` dispatches to the correct tool handler, collects `form_updates` and `tools_used`
5. Backend returns `{formUpdates, assistantMessage, toolsUsed}`
6. Frontend dispatches `updateFields(formUpdates)` → form re-renders with new values
7. Chat panel displays the assistant message with the tool badge

---

## Tech Stack

| Layer    | Tech                                                             |
| -------- | ---------------------------------------------------------------- |
| Frontend | React 18 (Vite), Redux Toolkit, Axios                            |
| Backend  | Python 3.11, FastAPI, Uvicorn                                    |
| Agent    | LangGraph 1.1.x, LangChain 1.2.x                                 |
| LLM      | Groq — `llama-3.3-70b-versatile` (gemma2-9b-it also supported)   |
| Database | SQLite (via SQLAlchemy) — swap `DATABASE_URL` for Postgres/MySQL |
| Font     | Google Inter                                                     |

---

## Project Structure

```
aifirst-crm-hcp/
├── backend/
│   ├── agent/
│   │   ├── graph.py              # LangGraph StateGraph + agent/tool nodes
│   │   ├── state.py              # AgentState TypedDict
│   │   ├── llm.py                # Groq client
│   │   └── tools/
│   │       ├── log_interaction.py
│   │       ├── edit_interaction.py
│   │       ├── fetch_hcp_info.py
│   │       ├── suggest_followup.py
│   │       └── schedule_reminder.py
│   ├── db/
│   │   ├── models.py             # SQLAlchemy models: HCP, Interaction, Reminder
│   │   ├── session.py            # Engine + session factory
│   │   └── seed.py               # Seeds 8 HCPs
│   ├── main.py                   # FastAPI app + /chat + /save
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/store.js
    │   ├── features/
    │   │   ├── interactionSlice.js
    │   │   └── chatSlice.js
    │   ├── components/
    │   │   ├── InteractionForm.jsx   # AI-controlled, disabled inputs
    │   │   └── ChatPanel.jsx
    │   ├── App.jsx
    │   └── main.jsx
    ├── index.html                 # Inter font link
    └── package.json
```

---

## Setup & Run

### Prerequisites

- Python 3.10+
- Node 18+
- A [Groq API key](https://console.groq.com/keys)

### 1. Backend

```bash
cd backend

# Create and activate virtualenv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
echo "GROQ_API_KEY=your_groq_key_here" > .env

# Seed the HCPs table
python -m db.seed

# Run the server
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Open the frontend URL in your browser and start typing into the chat panel on the right. The form on the left will populate automatically.

---

## Environment Variables

| Variable       | Required | Description                             |
| -------------- | -------- | --------------------------------------- |
| `GROQ_API_KEY` | Yes      | Your Groq API key from console.groq.com |

---

## The 5 LangGraph Tools

All 5 tools are registered with the LangGraph agent via `llm.bind_tools(...)`. The agent's system prompt classifies user intent and routes to exactly one tool per turn.

### 1. `log_interaction` (mandatory)

Extracts structured interaction details from a free-text description using the LLM with Pydantic structured output.

- Resolves relative dates (`"yesterday"`, `"this morning"`) to ISO `YYYY-MM-DD`
- Parses times into 24-hour `HH:MM`
- Extracts HCP name, interaction type, topics, materials shared, sentiment, attendees
- Cleans output: strips filler words, de-duplicates attendees vs HCP

**Example prompt:** _"Met Dr. Sarah Smith yesterday at 3pm, discussed Prodo-X, positive meeting, shared brochure"_

**Returns:** `{hcp_name, interaction_type, date, time, topics, materials_shared, sentiment}`

### 2. `edit_interaction` (mandatory)

Surgical edit of an existing interaction. Only fields explicitly mentioned by the user are updated — all other fields remain unchanged. Uses the LLM with structured output to return a partial JSON of deltas only.

**Example prompt:** _"Change sentiment to neutral"_ (with current form containing a full interaction)

**Returns:** `{sentiment: "neutral"}` — and nothing else

### 3. `fetch_hcp_info`

Queries the `hcps` table with a fuzzy (`ILIKE`) name match. Returns the HCP's specialty and last interaction date. Demonstrates agent + database integration.

**Example prompt:** _"Who is Dr. Rajesh Patel?"_

**Returns:** `{hcp_name, specialty, last_interaction, hcp_lookup_status}`

### 4. `suggest_followup`

Uses the LLM to generate a next-best-action recommendation tailored to a pharma sales rep. Takes the interaction context (topics, sentiment, HCP) and produces actionable advice.

**Example prompt:** _"What should I do next?"_

**Returns:** `{follow_up: "Share detailed Phase 3 clinical data with Dr. Smith..."}` (LLM-generated)

### 5. `schedule_reminder`

Uses the LLM to parse natural-language dates (`"next Tuesday"`, `"in 3 days"`) into ISO format, then persists a row in the `reminders` table.

**Example prompt:** _"Remind me next Tuesday to follow up"_

**Returns:** `{reminder_date, reminder_id, reminder_status}` — and a new row in the DB

---

## API Reference

### `POST /chat`

Main endpoint. Routes the user message through the LangGraph agent.

**Request:**

```json
{
  "message": "Met Dr. Smith yesterday...",
  "form_state": { "hcp_name": "...", "sentiment": "..." }
}
```

**Response:**

```json
{
  "formUpdates": {
    "hcp_name": "Dr. Sarah Smith",
    "interaction_type": "meeting",
    "date": "2026-04-20",
    "time": "15:00",
    "topics": ["Prodo-X"],
    "materials_shared": ["brochure"],
    "sentiment": "positive"
  },
  "assistantMessage": "Logged interaction with Dr. Sarah Smith. Review the form and edit if needed.",
  "toolsUsed": ["log_interaction"]
}
```

### `POST /save`

Persists the finalized interaction to the `interactions` table.

**Request:** the full Redux form state object

**Response:** `{"message": "Saved successfully"}`

---

## Sample Test Commands

Run each of these via `curl` to verify all 5 tools independently:

```bash
# 1. Log a new interaction
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Met Dr. Sarah Smith yesterday at 3pm, discussed Prodo-X, positive meeting, shared brochure", "form_state": {}}'

# 2. Edit a field
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Change sentiment to neutral", "form_state": {"hcp_name": "Dr. Sarah Smith", "sentiment": "positive"}}'

# 3. Fetch HCP info
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who is Dr. Rajesh Patel?", "form_state": {}}'

# 4. Suggest follow-up
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I do next?", "form_state": {"hcp_name": "Dr. Sarah Smith", "sentiment": "positive", "topics": ["Prodo-X"]}}'

# 5. Schedule a reminder
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Remind me next Tuesday to follow up", "form_state": {}}'
```

---

## Design Decisions

**Form is intentionally read-only.** The assignment's core requirement is that users drive the form through the AI, not by typing. All inputs on the left panel use the `disabled` attribute — this makes the AI-controlled nature immediately obvious to reviewers and enforces the intended UX.

**Every field fill goes through a LangGraph tool.** No field is populated by hard-coded string parsing. Even the edit flow — which feels like it could be done with regex — uses the LLM with structured output to decide which fields to change. This is central to the assignment's grading criterion.

**`edit_interaction` returns partial JSON.** The prompt explicitly instructs the LLM to return _only_ changed fields. This prevents unintended overwrites when the user says "change just the sentiment" — other fields stay untouched. Tested and verified via curl.

**SQLite by default, swap for Postgres in production.** Change `DATABASE_URL` in `db/session.py` to a Postgres/MySQL connection string. Schema is portable SQLAlchemy.

**No forced tool-call fallback.** The system prompt is strong enough (with few-shot examples for each tool) that the LLM reliably picks a tool without any hardcoded routing logic.

---

## Seeded Test Data

The `db/seed.py` script populates 8 HCPs for testing `fetch_hcp_info`:

- Dr. Sarah Smith (Cardiologist)
- Dr. John Smith (General Physician)
- Dr. Rajesh Patel (Endocrinologist)
- Dr. Priya Sharma (Oncologist)
- Dr. Michael Kim (Neurologist)
- Dr. Anjali Reddy (Pediatrician)
- Dr. David Lee (Dermatologist)
- Dr. Fatima Khan (Psychiatrist)

---

## Known Limitations

- Single-user, no authentication (out of scope for assignment).
- Conversation history is not sent to the backend — each `/chat` call is stateless. Multi-turn follow-ups (_"actually make that Tuesday"_) rely on the current form state rather than full message history.
- `fetch_hcp_info` uses a simple `ILIKE` match — a search for "Dr. Patel" won't find "Dr. Rajesh Patel" because of the middle name. Use full names or last names alone for reliable lookup.
- No rate limiting on Groq API calls.
- No tests (time-boxed submission).

---

## Submission Checklist

- [x] React frontend with Redux state management
- [x] Split-screen layout matching the brief's screenshot
- [x] Form fields are AI-controlled (disabled — users cannot type)
- [x] FastAPI backend
- [x] LangGraph agent with 5 tools
- [x] Two mandatory tools: `log_interaction` and `edit_interaction`
- [x] Three additional tools: `fetch_hcp_info`, `suggest_followup`, `schedule_reminder`
- [x] Groq LLM integration
- [x] SQL database (SQLite — swappable for Postgres/MySQL)
- [x] Google Inter font
- [x] README with setup and architecture

---

## Author

Built by Rishika Reddy
