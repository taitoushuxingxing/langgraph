"""Advanced example 08: let a real LLM choose which tool the graph should call.

This is the natural upgrade path for example 05.
Instead of using fixed keyword rules, we ask the model to output a tool choice.
"""

import os
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.graph import END, START, StateGraph


class ToolDecision(BaseModel):
    tool_name: Literal["calculator", "faq_lookup", "fallback"] = Field(
        description="The tool that should handle the user request."
    )
    tool_input: str = Field(description="The exact input that should be passed to the tool.")


class ToolState(TypedDict):
    question: str
    tool_name: str
    tool_input: str
    tool_result: str
    final_answer: str


@tool
def calculator_tool(expression: str) -> str:
    """Add integer numbers found in the expression."""
    numbers = [int(token) for token in expression.split() if token.isdigit()]
    return f"Total = {sum(numbers)}"


@tool
def faq_lookup_tool(question: str) -> str:
    """Return a small policy answer from a fake FAQ source."""
    if "refund" in question.lower():
        return "Refunds are available within 7 days with proof of purchase."
    return "The FAQ source has no exact match, so ask a human for confirmation."


@tool
def fallback_tool(question: str) -> str:
    """Handle requests that do not fit any specific tool."""
    return f"No special tool matched: {question}"


def get_model() -> ChatOpenAI:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    return ChatOpenAI(model=model_name, temperature=0)


def choose_tool_with_llm(state: ToolState) -> dict:
    model = get_model().with_structured_output(ToolDecision)
    decision = model.invoke(
        [
            SystemMessage(
                content=(
                    "Choose one tool for the user's question. "
                    "Use calculator for arithmetic, faq_lookup for policy questions, "
                    "and fallback for everything else."
                )
            ),
            HumanMessage(content=state["question"]),
        ]
    )
    return {"tool_name": decision.tool_name, "tool_input": decision.tool_input}


def route_tool(state: ToolState) -> Literal["run_calculator", "run_faq_lookup", "run_fallback"]:
    mapping = {
        "calculator": "run_calculator",
        "faq_lookup": "run_faq_lookup",
        "fallback": "run_fallback",
    }
    return mapping[state["tool_name"]]


def run_calculator(state: ToolState) -> dict:
    return {"tool_result": calculator_tool.invoke(state["tool_input"])}


def run_faq_lookup(state: ToolState) -> dict:
    return {"tool_result": faq_lookup_tool.invoke(state["tool_input"])}


def run_fallback(state: ToolState) -> dict:
    return {"tool_result": fallback_tool.invoke(state["tool_input"])}


def final_answer_with_llm(state: ToolState) -> dict:
    model = get_model()
    response = model.invoke(
        [
            SystemMessage(
                content="Write a concise final answer for the user based on the tool result."
            ),
            HumanMessage(
                content=(
                    f"Question: {state['question']}\n"
                    f"Tool used: {state['tool_name']}\n"
                    f"Tool result: {state['tool_result']}"
                )
            ),
        ]
    )
    return {"final_answer": response.content}


def build_graph():
    graph = StateGraph(ToolState)

    graph.add_node("choose_tool_with_llm", choose_tool_with_llm)
    graph.add_node("run_calculator", run_calculator)
    graph.add_node("run_faq_lookup", run_faq_lookup)
    graph.add_node("run_fallback", run_fallback)
    graph.add_node("final_answer_with_llm", final_answer_with_llm)

    graph.add_edge(START, "choose_tool_with_llm")
    graph.add_conditional_edges("choose_tool_with_llm", route_tool)
    graph.add_edge("run_calculator", "final_answer_with_llm")
    graph.add_edge("run_faq_lookup", "final_answer_with_llm")
    graph.add_edge("run_fallback", "final_answer_with_llm")
    graph.add_edge("final_answer_with_llm", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    for question in [
        "Please add 18 and 24",
        "What is your refund policy?",
        "How should I start learning LangGraph?",
    ]:
        result = app.invoke(
            {
                "question": question,
                "tool_name": "",
                "tool_input": "",
                "tool_result": "",
                "final_answer": "",
            }
        )
        print("-" * 60)
        print("Question:", question)
        print("Tool:", result["tool_name"])
        print("Tool input:", result["tool_input"])
        print("Tool result:", result["tool_result"])
        print("Final answer:", result["final_answer"])