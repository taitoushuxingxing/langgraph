# LangGraph 中文学习笔记

这份笔记不是重复解释所有代码，而是帮你建立一个适合小白的阅读顺序。
每个文件都按同一个框架来学：

1. 先看这个文件解决什么问题。
2. 再看 state 里有哪些字段。
3. 再看 node 怎么改 state。
4. 最后看 graph 怎么把节点连起来。

---

## 1. examples/01_linear_graph.py

### 这一节学什么

这是最小 LangGraph。
你只需要先搞懂一件事：图本质上就是“状态流过多个节点”。

### 先看哪里

1. `QAState`
2. `normalize_question`
3. `answer_question`
4. `build_graph`
5. `app.invoke(...)`

### 你应该看懂什么

- `QAState` 规定图里会流动哪些数据。
- `normalize_question` 不会返回整个 state，只返回它修改的部分。
- `answer_question` 读取前一个节点写入的结果。
- 图的执行顺序是固定的：`START -> normalize_question -> answer_question -> END`。

### 运行后重点观察

- 输入问题有没有保留下来。
- `normalized_question` 是怎么被补进最终结果里的。
- `answer` 是怎么依赖 `normalized_question` 的。

### 这一节最容易卡住的点

很多初学者会以为每个节点都要返回完整 state。
其实不是。
LangGraph 会把节点返回的字典合并回共享状态。

### 建议你动手改什么

- 给 `QAState` 增加一个 `question_length` 字段。
- 在 `normalize_question` 里顺手把长度也算出来。
- 打印结果，看 state 是不是多了一项。

---

## 2. examples/02_conditional_router.py

### 这一节学什么

这一节的重点是“图不一定只有一条固定路线”。
LangGraph 可以先分类，再决定下一步走哪个节点。

### 先看哪里

1. `SupportState`
2. `classify_intent`
3. `route_by_intent`
4. `pricing_node`、`refund_node`、`general_node`
5. `graph.add_conditional_edges(...)`

### 你应该看懂什么

- `classify_intent` 负责把用户输入转成一个中间结果 `intent`。
- `route_by_intent` 不做业务处理，只做“下一步去哪”的决定。
- 三个分支节点各自代表一个处理路径。
- `add_conditional_edges` 是 LangGraph 分支能力的核心入口。

### 运行后重点观察

- 同样的图，为什么不同输入会走不同节点。
- `intent` 在最终输出里有没有留下来。
- route 函数返回的是节点名，不是普通文本。

### 这一节最容易卡住的点

很多人会把“分类逻辑”和“分支后的处理逻辑”写在一起。
这会让图越来越难维护。
比较好的做法就是像这个例子一样拆成两步：先分类，再路由。

### 建议你动手改什么

- 增加一个 `shipping` 意图。
- 新增 `shipping_node`。
- 把 `route_by_intent` 和 `build_graph` 一起补完整。

---

## 3. examples/03_loop_until_good.py

### 这一节学什么

这一节的重点是“图可以回环”。
不是所有工作流都是一次走到终点，有时需要写一版、审一版、不够好再重写。

### 先看哪里

1. `DraftState`
2. `write_draft`
3. `review_draft`
4. `decide_next_step`
5. `prepare_rewrite`
6. `graph.add_conditional_edges(...)`

### 你应该看懂什么

- `revision_count` 是防止死循环的重要字段。
- `review_score` 是决定要不要继续重写的依据。
- `decide_next_step` 就是循环控制器。
- 图结构不是线性的，而是会回到 `write_draft`。

### 运行后重点观察

- 第一次草稿为什么得分不高。
- 第二次草稿为什么能通过。
- 最终结果里 `revision_count` 有没有变化。

### 这一节最容易卡住的点

你可能会想，为什么不在 `review_draft` 里直接重写。
原因是职责分离。
review 节点只负责评估，rewrite 节点只负责修改，这样图会更清楚。

### 建议你动手改什么

- 把通过阈值从 8 改成 9。
- 或者把最大重试次数从 1 改成 2。
- 看图的运行次数会怎样变化。

---

## 4. examples/04_memory_with_messages.py

