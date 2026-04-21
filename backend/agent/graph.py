from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from agent.state import AgentState
from agent.llm import llm
from agent.tools.log_interaction import log_interaction
from agent.tools.edit_interaction import edit_interaction
from agent.tools.fetch_hcp_info import fetch_hcp_info
from agent.tools.suggest_followup import suggest_followup
from agent.tools.schedule_reminder import schedule_reminder
from langchain_core.messages import SystemMessage

tools = [
    log_interaction,
    edit_interaction,
    fetch_hcp_info,
    suggest_followup,
    schedule_reminder
]

llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    messages = state["messages"]

    system = SystemMessage(content="""
You are a CRM assistant.

Decide intelligently which tool to use:

- New interaction → log_interaction
- Edit request → edit_interaction
- Doctor info → fetch_hcp_info
- Next steps → suggest_followup
- Scheduling → schedule_reminder

IMPORTANT:
- Only call a tool if clearly needed
- Otherwise respond normally
- When calling tools, follow correct JSON format
""")

    response = llm_with_tools.invoke([system] + messages)

    if not getattr(response, "tool_calls", None):
        print(" No tool call → forcing log_interaction fallback")
        response.tool_calls = [{
            "name": "log_interaction",
            "args": {"text": messages[-1].content}
        }]

    return {
        "messages": messages + [response]
    }

def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    updates = {}

    tool_calls = getattr(last_message, "tool_calls", []) or []

    if not tool_calls:
        print("No tool calls received")
        return {"form_updates": {}}

    for call in tool_calls:
        name = call.get("name", "").strip()
        args = call.get("args", {}) or {}

        print(f"🔧 TOOL: {name}")
        print(f"ARGS: {args}")

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

        if isinstance(result, dict):
            updates.update(result)

    return {"form_updates": updates}

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
        {
            "tools": "tools",
            END: END
        }
    )

    builder.add_edge("tools", END)

    return builder.compile()