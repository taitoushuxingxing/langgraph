"""Beginner example 03: a graph can loop and improve its own output.

This file introduces a practical LangGraph idea: do work, review it,
and retry if the quality is not good enough.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class DraftState(TypedDict):
    # revision_count helps us avoid an endless loop.
    topic: str
    draft: str
    review_score: int
    revision_count: int


def write_draft(state: DraftState) -> dict:
    revision_count = state.get("revision_count", 0)

    if revision_count == 0:
        draft = f"Short draft about {state['topic']}."
    else:
        draft = (
            f"Improved draft about {state['topic']} with clearer structure, "
            "an example, and a short conclusion."
        )

    return {"draft": draft}


def review_draft(state: DraftState) -> dict:
    draft = state["draft"]
    score = 9 if "example" in draft and "conclusion" in draft else 6

    return {"review_score": score}


def decide_next_step(state: DraftState) -> Literal["rewrite", "finish"]:
    # The router decides whether to continue the loop or stop.
    if state["review_score"] >= 8:
        return "finish"

    if state.get("revision_count", 0) >= 1:
        return "finish"

    return "rewrite"


def prepare_rewrite(state: DraftState) -> dict:
    return {"revision_count": state.get("revision_count", 0) + 1}


def build_graph():
    graph = StateGraph(DraftState)

    graph.add_node("write_draft", write_draft)
    graph.add_node("review_draft", review_draft)
    graph.add_node("prepare_rewrite", prepare_rewrite)

    graph.add_edge(START, "write_draft")
    graph.add_edge("write_draft", "review_draft")
    # If review fails, the graph goes back for another pass.
    graph.add_conditional_edges(
        "review_draft",
        decide_next_step,
        {
            "rewrite": "prepare_rewrite",
            "finish": END,
        },
    )
    graph.add_edge("prepare_rewrite", "write_draft")

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke(
        {
            "topic": "LangGraph state",
            "draft": "",
            "review_score": 0,
            "revision_count": 0,
        }
    )

    print("Topic:", result["topic"])
    print("Revision count:", result["revision_count"])
    print("Review score:", result["review_score"])
    print("Final draft:", result["draft"])