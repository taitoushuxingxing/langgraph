"""Advanced example 09: a real LLM plays planner, writer, and reviewer roles.

This is the upgrade path for example 06.
The graph shape is the same, but the content generation now comes from a model.
"""

import os
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.graph import END, START, StateGraph


class ReviewResult(BaseModel):
    approved: bool = Field(description="Whether the draft is good enough for a beginner.")
    feedback: str = Field(description="Short review feedback for the writer.")


class TeamState(TypedDict):
    topic: str
    outline: str
    draft: str
    review: str
    approved: bool
    revision_count: int


def get_model() -> ChatOpenAI:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    return ChatOpenAI(model=model_name, temperature=0)


def planner(state: TeamState) -> dict:
    model = get_model()
    response = model.invoke(
        [
            SystemMessage(
                content="Create a short beginner-friendly outline with 3 to 5 points."
            ),
            HumanMessage(content=f"Topic: {state['topic']}"),
        ]
    )
    return {"outline": response.content}


def writer(state: TeamState) -> dict:
    model = get_model()
    revision_note = ""
    if state.get("revision_count", 0) > 0:
        revision_note = f"Improve the draft based on this review feedback: {state['review']}"

    response = model.invoke(
        [
            SystemMessage(
                content=(
                    "Write a clear explanation for a complete beginner. "
                    "Use simple wording and include one small example."
                )
            ),
            HumanMessage(
                content=(
                    f"Topic: {state['topic']}\n"
                    f"Outline: {state['outline']}\n"
                    f"{revision_note}"
                )
            ),
        ]
    )
    return {"draft": response.content}


def reviewer(state: TeamState) -> dict:
    model = get_model().with_structured_output(ReviewResult)
    result = model.invoke(
        [
            SystemMessage(
                content=(
                    "Review the draft for beginner clarity. "
                    "Approve only if it is accurate, simple, and has at least one concrete example."
                )
            ),
            HumanMessage(
                content=(
                    f"Topic: {state['topic']}\n"
                    f"Draft: {state['draft']}"
                )
            ),
        ]
    )
    return {"approved": result.approved, "review": result.feedback}


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
            "topic": "How LangGraph conditional routing works",
            "outline": "",
            "draft": "",
            "review": "",
            "approved": False,
            "revision_count": 0,
        }
    )

    print("Outline:")
    print(result["outline"])
    print("\nDraft:")
    print(result["draft"])
    print("\nReview:")
    print(result["review"])
    print("\nApproved:", result["approved"])
    print("Revision count:", result["revision_count"])