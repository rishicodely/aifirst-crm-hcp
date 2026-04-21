# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from the `backend/` directory with the local venv activated (`source venv/bin/activate`).

- Run the API: `uvicorn main:app --reload`
- Ad-hoc tool smoke test: `python test_log.py` (invokes `log_interaction_tool` directly, bypasses the graph)
- Ad-hoc LLM smoke test: `python test_llm.py` (pings Groq via `agent.llm.llm`)
- Install deps: `pip install -r requirements.txt`
- No test framework or linter is configured. The `test_*.py` files are scratch scripts, not pytest cases.

Environment: `.env` must define `GROQ_API_KEY` (loaded by `agent/llm.py` via python-dotenv).

## Architecture

Single FastAPI service wrapping a LangGraph agent that extracts structured CRM interaction data from free-text HCP (healthcare professional) interaction descriptions.

**Request flow** (`POST /chat` in `main.py`):
1. Client sends `{ message, form_state }`.
2. `graph.invoke(...)` runs the LangGraph in `agent/graph.py`.
3. Response returns `{ formUpdates }` — a partial dict of fields to merge into the client-side form.

**Graph shape** (`agent/graph.py`):
- `agent` node → `tool_node` → `END` (one-shot; tools do not loop back to the agent).
- The LLM is bound with `tool_choice="required"` — it is forced to call exactly one of `log_interaction` or `edit_interaction`. The system prompt explicitly forbids free-text replies.
- `should_continue` routes to `tools` only if the LLM produced a tool call; otherwise ends.

**State** (`agent/state.py`): `AgentState` is a `TypedDict` with `messages`, `form_state` (current form from client), `form_updates` (partial output returned to client).

**Tools** (`agent/tools/`):
- `log_interaction`: new interaction → full structured `InteractionData` (hcp_name, interaction_type, date/time, topics, materials_shared, sentiment, attendees). The tool prompt injects today's date so the LLM can resolve relative dates ("yesterday"). `clean_output` strips self-references from attendees and `"discussed "` prefixes from topics.
- `edit_interaction`: correction to an existing form → **partial** dict containing only changed fields (None-valued keys are filtered out). Receives `current_form` alongside the edit text.
- `fetch_hcp_info.py`, `schedule_reminder.py`, `suggest_followup.py` exist as empty placeholders — not wired into the graph.

**LLM** (`agent/llm.py`): single shared `ChatGroq` instance using `llama-3.1-8b-instant`. Both tools use `llm.with_structured_output(<PydanticModel>)` for reliable JSON extraction.

## Known gaps

- `db/models.py`, `db/session.py`, `schemas.py` are empty placeholders — no persistence layer exists yet.
- `agent/tools/fetch_hcp_info.py`, `schedule_reminder.py`, `suggest_followup.py` are empty placeholders — not wired into the graph.