### 这一节学什么

这一节开始进入“多轮对话”。
重点不是模型聪明不聪明，而是图能不能记住前面的消息。

### 先看哪里

1. `MessagesState`
2. `chatbot`
3. `MemorySaver`
4. `config = {"configurable": {"thread_id": ...}}`
5. 两次 `app.invoke(...)`

### 你应该看懂什么

- `MessagesState` 是 LangGraph 对消息列表的一种常见 state 设计。
- `MemorySaver` 会按 `thread_id` 存储这条会话的历史。
- 第一次调用和第二次调用虽然是分开的，但因为 `thread_id` 一样，所以历史能串起来。

### 运行后重点观察

- 第二次调用时，图是否还能看到第一次的消息。
- 输出里的 `messages` 列表是不是逐渐变长。
- 如果改掉 `thread_id`，记忆是否会消失。

### 这一节最容易卡住的点

很多初学者以为 memory 是模型提供的。
其实这里的 memory 是图工作流层面的状态持久化，不是模型自己“记住”了什么。

### 建议你动手改什么

- 把 `demo-thread` 改成两个不同的值分别测试。
- 第一轮告诉系统一个名字，第二轮换个问题去问。
- 对比同线程和不同线程的输出差异。

---

## 5. examples/05_tool_workflow.py

### 这一节学什么

这一节是工具工作流的最小版本。
核心思路是：先决定该用哪个工具，再调用工具，最后整理答案。

### 先看哪里

1. `ToolState`
2. `choose_tool`
3. `route_tool`
4. 三个工具节点
5. `finalize_answer`

### 你应该看懂什么

- 工具工作流通常不是“模型直接回答”，而是“模型或规则先决定工具，再把工具结果整合回答案”。
- `selected_tool` 是中间决策结果。
- 每个工具节点都只处理自己的职责。
- `finalize_answer` 用来把流程结果变成用户能读懂的话。

### 运行后重点观察

- 不同问题会选中哪个工具。
- 为什么工具节点之后还要再经过一个总结节点。
- 最终输出里是否同时保留了路由结果和工具结果。

### 这一节最容易卡住的点

初学者常常会把“选工具”和“执行工具”写到同一个函数里。
短期看起来更省事，但后面一多就会乱。
拆开之后，你以后更容易把规则路由换成 LLM 路由。

### 建议你动手改什么

- 新增一个 `shipping_policy` 工具分支。
- 让 `choose_tool` 能识别物流相关问题。
- 再把总结节点的输出文案改得更自然一点。

---

## 6. examples/06_multi_role_workflow.py

### 这一节学什么

这一节让你理解“多角色协作”不等于“复杂 agent 系统”。
很多时候，它只是一个图里不同节点承担不同职责。

### 先看哪里

1. `TeamState`
2. `planner`
3. `writer`
4. `reviewer`
5. `decide_after_review`
6. `revise`

### 你应该看懂什么

- planner 负责想结构。
- writer 负责生成内容。
- reviewer 负责判断质量。
- revise 负责推动进入下一轮。
- 这些角色共享同一份 state，而不是各自维护一套独立数据。

### 运行后重点观察

- 第一版草稿为什么不过。
- 第二版是怎么被批准的。
- `approved` 和 `revision_count` 是怎么共同控制流程结束的。

### 这一节最容易卡住的点

你可能会觉得这些节点看起来像不同 agent。
但本质上，它们现在还只是不同职责的节点。
真正复杂的多 agent，还会涉及更独立的目标、记忆、工具和通信机制。

### 建议你动手改什么

- 加一个 `publisher` 节点。
- 只有 review 通过后才进入 publisher。
- publisher 负责给最终文案加一个简短标题。

---

## 7. advanced/07_real_llm_chatbot.py

### 这一节学什么

这是从基础版记忆聊天过渡到真实 LLM 的第一步。
图结构几乎没变，变的是节点内部不再写死回复，而是调用模型。

### 先看哪里

1. `get_model`
2. `llm_chatbot`
3. `SystemMessage`
4. `MemorySaver`
5. 两次 `invoke`

