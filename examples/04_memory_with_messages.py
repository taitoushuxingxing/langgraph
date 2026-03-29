"""Beginner example 04: message memory across multiple turns.

This is the first example where the graph remembers earlier conversation.
The important pieces are MessagesState, MemorySaver, and thread_id.
"""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph


def chatbot(state: MessagesState) -> dict:
    # MessagesState stores a list of chat messages under state["messages"].
    last_message = state["messages"][-1]
    reply = AIMessage(
        content=(
            "I remember this thread. "
            f"Your latest message was: {last_message.content}"
        )
    )
    return {"messages": [reply]}


def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("chatbot", chatbot)
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)

    # MemorySaver keeps previous state for the same thread_id.
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


if __name__ == "__main__":
    app = build_graph()
    # Same thread_id means the second call can see the first call history.
    config = {"configurable": {"thread_id": "demo-thread"}}

    first_turn = app.invoke(
        {"messages": [HumanMessage(content="My name is Alice.")]},
        config=config,
    )
    second_turn = app.invoke(
        {"messages": [HumanMessage(content="What is my name?")]},
        config=config,
    )

    print("First turn messages:")
    for message in first_turn["messages"]:
        print(type(message).__name__, ":", message.content)

    print("\nSecond turn messages:")
    for message in second_turn["messages"]:
        print(type(message).__name__, ":", message.content)