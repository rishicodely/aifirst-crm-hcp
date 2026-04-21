from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from agent.state import AgentState
from agent.llm import llm
from agent.tools.log_interaction import log_interaction
from agent.tools.edit_interaction import edit_interaction
from langchain_core.messages import SystemMessage

tools = [log_interaction, edit_interaction]

llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    messages = state["messages"]

    system = SystemMessage(content="""
You are a CRM assistant.

Decide which tool to use:

- If user describes a new interaction → call log_interaction
- If user corrects or edits → call edit_interaction

If no tool is needed, respond normally.

Be accurate. Do not hallucinate.
""")

    response = llm_with_tools.invoke([system] + messages)

    return {
        "messages": messages + [response]
    }

def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    updates = {}

    for call in last_message.tool_calls:
        if call["name"] == "log_interaction":
            result = log_interaction.invoke(call["args"]["text"])
        elif call["name"] == "edit_interaction":
            result = edit_interaction.invoke({
                "text": call["args"]["text"],
                "current_form": state["form_state"]
            })
        else:
            result = {}
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