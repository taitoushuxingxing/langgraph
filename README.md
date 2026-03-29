# LangGraph Zero-to-One Roadmap

This repository is organized for a complete beginner.
You do not need an API key to understand the first several examples.
The goal is to learn LangGraph in layers instead of jumping straight into agents.

This repository now has two parallel tracks:

1. Beginner track: understand graph structure without relying on a real LLM.
2. Advanced track: replace fixed rules with a real LLM after the basics are clear.

## 1. What to learn first

If you are new, do not start with a multi-agent demo.
Start with these concepts in order:

1. State: what data moves through the graph.
2. Node: one step that reads state and returns updates.
3. Edge: how execution moves from one node to another.
4. Router: how the graph chooses different paths.
5. Loop: how the graph retries or improves an answer.
6. Memory: how a graph remembers past messages.
7. Tool workflow: how a graph calls external capabilities.
8. Multi-role design: how planner, writer, and reviewer cooperate.

## 2. Recommended learning order

Read and run the examples in this order:

1. `examples/01_linear_graph.py`
	Learn the minimum LangGraph structure: state, node, edge, compile, invoke.
2. `examples/02_conditional_router.py`
	Learn conditional routing and intent-based branching.
3. `examples/03_loop_until_good.py`
	Learn cycles, review logic, and stopping conditions.
4. `examples/04_memory_with_messages.py`
	Learn message state and thread memory.
5. `examples/05_tool_workflow.py`
	Learn how a graph can choose and call different tools.
6. `examples/06_multi_role_workflow.py`
	Learn how to model a simple multi-role workflow before real multi-agent systems.
7. `advanced/07_real_llm_chatbot.py`
	Learn how to replace a fake responder with a real chat model and memory.
8. `advanced/08_real_llm_tools.py`
	Learn how to use a real LLM to decide which tool should be called.
9. `advanced/09_real_llm_multi_role.py`
	Learn how planner, writer, and reviewer can be powered by a real model.

Chinese study notes:

- `docs/langgraph-study-notes-zh.md`
  A beginner-friendly walkthrough for all 9 files, including what to read, what to observe, and what to modify.
- `docs/langgraph-exercises-zh.md`
	Progressive exercises and reference answers for all 9 files.

## 3. Suggested study plan for a beginner

### Stage 1: Understand the graph shape

Target files:

- `examples/01_linear_graph.py`
- `examples/02_conditional_router.py`

Focus on these questions:

- What does the state contain?
- What does each node return?
- Which edge is fixed, and which edge is conditional?
- Where does the graph start and end?

### Stage 2: Understand control flow

Target file:

- `examples/03_loop_until_good.py`

Focus on these questions:

- Why does the graph go back to an earlier node?
- What condition stops the loop?
- How do retries change the state?

### Stage 3: Understand conversation memory

Target file:

- `examples/04_memory_with_messages.py`

Focus on these questions:

- Why is `thread_id` important?
- What is stored in `messages`?
- What changes between the first and second invoke?

### Stage 4: Understand tools and workflows

Target files:

- `examples/05_tool_workflow.py`
- `examples/06_multi_role_workflow.py`

Focus on these questions:

- How does the graph decide which tool to use?
- Why split planner, writer, and reviewer into separate nodes?
- Which parts can later be replaced by a real LLM?

## 4. How to read each example

For every file, use the same reading order:

1. Read the state definition first.
2. Read all node functions.
3. Read the router function if there is one.
4. Read the graph construction section.
5. Read the sample invocation at the bottom.
6. Change one rule and rerun.

## 5. Beginner exercises

After you finish each stage, do one small change:

1. In `01`, add one more field into the state.
2. In `02`, add a new intent such as `shipping`.
3. In `03`, change the review score rule.
4. In `04`, try a different `thread_id` and compare results.
5. In `05`, add one new tool branch.
6. In `06`, add a final `publisher` node.

## 6. What comes after these examples

After you understand this repository, your next step is:

1. Replace deterministic rules with a real LLM.
2. Replace fake tools with real APIs or databases.
3. Add persistence for longer workflows.
4. Add streaming, interrupts, and human-in-the-loop review.
5. Build a real agent system only after the above is clear.

## 7. Advanced track after the beginner track

When you finish `examples/01` to `examples/06`, continue with the real LLM files.

### `advanced/07_real_llm_chatbot.py`

What you will learn:

- how a node calls a real chat model
- how `MessagesState` works with real messages
- how memory is kept by `thread_id`

### `advanced/08_real_llm_tools.py`

What you will learn:

- how an LLM can output a structured tool decision
- how a graph routes to different tool nodes
- how tool results are merged back into a final answer

### `advanced/09_real_llm_multi_role.py`

What you will learn:

- how one model can play different roles with different prompts
- how review feedback creates a loop
- how to stop a graph when quality is good enough

## 8. How to study as a beginner

Use this rhythm for each file:

1. Read the top comment first.
2. Find the state definition.
3. Read each node from top to bottom.
4. Look at the graph edges last.
5. Run the file and compare input and output.
6. Change one condition and observe the effect.

## 9. Dependency note

- Beginner examples mainly need `langgraph` and `langchain-core`.
- Advanced examples additionally use `langchain-openai` and `pydantic`.
- See `requirements.txt` for a compact dependency list.

## 10. Notes

- These examples focus on learning structure, not fancy prompts.
- Most examples avoid external services so you can focus on LangGraph itself.
- You said you do not need environment setup, so this repository only provides the learning path and code.