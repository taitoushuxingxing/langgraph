# LangGraph 练习题与参考答案

这份练习题按仓库里的 9 个示例顺序设计。
建议你每看完一个文件，就先自己做题，再看参考答案。

更推荐的做法是：

1. 先独立回答“概念题”。
2. 再自己改代码做“动手题”。
3. 最后再对照参考答案。

---

## 1. examples/01_linear_graph.py

### 练习题

1. 这个文件里的 state 包含哪三个字段？
2. `normalize_question` 节点做了什么？
3. 为什么 `answer_question` 能读取 `normalized_question`？
4. 这个图的执行顺序是什么？
5. 动手题：给 state 增加一个 `question_length` 字段，并在结果中打印出来。

### 参考答案

1. `question`、`normalized_question`、`answer`。
2. 它把输入问题去掉前后空格并转成小写，然后返回更新后的 `normalized_question`。
3. 因为 LangGraph 会把前一个节点返回的字段合并回共享 state，后面的节点就能继续读取。
4. `START -> normalize_question -> answer_question -> END`。
5. 一种参考改法：

```python
class QAState(TypedDict):
    question: str
    normalized_question: str
    question_length: int
    answer: str


def normalize_question(state: QAState) -> dict:
    normalized = state["question"].strip().lower()
    return {
        "normalized_question": normalized,
        "question_length": len(normalized),
    }
```

---

## 2. examples/02_conditional_router.py

### 练习题

1. `classify_intent` 和 `route_by_intent` 的职责有什么不同？
2. 为什么条件路由一般要先产出一个中间字段，比如 `intent`？
3. 如果输入是“how much does it cost”，会走哪个分支？
4. 动手题：增加 `shipping` 分支，支持识别物流问题。
5. 动手题：让 `general_node` 的回复更像客服，而不是占位语句。

### 参考答案

1. `classify_intent` 负责判断用户意图并把结果写入 state，`route_by_intent` 负责根据这个意图决定下一步去哪一个节点。
2. 因为分类和路由拆开之后结构更清楚，后续更容易扩展、调试和替换。
3. 会走 `pricing_node`，因为 `cost` 会被识别成 `pricing`。
4. 一种参考改法：

```python
def classify_intent(state: SupportState) -> dict:
    text = state["user_text"].lower()

    if "price" in text or "cost" in text:
        intent = "pricing"
    elif "refund" in text or "return" in text:
        intent = "refund"
    elif "shipping" in text or "delivery" in text:
        intent = "shipping"
    else:
        intent = "general"

    return {"intent": intent}
```

还需要同步增加 `shipping_node` 和对应路由映射。

5. 比如可以改成：`How can I help with your general question today?`

---

## 3. examples/03_loop_until_good.py

### 练习题

1. 为什么这个图不是一条直线，而是一个回环？
2. `review_score` 的作用是什么？
3. `revision_count` 的作用是什么？
4. 为什么要把“审稿”和“重写准备”拆成两个节点？
5. 动手题：把最大重试次数从 1 改成 2。

### 参考答案

1. 因为这个流程想模拟“先写草稿，再评审，不够好就继续修改”的实际工作流。
2. 它是质量判断依据，决定图是结束还是继续进入下一轮。
3. 它是防止无限循环的保险机制。
4. 因为 review 负责判断，prepare_rewrite 负责推进重试计数，这样职责更明确。
5. 可以把：

```python
if state.get("revision_count", 0) >= 1:
    return "finish"
```

改成：

```python
if state.get("revision_count", 0) >= 2:
    return "finish"
```

---

## 4. examples/04_memory_with_messages.py

### 练习题

1. `MessagesState` 和前面自定义的 `TypedDict` state 有什么不同？
2. `MemorySaver` 的作用是什么？
3. 为什么第二次调用还能看到第一次的消息？
4. `thread_id` 改掉之后会发生什么？
5. 动手题：自己构造两组不同的 `thread_id`，验证会话是否隔离。

### 参考答案

1. `MessagesState` 是 LangGraph 内置的一种消息状态结构，适合对话场景，核心字段是 `messages`。
2. 它会为同一个线程保存历史 state，让后续调用可以接上之前的上下文。
3. 因为两次调用使用了同一个 `thread_id`，所以 MemorySaver 会把它们串成同一条会话。
4. 如果改成新的 `thread_id`，那条会话会被当成全新线程，之前的消息不会自动带过来。
5. 你应该能观察到：相同 `thread_id` 共享历史，不同 `thread_id` 各自独立。

---

## 5. examples/05_tool_workflow.py

### 练习题

1. 这个文件里为什么需要 `selected_tool` 字段？
2. 为什么工具节点执行完以后，还要再经过 `finalize_answer`？
3. `choose_tool` 和 `route_tool` 分开写的好处是什么？
4. 如果问题里既出现数字又出现 refund，当前规则会怎样？
5. 动手题：增加一个 `shipping_policy` 工具分支。

### 参考答案

1. 因为图需要先记录“选了哪个工具”，这个中间决策既方便路由，也方便后续调试。
2. 因为工具结果往往偏原始，最终通常还需要一层整理，把它变成用户能直接读懂的答案。
3. 这样结构更清楚，以后更容易把规则决策替换成 LLM 决策。
4. 按当前代码顺序，可能会优先命中加法相关关键词，从而选择 `calculator`。
5. 一种思路：

```python
elif "shipping" in question or "delivery" in question:
    selected_tool = "shipping_policy"
```

然后增加：

```python
def shipping_policy_tool(state: ToolState) -> dict:
    return {"tool_result": "Shipping usually takes 3 to 5 business days."}
```

并把它接入路由与图构建。

---

## 6. examples/06_multi_role_workflow.py

### 练习题

