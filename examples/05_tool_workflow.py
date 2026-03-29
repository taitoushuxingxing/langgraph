"""Beginner example 05: choose and call a tool inside a graph.

This version uses simple rules so you can understand the workflow shape
before replacing the router with a real LLM.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class ToolState(TypedDict):
    # selected_tool records the routing decision.
    question: str
    selected_tool: str
    tool_result: str
    final_answer: str


def choose_tool(state: ToolState) -> dict:
    question = state["question"].lower()

    if any(word in question for word in ["add", "sum", "plus"]):
        selected_tool = "calculator"
    elif "policy" in question or "refund" in question:
        selected_tool = "faq_lookup"
    else:
        selected_tool = "fallback"

    return {"selected_tool": selected_tool}


def route_tool(state: ToolState) -> Literal["calculator_tool", "faq_tool", "fallback_tool"]:
    # This router maps the decision into the next node name.
    mapping = {
        "calculator": "calculator_tool",
        "faq_lookup": "faq_tool",
        "fallback": "fallback_tool",
    }
    return mapping[state["selected_tool"]]


def calculator_tool(state: ToolState) -> dict:
    numbers = [int(token) for token in state["question"].split() if token.isdigit()]
    total = sum(numbers)
    return {"tool_result": f"The calculator tool found total = {total}."}


def faq_tool(state: ToolState) -> dict:
    return {"tool_result": "The FAQ tool says refunds are allowed within 7 days."}


def fallback_tool(state: ToolState) -> dict:
    return {"tool_result": "No matching tool was found, so a general response will be used."}


def finalize_answer(state: ToolState) -> dict:
    return {
        "final_answer": (
            f"Selected tool: {state['selected_tool']}. "
            f"Result: {state['tool_result']}"
        )
    }


def build_graph():
    graph = StateGraph(ToolState)

    graph.add_node("choose_tool", choose_tool)
    graph.add_node("calculator_tool", calculator_tool)
    graph.add_node("faq_tool", faq_tool)
    graph.add_node("fallback_tool", fallback_tool)
    graph.add_node("finalize_answer", finalize_answer)

    graph.add_edge(START, "choose_tool")
    # After tool selection, the graph jumps to exactly one tool node.
    graph.add_conditional_edges("choose_tool", route_tool)
    graph.add_edge("calculator_tool", "finalize_answer")
    graph.add_edge("faq_tool", "finalize_answer")
    graph.add_edge("fallback_tool", "finalize_answer")
    graph.add_edge("finalize_answer", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    samples = [
        "Please add 12 and 30",
        "What is your refund policy?",
        "Tell me something helpful",
    ]

    for sample in samples:
        result = app.invoke({"question": sample})
        print("-" * 60)
        print("Question:", sample)
        print("Selected tool:", result["selected_tool"])
        print("Final answer:", result["final_answer"])