### 你应该看懂什么

- `get_model` 把模型初始化收口，后面换 provider 会方便很多。
- `SystemMessage` 用来给模型设定角色。
- `state["messages"]` 会把之前对话一起交给模型。
- 图结构不变，但节点实现从规则变成了 LLM 调用。

### 运行后重点观察

- 第二轮回答是否延续了第一轮上下文。
- 改系统提示词后，回答风格会不会变化。
- 同样的图结构，换成真实模型后能力增强在哪里。

### 这一节最容易卡住的点

不要把 LangGraph 和大模型调用混为一谈。
LangGraph 管的是流程，ChatOpenAI 管的是模型调用。
这个文件的意义就是让你看清这两层的边界。

### 建议你动手改什么

- 把 system prompt 改成“只用三句话回答”。
- 把温度调高一点，看输出有没有变化。
- 再对比它和 `examples/04_memory_with_messages.py` 的差别。

---

## 8. advanced/08_real_llm_tools.py

### 这一节学什么

这一节是把基础版工具路由升级成“让 LLM 做决策”。
关键点不只是调用模型，而是让模型输出结构化结果。

### 先看哪里

1. `ToolDecision`
2. `choose_tool_with_llm`
3. `route_tool`
4. 各个 `run_*` 节点
5. `final_answer_with_llm`

### 你应该看懂什么

- `ToolDecision` 定义了模型必须输出的结构。
- `with_structured_output(...)` 可以约束模型返回结构化数据。
- LLM 负责决策，不一定负责直接执行工具。
- 工具执行完以后，还可以再用模型做一次结果整理。

### 运行后重点观察

- 模型选出的 `tool_name` 是不是符合预期。
- `tool_input` 是否被单独抽取出来。
- 为什么最终答案不是工具原始输出，而是再过一层总结。

### 这一节最容易卡住的点

很多人第一次做工具调用时，会让模型自己把工具结果和最终答案混着返回。
这样很快会失控。
这里更稳妥的做法是分三段：决策、执行、总结。

### 建议你动手改什么

- 再新增一个 `weather` 或 `search` 风格的伪工具。
- 扩展 `ToolDecision` 的枚举值。
- 观察图结构几乎不用大改，只是多了一个分支。

---

## 9. advanced/09_real_llm_multi_role.py

### 这一节学什么

这是“真实 LLM 多角色工作流”的最小版。
你会看到一个模型通过不同 prompt，分别扮演 planner、writer、reviewer。

### 先看哪里

1. `ReviewResult`
2. `planner`
3. `writer`
4. `reviewer`
5. `decide_after_review`
6. `revise`

### 你应该看懂什么

- 不同角色不一定要不同模型，很多时候是同一个模型配不同系统提示词。
- reviewer 用结构化输出返回 `approved` 和 `feedback`，这样流程更稳定。
- 写作和审稿之间的循环，是 LangGraph 非常典型的应用模式。

### 运行后重点观察

- `outline` 怎样影响 `draft`。
- 审稿反馈怎样进入下一次写作。
- 为什么这里要限制 `revision_count`，而不是无限改下去。

### 这一节最容易卡住的点

你可能会误以为“多角色”就是更高级的 prompt engineering。
其实更重要的是流程拆分。
如果拆分合理，就算未来换模型，图结构也能保留。

### 建议你动手改什么

- 增加一个 `teacher_review` 节点，专门检查是不是适合初学者。
- 或者增加 `publisher` 节点，把通过审稿的内容改写成博客格式。
- 这样你会更清楚 LangGraph 擅长的是工作流编排，而不是单点生成。

---

## 最后给你的学习建议

如果你真的是小白，不要一开始就追求“做出一个超级 agent”。
你先按下面顺序吃透：

1. `01` 和 `02`，先理解图是什么。
2. `03` 和 `04`，理解循环和记忆。
3. `05` 和 `06`，理解工具和角色拆分。
4. `07` 到 `09`，再理解真实 LLM 只是替换节点能力，不是替换图本身。

一句话总结：
先学流程，再学模型接入；先学节点协作，再学 agent。