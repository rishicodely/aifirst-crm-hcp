from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.llm import llm
from agent.tools.log_interaction import log_interaction
from agent.tools.edit_interaction import edit_interaction
from agent.tools.fetch_hcp_info import fetch_hcp_info
from agent.tools.suggest_followup import suggest_followup
from agent.tools.schedule_reminder import schedule_reminder

tools = [
    log_interaction,
    edit_interaction,
    fetch_hcp_info,
    suggest_followup,
    schedule_reminder,
]

llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are a pharma CRM assistant helping sales reps log interactions with healthcare professionals (HCPs).

You MUST call exactly one tool for every user message. Choose based on intent:

1. log_interaction — user DESCRIBES a new interaction
   Examples:
   - "Met Dr. Smith yesterday, discussed Prodo-X, positive meeting"
   - "Called Dr. Patel about samples this morning"
   - "Email to Dr. Kim about new brochure"

2. edit_interaction — user CORRECTS or CHANGES existing form data
   Examples:
   - "Change sentiment to neutral"
   - "Actually it was Dr. John Smith, not Sarah"
   - "Update the date to Monday"
   - "The attendees should be Dr. Lee and Dr. Kim"

3. fetch_hcp_info — user ASKS ABOUT an HCP (specialty, past interactions, background)
   Examples:
   - "Who is Dr. Smith?"
   - "What's Dr. Patel's specialty?"
   - "Tell me about Dr. Kim"
   - "When did I last meet Dr. Sharma?"

4. suggest_followup — user asks for NEXT STEPS, recommendations, or advice
   Examples:
   - "What should I do next?"
   - "Suggest a follow-up action"
   - "What's my next best step with this HCP?"

5. schedule_reminder — user wants to SET A REMINDER or schedule something
   Examples:
   - "Remind me next Tuesday"
   - "Set a reminder for 3 days from now"
   - "Schedule a follow-up for next week"

Always call exactly one tool. Do not respond with plain text."""


def agent_node(state: AgentState):
    messages = state["messages"]
    system = SystemMessage(content=SYSTEM_PROMPT)
    response = llm_with_tools.invoke([system] + messages)
    return {"messages": messages + [response]}


def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    updates = {}
    tools_used = []

    tool_calls = getattr(last_message, "tool_calls", []) or []

    if not tool_calls:
        print("No tool calls received")
        return {"form_updates": {}, "tools_used": []}

    for call in tool_calls:
        name = call.get("name", "").strip()
        args = call.get("args", {}) or {}

        print(f"🔧 TOOL: {name}")
        print(f"ARGS: {args}")

        tools_used.append(name)

        try:
            if name == "log_interaction":
                result = log_interaction.invoke(args)

            elif name == "edit_interaction":
                result = edit_interaction.invoke({
                    **args,
                    "current_form": state["form_state"],
                })

            elif name == "fetch_hcp_info":
                result = fetch_hcp_info.invoke(args)

            elif name == "suggest_followup":
                result = suggest_followup.invoke(args)

            elif name == "schedule_reminder":
                result = schedule_reminder.invoke(args)

            else:
                result = {}
        except Exception as e:
            print(f"Tool {name} failed: {e}")
            result = {}

        if isinstance(result, dict):
            updates.update(result)

    return {"form_updates": updates, "tools_used": tools_used}


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)
    builder.set_entry_point("agent")
    builder.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", END)
    return builder.compile()