1. planner、writer、reviewer 各自负责什么？
2. 为什么 reviewer 不直接去修改 draft？
3. `approved` 和 `revision_count` 是怎么共同控制流程结束的？
4. 这个例子为什么说是“多角色工作流”，但还不是复杂多 agent 系统？
5. 动手题：增加一个 `publisher` 节点，只在通过审核后执行。

### 参考答案

1. planner 负责出结构，writer 负责写内容，reviewer 负责检查质量。
2. 因为 reviewer 的职责是判断和反馈，不是直接改写内容，这样节点分工更清楚。
3. `approved=True` 时可以直接结束，没通过时会看 `revision_count` 是否超过上限，超过也会终止，避免无限循环。
4. 因为它本质上还是一个共享 state 的工作流拆分，还没有涉及更独立的 agent 记忆、通信和工具自治。
5. 一个参考结构是：`reviewer -> publisher -> END`，但前提是 reviewer 返回 `finish` 时不要直接去 END，而是先去 `publisher`。

---

## 7. advanced/07_real_llm_chatbot.py

### 练习题

1. 这个文件和 `examples/04_memory_with_messages.py` 最大的区别是什么？
2. `get_model` 为什么要单独写成函数？
3. `SystemMessage` 在这里起什么作用？
4. 这个文件说明 LangGraph 和大模型调用分别负责什么？
5. 动手题：把系统提示词改成“回答不要超过三句话”。

### 参考答案

1. 最大区别是：基础版用固定规则生成回复，这个版本在节点内部调用了真实 LLM。
2. 因为模型初始化集中管理后，未来改模型名、改 provider、改参数都会更方便。
3. 它用来设定模型的身份和回答风格，比如这里要求模型用适合初学者的方式解释。
4. LangGraph 负责流程编排和状态流动，ChatOpenAI 负责真正生成自然语言内容。
5. 参考改法：

```python
system_message = SystemMessage(
    content="You are a patient tutor. Answer in no more than three sentences."
)
```

---

## 8. advanced/08_real_llm_tools.py

### 练习题

1. `ToolDecision` 这个模型类的作用是什么？
2. 为什么这里用 `with_structured_output(...)` 而不是让模型随便输出文本？
3. 这个文件里哪些部分是“LLM 决策”，哪些部分是“工具执行”？
4. 为什么最终还要经过 `final_answer_with_llm`？
5. 动手题：增加一个假的 `weather_tool` 分支。

### 参考答案

1. 它定义了模型必须返回的结构，包括 `tool_name` 和 `tool_input`，避免模型乱输出。
2. 因为结构化输出更稳定，后续路由和工具执行更容易写，也更容易做校验。
3. `choose_tool_with_llm` 是决策，`run_calculator`、`run_faq_lookup`、`run_fallback` 是执行。
4. 因为工具结果通常比较原始，再让模型整理一次，用户体验会更好。
5. 一种参考结构：

```python
@tool
def weather_tool(city: str) -> str:
    return f"The fake weather for {city} is sunny."
```

同时还要扩展 `ToolDecision` 的枚举、路由映射、执行节点和图构建。

---

## 9. advanced/09_real_llm_multi_role.py

### 练习题

1. 这个文件里为什么 reviewer 用了结构化输出？
2. 为什么同一个模型可以扮演 planner、writer、reviewer 三个角色？
3. `revision_count` 在真实 LLM 场景下为什么更重要？
4. 这个例子最值得你学的，不是 prompt，而是什么？
5. 动手题：增加一个 `publisher` 节点，把通过审核的内容改成博客风格。

### 参考答案

1. 因为 reviewer 的输出需要稳定地控制流程，尤其是 `approved` 这种布尔值，用结构化输出会更可靠。
2. 因为角色本质上是不同 prompt 设定下的不同职责，不一定非要换不同模型。
3. 因为真实模型可能一直给出“不完美但也不完全失败”的结果，如果没有重试上限，就更容易出现无穷循环。
4. 最值得学的是流程拆分能力，也就是把规划、写作、审查、修改拆成稳定的图结构。
5. 一种思路是增加：`reviewer -> publisher -> END`，publisher 节点读取 `draft`，输出一个新的 `published_article` 字段。

---

## 综合练习

做完 9 个文件后，你可以尝试下面这 3 个综合练习。

### 综合练习 1

做一个“LangGraph 学习助手”图：

1. 用户提问后先分类。
2. 基础问题走知识解释分支。
3. 代码问题走示例推荐分支。
4. 最后统一整理成一段回复。

参考思路：
你可以把 `02_conditional_router.py` 的路由思路和 `05_tool_workflow.py` 的工具思路合起来。

### 综合练习 2

做一个“写文章并自检”的图：

1. planner 先出提纲。
2. writer 写初稿。
3. reviewer 判断是否适合小白。
4. 不通过就重写一次。

参考思路：
你可以把 `03_loop_until_good.py` 和 `06_multi_role_workflow.py` 的结构合起来。

### 综合练习 3

做一个“真实 LLM + 工具 + 记忆”的图：

1. 使用 `MessagesState` 保存对话。
2. 让模型选择工具。
3. 工具执行后总结答案。
4. 同一个线程内保留多轮上下文。

参考思路：
你可以把 `04_memory_with_messages.py` 和 `08_real_llm_tools.py` 组合起来。

---

## 最后建议

如果你发现自己一到 advanced 文件就开始混乱，通常不是模型太难，而是前面的“图思维”还不够稳。
你可以用一个简单标准检查自己有没有学懂：

1. 你能不能独立说清楚 state 里每个字段是干什么的。
2. 你能不能独立说清楚每个节点输入什么、输出什么。
3. 你能不能画出执行路径。
4. 你能不能自己加一个分支或一个节点。

如果这四件事你都能做出来，说明你已经不是完全小白了。