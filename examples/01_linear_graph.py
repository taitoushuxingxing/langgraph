"""Beginner example 01: the smallest useful LangGraph.

Read this file in this order:
1. QAState: what data exists in the graph.
2. normalize_question: first node.
3. answer_question: second node.
4. build_graph: how the nodes are connected.
5. __main__: how the graph is executed.
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class QAState(TypedDict):
    # This is the shared state that flows through the graph.
    question: str
    normalized_question: str
    answer: str


def normalize_question(state: QAState) -> dict:
    # A node reads the current state and returns only the fields it updates.
    return {"normalized_question": state["question"].strip().lower()}


def answer_question(state: QAState) -> dict:
    question = state["normalized_question"]

    if "langgraph" in question:
        answer = "LangGraph is a workflow framework for building stateful LLM applications."
    else:
        answer = "This demo uses a simple rule-based answer so you can focus on graph basics."

    return {"answer": answer}


def build_graph():
    # StateGraph tells LangGraph what the shared state shape looks like.
    graph = StateGraph(QAState)

    graph.add_node("normalize_question", normalize_question)
    graph.add_node("answer_question", answer_question)

    # Execution starts at START and ends at END.
    graph.add_edge(START, "normalize_question")
    graph.add_edge("normalize_question", "answer_question")
    graph.add_edge("answer_question", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    # invoke runs the whole graph once and returns the final state.
    result = app.invoke({"question": " What is LangGraph? "})
    print("Question:", result["question"])
    print("Normalized:", result["normalized_question"])
    print("Answer:", result["answer"])