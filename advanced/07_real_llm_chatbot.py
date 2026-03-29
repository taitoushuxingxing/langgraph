"""Advanced example 07: replace a fake chatbot node with a real LLM.

This file keeps the graph structure simple and upgrades only one part:
the chatbot node now calls a real chat model.
"""

import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph


def get_model() -> ChatOpenAI:
    # Keep model selection configurable so you can switch models later.
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    return ChatOpenAI(model=model_name, temperature=0)


def llm_chatbot(state: MessagesState) -> dict:
    model = get_model()
    system_message = SystemMessage(
        content=(
            "You are a patient LangGraph tutor for beginners. "
            "Answer clearly, use simple language, and keep examples practical."
        )
    )

    response = model.invoke([system_message, *state["messages"]])
    return {"messages": [response]}


def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("llm_chatbot", llm_chatbot)
    graph.add_edge(START, "llm_chatbot")
    graph.add_edge("llm_chatbot", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


if __name__ == "__main__":
    app = build_graph()
    config = {"configurable": {"thread_id": "real-llm-demo"}}

    first_turn = app.invoke(
        {"messages": [HumanMessage(content="Explain LangGraph like I am a beginner.")]},
        config=config,
    )
    second_turn = app.invoke(
        {"messages": [HumanMessage(content="Now give me one very small example.")]},
        config=config,
    )

    print("First answer:")
    print(first_turn["messages"][-1].content)
    print("\nSecond answer:")
    print(second_turn["messages"][-1].content)