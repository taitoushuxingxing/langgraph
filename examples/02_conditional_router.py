"""Beginner example 02: routing to different branches.

The key idea here is that a graph does not always follow one fixed path.
It can inspect the state and choose a different next node.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class SupportState(TypedDict):
    # The graph gradually fills these fields during execution.
    user_text: str
    intent: str
    response: str


def classify_intent(state: SupportState) -> dict:
    text = state["user_text"].lower()

    if "price" in text or "cost" in text:
        intent = "pricing"
    elif "refund" in text or "return" in text:
        intent = "refund"
    else:
        intent = "general"

    return {"intent": intent}


def route_by_intent(state: SupportState) -> Literal["pricing_node", "refund_node", "general_node"]:
    # This router decides which node should run next.
    mapping = {
        "pricing": "pricing_node",
        "refund": "refund_node",
        "general": "general_node",
    }
    return mapping[state["intent"]]


def pricing_node(state: SupportState) -> dict:
    return {"response": "Pricing questions go to the pricing workflow."}


def refund_node(state: SupportState) -> dict:
    return {"response": "Refund questions go to the refund workflow."}


def general_node(state: SupportState) -> dict:
    return {"response": "General questions go to the general support workflow."}


def build_graph():
    graph = StateGraph(SupportState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("pricing_node", pricing_node)
    graph.add_node("refund_node", refund_node)
    graph.add_node("general_node", general_node)

    graph.add_edge(START, "classify_intent")
    # Conditional edges are the core of branching workflows.
    graph.add_conditional_edges("classify_intent", route_by_intent)
    graph.add_edge("pricing_node", END)
    graph.add_edge("refund_node", END)
    graph.add_edge("general_node", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    samples = [
        "How much does the pro plan cost?",
        "I want a refund for my last order.",
        "What does this product do?",
    ]

    for sample in samples:
        result = app.invoke({"user_text": sample})
        print("-" * 60)
        print("Input:", sample)
        print("Intent:", result["intent"])
        print("Response:", result["response"])