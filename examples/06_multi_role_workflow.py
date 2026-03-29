"""Beginner example 06: model a team workflow with separate roles.

This is not a full multi-agent system yet.
It is a simple graph where each node plays one responsibility.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class TeamState(TypedDict):
    # Each role writes back into the same shared state.
    topic: str
    plan: str
    draft: str
    review: str
    approved: bool
    revision_count: int


def planner(state: TeamState) -> dict:
    plan = (
        f"Plan for {state['topic']}: define the concept, explain why it matters, "
        "and give one simple example."
    )
    return {"plan": plan}


def writer(state: TeamState) -> dict:
    revision_count = state.get("revision_count", 0)

    if revision_count == 0:
        draft = f"Draft about {state['topic']}. It has the concept, but the example is weak."
    else:
        draft = (
            f"Revised draft about {state['topic']}. It defines the concept, explains its value, "
            "and includes a clear beginner example."
        )

    return {"draft": draft}


def reviewer(state: TeamState) -> dict:
    # Reviewer checks quality and decides whether the draft is acceptable.
    if "clear beginner example" in state["draft"]:
        return {"review": "Approved.", "approved": True}

    return {"review": "Please improve the example.", "approved": False}


def decide_after_review(state: TeamState) -> Literal["revise", "finish"]:
    if state["approved"]:
        return "finish"

    if state.get("revision_count", 0) >= 1:
        return "finish"

    return "revise"


def revise(state: TeamState) -> dict:
    return {"revision_count": state.get("revision_count", 0) + 1}


def build_graph():
    graph = StateGraph(TeamState)

    graph.add_node("planner", planner)
    graph.add_node("writer", writer)
    graph.add_node("reviewer", reviewer)
    graph.add_node("revise", revise)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "writer")
    graph.add_edge("writer", "reviewer")
    # Review can either finish the graph or trigger a revision loop.
    graph.add_conditional_edges(
        "reviewer",
        decide_after_review,
        {
            "revise": "revise",
            "finish": END,
        },
    )
    graph.add_edge("revise", "writer")

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke(
        {
            "topic": "LangGraph routing",
            "plan": "",
            "draft": "",
            "review": "",
            "approved": False,
            "revision_count": 0,
        }
    )

    print("Plan:", result["plan"])
    print("Draft:", result["draft"])
    print("Review:", result["review"])
    print("Approved:", result["approved"])
    print("Revision count:", result["revision_count"])