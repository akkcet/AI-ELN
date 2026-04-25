# backend/agents/orchestrator_graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict

from backend.agents.qna_agent import qna_agent
from backend.agents.admin_request_agent import admin_request_agent, is_admin_request
from backend.agents.workflow_agent import workflow_agent, is_workflow_command

class ChatState(TypedDict):
    message: str
    user: str
    response: str

async def orchestrator_node(state: ChatState):
    msg = state["message"].lower()

    # Route based on intent
    if is_workflow_command(msg):
        state["response"] = workflow_agent(state["message"], state["user"])
        return state

    if is_admin_request(msg):
        state["response"] = admin_request_agent(state["message"], state["user"])
        return state

    # Default → QnA Agent (your existing pipeline)
    state["response"] = await qna_agent(state["message"])
    return state

def build_orchestrator():
    graph = StateGraph(ChatState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", END)
    return graph.compile()