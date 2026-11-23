"""《从零手写 AI Agent》课程第 6-10 课种子数据：Agent 核心 ReAct 循环与终止条件、实用工具集、短期记忆、长期记忆、RAG 检索增强。"""

ARTICLES_B = [
    {
        "title": "第 6 课 · Agent 核心：ReAct 循环与终止条件",
        "summary": "三块积木合体成 Agent.run()：ReAct 循环让模型自主决定何时调工具、何时收工，max_steps 双刹车防失控，verbose 轨迹看清每步思考、行动与观察。",
        "difficulty": 2,
        "tags": ["Agent开发", "ReAct", "核心循环"],
        "duration_minutes": 22,
        "content": r"""## 🎯 本课目标

- 说清 ReAct = Reason + Act：思考、行动、观察三步如何循环出 Agent 的「自主性」
- 写出 agent_core.py：DEFAULT_SYSTEM_PROMPT 与 Agent 类，run() 一个方法跑通完整循环
- 装好两把刹车：max_steps 步数上限与「不再请求工具即终止」的统一出口
- 能读懂 verbose 轨迹，看得出 Agent 卡在哪一步、烧在哪个工具上

## 📦 本课产出

| 产出 | 说明 | 备注 |
|------|------|------|
| agent_core.py | Agent 类：ReAct 循环 + 终止条件 | 后续 9 课的引擎，接口今日锁定 |
| demo_agent.py | 第一个真正意义的 Agent 演示 | 一个需要工具的问题 + 一个不需要的 |
| 看轨迹的能力 | verbose 逐步打印思考/行动/观察 | 调试 Agent 的眼睛，日后排查全靠它 |

## 🔗 承接上一步

第 5 课的 ToolBox 把「注册工具」变成了贴标签：get_schemas() 一键导出 OpenAI tools 格式，execute() 按名执行且异常自动回传给模型。加上第 2 课的 LLMClient（重试与 token 记账）和第 4 课摸清的消息回传规则，积木齐了。

但第 4 课那个循环是为单个工具手写的死流程：schema 抄一遍、路由 if/elif 写一遍，调完一次就结束。本课把散件组装成通用的 Agent 类：

| 维度 | 第 4 课手工循环 | 第 6 课 Agent |
|------|----------------|---------------|
| 工具数量 | 单个，写死在代码里 | 任意 ToolBox，随插随用 |
| 决策权 | 代码写死调哪个工具 | 模型每轮自己决定调不调、调哪个 |
| 迭代能力 | 调一次就结束 | 观察结果后再行动，可多轮推进 |
| 步数上限 | 无 | max_steps 兜底，防失控烧钱 |
| 终止条件 | 手工判断 finish_reason | 统一出口：无 tool_calls 即收工 |

## 📖 概念讲解

### ReAct：让「想」与「做」交替进行

ReAct = Reasoning + Acting，2022 年由普林斯顿团队提出，如今几乎所有 Agent 框架的内核都是它。核心思想一句话：模型每轮先思考（Reason）要不要行动，行动（Act）后观察（Observe）结果，再进入下一轮思考——直到它认为可以给出最终答案。

```text
用户问题
   │
   ▼
┌────────────────┐
│ 🤔 Reason 思考  │  模型读全部历史，决定：调工具？还是直接回答？
└───────┬────────┘
        │ 响应里有 tool_calls 吗？
   ┌────┴─────┐
   有│          │没有
   ▼          ▼
┌─────────┐  ┌────────────┐
│ 🔧 Act   │  │ ✅ 最终回答  │ ──► 正常终止
│ 执行工具  │  └────────────┘
└────┬────┘
     ▼
┌─────────┐
│ 👁 观察   │  工具结果以 role=tool 写回历史
└────┬────┘
     │ 步数 +1；若已到 max_steps ──► 强制终止
     └────────► 回到 Reason
```

这张图里藏着一个反直觉的事实：**模型自己不会「循环」**。所谓 ReAct 循环，是我们的 for 循环在反复调用模型——模型每一轮只做一次决策，循环感完全是客户端代码制造出来的。理解了这一点，再看任何 Agent 框架都没有魔法。

### 终止条件：Agent 的安全带

一次 Agent 任务可能跑几十步，每一步都是真金白银。如果模型陷入「反复调用同一工具」的死胡同，没有刹车的循环会一直烧下去。所以两把刹车必须同时装：

| 刹车 | 触发条件 | 动作 |
|------|----------|------|
| 正常出口 | 本轮响应没有 tool_calls | 记下 msg.content，break 返回 |
| 强制出口 | for 循环走满 max_steps | 返回兜底话术，提示拆小问题 |

max_steps 取多大？经验值：简单问答 3~5 步足够，多工具协作 8~15 步。太小任务做不完，太大失控成本高。本课默认 8。

### DEFAULT_SYSTEM_PROMPT：行为约束写在开头

Agent 的系统提示词要提前立好三条规矩：先思考再行动、依据工具真实结果作答、结果不足时如实说明。这是反幻觉的第一道防线，全课程沿用。

## 🛠 分步实现

### Step 1：agent_core.py——骨架与构造函数

```python
# agent_core.py：Agent 内核——ReAct 循环与终止条件
from llm_client import LLMClient
from toolbox import ToolBox

# 系统提示词：给 Agent 立好「先思考、用真结果、不编造」的规矩
DEFAULT_SYSTEM_PROMPT = (
    "你是一个能使用工具的智能助手。回答问题前先思考：是否需要调用工具获取事实？"
    "需要时调用工具，并根据工具返回的真实结果作答；"
    "工具结果不足或失败时，如实说明，不要编造。"
)


class Agent:
    '''最小可用 Agent：ReAct 循环 + 步数上限 + 统一终止条件。'''

    def __init__(self, llm: LLMClient,
                 toolbox: ToolBox | None = None,
                 system_prompt: str = DEFAULT_SYSTEM_PROMPT,
                 max_steps: int = 8):
        self.llm = llm                    # 统一的大模型客户端（第 2 课）
        self.toolbox = toolbox            # 工具箱（第 5 课），可为空：纯聊天模式
        self.system_prompt = system_prompt
        self.max_steps = max_steps        # 强制终止的最大步数
```

两个设计要点：其一，toolbox 允许为 None——没有工具时 Agent 退化为普通对话机器人，tools 参数自然不传；其二，ToolBox | None 是 Python 3.10+ 的联合类型写法，与本课程的环境要求一致。

### Step 2：run()——整个课程的心脏

```python
    def run(self, question: str, verbose: bool = True) -> str:
        # 1) 拼初始消息：system 在前，user 在后
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question},
        ]
        # 工具 schema 只需导出一次；没有工具箱就不传 tools
        tools = self.toolbox.get_schemas() if self.toolbox else None

        final = None
        # 2) ReAct 主循环：步数从 1 数到 max_steps
        for step in range(1, self.max_steps + 1):
            resp = self.llm.chat(messages, tools=tools)
            msg = resp.choices[0].message

            if msg.tool_calls:
                if verbose:
                    print(f"\n🤔 第 {step} 步：模型决定调用 {len(msg.tool_calls)} 个工具")
                # 关键一步：把带 tool_calls 的 assistant 消息原样写回历史
                # 少了它，下一轮请求会因 tool 消息失去配对对象而报 400
                messages.append(msg.model_dump())

                # 3) 逐个执行模型点名的工具
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = tc.function.arguments      # 注意：这是 JSON 字符串
                    if verbose:
                        print(f"🔧 调用 {name}({args})")
                    result = self.toolbox.execute(name, args)
                    if verbose:
                        preview = result[:80] + ("…" if len(result) > 80 else "")
                        print(f"👁 结果: {preview}")
                    # 工具结果按协议配对写回：tool_call_id 必须对应
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": name,
                        "content": result,
                    })
                # 执行完回到循环顶部：观察结果喂给模型，进入下一轮思考
            else:
                # 4) 本轮没有 tool_calls：模型给出最终回答，正常终止
                final = msg.content
                if verbose:
                    print(f"\n✅ 第 {step} 步：模型给出最终回答")
                break

        # 5) 强制出口：步数耗尽还没拿到最终回答
        if final is None:
            final = "已达最大步数仍未得出答案，请尝试拆小问题"
        return final
```

逐段看：messages 初值是 system + user 两条；每轮 llm.chat 把当前全部历史发给模型。响应里 msg.tool_calls 存在说明模型想用工具——先用 model_dump() 把这条 assistant 消息原样写回历史（协议要求 assistant 的 tool_calls 与随后的 tool 消息一一配对），再逐个执行工具、把结果以 role=tool 写回。下一轮模型看到工具结果，要么继续调工具（多步任务），要么给出最终回答（无 tool_calls，break）。两种出口全覆盖：break 是正常终止；循环自然走完则 final 仍为 None，返回兜底话术。

verbose 的三个表情正好对应 ReAct 三步：🤔 思考（决定调几个工具）、🔧 行动（工具名 + 参数）、👁 观察（结果前 80 字预览）。

### Step 3：demo_agent.py——见证第一个 Agent

```python
# demo_agent.py：第一个真正意义的 Agent
from agent_core import Agent
from llm_client import LLMClient
from toolbox import tool, ToolBox

llm = LLMClient()          # 重试与 token 记账都由它管
box = ToolBox()


@tool(description="把输入原样返回，仅用于演示工具调用流程")
def simple_echo(text: str):
    '''把输入原样返回'''
    return f"echo: {text}"


@tool(description="查询指定城市的当前时间（演示用假数据）")
def get_city_time(city: str):
    '''查询指定城市的当前时间'''
    # 假数据源：真实场景这里会调用时间 API
    fake_db = {
        "北京": "2026-11-01 09:00:00",
        "东京": "2026-11-01 10:00:00",
        "巴黎": "2026-11-01 02:00:00",
    }
    return fake_db.get(city, f"暂无 {city} 的时区数据")


box.register(simple_echo)
box.register(get_city_time)

agent = Agent(llm, box)

# 问题 1：时间信息模型不可能知道，必须调工具
print("=" * 60)
print("问题 1：现在东京和巴黎各是几点？")
answer = agent.run("现在东京和巴黎各是几点？")
print("最终回答:", answer)

# 问题 2：常识问题，模型应直接回答，一次工具都不调
print("=" * 60)
print("问题 2：用一句话解释什么是光合作用")
answer = agent.run("用一句话解释什么是光合作用")
print("最终回答:", answer)

print("=" * 60)
print("本次累计 token:", llm.total_tokens)
```

两个问题各有用意：问题 1 验证「会调工具」；问题 2 验证「知道不用调工具」——后者同样重要，一个见工具就乱调的 Agent 又慢又贵。

## ▶️ 运行效果

```text
$ python demo_agent.py
============================================================
问题 1：现在东京和巴黎各是几点？
🤔 第 1 步：模型决定调用 2 个工具
🔧 调用 get_city_time({"city": "东京"})
👁 结果: 2026-11-01 10:00:00
🔧 调用 get_city_time({"city": "巴黎"})
👁 结果: 2026-11-01 02:00:00

✅ 第 2 步：模型给出最终回答
最终回答: 现在东京是 10:00，巴黎是 02:00。

============================================================
问题 2：用一句话解释什么是光合作用

✅ 第 1 步：模型给出最终回答
最终回答: 光合作用是植物利用光能把二氧化碳和水转化为养分并释放氧气的过程。

============================================================
本次累计 token: 832
```

（输出因模型而异，字段结构一致。值得注意：deepseek-chat 在一轮里就返回了两个 tool_calls，所以第 1 步完成两次查询、第 2 步收工。）

## ⚠️ 常见坑

1. **max_steps 太小，任务做不完**。现象：复杂问题总返回兜底话术。原因：模型想先查 A 再查 B，还没走完就被掐断。解法：看 verbose 轨迹数一数实际需要几步，再把 max_steps 放宽一档；同时检查工具描述是否写清「一次能查什么」，减少无效轮次。

2. **没有终止条件，死循环烧钱**。现象：程序不结束，token 数一路狂飙。原因：只写了「调工具」分支而没有步数上限，模型陷入重复调用。解法：for + max_steps 是底线；生产环境再加两层——单次任务 token 预算（第 13 课护栏）、同一工具同参数连续调用检测。

3. **工具结果太大，撑爆上下文**。现象：多步之后请求报 400（消息过长）或费用陡增。原因：抓取类工具返回几万字，每轮全量重发。解法：写回历史前截断：

```python
MAX_TOOL_RESULT_CHARS = 2000

result = self.toolbox.execute(name, args)
if len(result) > MAX_TOOL_RESULT_CHARS:
    result = result[:MAX_TOOL_RESULT_CHARS] + f"…[已截断，原长 {len(result)} 字]"
```

4. **忘写 model_dump()，丢掉 tool_calls**。现象：第二轮请求报 400，提示 tool_calls 与 tool 消息不配对。原因：手动拼一条 {"role": "assistant"} 写回历史，tool_calls 字段丢了。解法：永远用 messages.append(msg.model_dump()) 原样写回——它是 pydantic 对象转 dict 的标准姿势，一字不差保留结构。

## ✍️ 课后练习

1. （易）注册一个 roll_dice(sides: int) 工具返回随机点数，问 Agent「掷一个 20 面骰」，对照 verbose 轨迹确认它调了工具。
2. （中）给 run() 加一个仅本次调用生效的覆盖参数：run(question, max_steps=3)，验证 max_steps=1 时问题 1 的兜底话术输出。
3. （难）把坑 3 的截断逻辑封装成 Agent 的方法 _clip(text)，并做实验：注册一个返回 5000 字假文本的工具，打印截断前后 llm.total_tokens 的差值。

## ⏭ 下一课预告

Agent 有了内核，手里却只有 echo 和假工具，像一台没装软件的电脑。第 7 课装上四件真家伙：ast 白名单安全计算器、当前时间、data 沙箱文件读写与网页抓取净化器，顺带演示 eval 计算器被一行字符串攻破的全过程。
""",
    },
    {
        "title": "第 7 课 · 实用工具集：计算器、时间、文件与网页抓取",
        "summary": "Agent 空有循环没有真工具等于空转。本课写四件套：ast 白名单安全计算器、时间、data 沙箱文件读写与网页抓取，现场演示 eval 被一行字符串攻破。",
        "difficulty": 2,
        "tags": ["Agent开发", "工具设计", "安全计算器", "网页抓取"],
        "duration_minutes": 25,
        "content": r"""## 🎯 本课目标

- 掌握工具设计三原则：单一职责、返回值可序列化、失败也要返回信息
- 写出 safe_calculator：ast 白名单求值，从语法树层面杜绝 eval 注入
- 写出时间、data 沙箱文件读写、网页抓取净化器，凑齐实用工具四件套
- 用 Agent 连跑四个真实问题，观察模型自己挑工具、自己纠错的全过程

## 📦 本课产出

| 产出 | 说明 | 备注 |
|------|------|------|
| tools_basic.py | 四件套工具，全部 @tool 注册 | 计算器 / 时间 / 文件 / 网页 |
| demo_tools.py | Agent 四连问演示 | 第一个能干真实活的 Agent |
| 一套安全意识 | 注入、越界、编码三大坑的防御 | 比代码本身更值钱 |

## 🔗 承接上一步

第 6 课的 Agent 已经会思考、会调工具，但 toolbox 里只有 simple_echo 和假数据 get_city_time——内核强了，四肢还是假的。本课给 ToolBox 装上第一批真工具。顺带一提：openai SDK 本身就依赖 httpx，装 openai 时它已经进环境了，本课网页抓取不用额外安装。

## 📖 概念讲解

### 工具设计三原则

给模型写的工具和人用的库函数不一样，三条铁律：

| 原则 | 为什么 | 反例 |
|------|--------|------|
| 单一职责 | 模型按描述选工具，大杂烩工具会让它选错 | do_everything(action, ...) |
| 返回值可序列化 | ToolBox.execute 要把结果转成字符串回传 | 返回打开的文件对象 |
| 失败也要返回信息 | 错误信息是模型自纠的原料 | 直接 raise，整个循环崩掉 |

第三条最反直觉：第 5 课的 execute 已把异常转成错误字符串——模型读到「ZeroDivisionError」会自动换写法重试，这就是自纠闭环。工具报错不是事故，是反馈。

### 安全计算器：为什么绝不能用 eval

模型传来的 expression 是纯字符串，最省事的实现是 eval(expression)。但模型可能被提示词注入（比如网页抓取的正文里藏了一句指令），也可能纯粹抽风，传进 __import__('os') 之类的代码——eval 会照单全收，任意执行。防御思路：不执行字符串，而是先用 ast.parse 解析成语法树，然后**只放行白名单节点**：

| AST 节点 | 对应语法 | 允许？ |
|----------|----------|--------|
| Constant（int/float） | 3、3.14 | ✅ |
| BinOp + Add/Sub/Mult/Div/Pow/Mod | a+b、a**b、a%b | ✅ |
| UnaryOp + UAdd/USub | -a、+a | ✅（括号在语法树里天然支持） |
| Name（变量名） | os | ❌ 拒绝 |
| Call（函数调用） | __import__('os') | ❌ 拒绝 |

不在白名单里的节点一律抛错——注入在语法树层面就被挡死。

### 文件沙箱：把读写能力关进 data 目录

给 Agent 文件读写，等于把仓库钥匙交给模型，必须圈地三步：所有路径拼上 ./data 前缀；os.path.realpath 解析出真实绝对路径（消解 ../ 这类花招）；校验真实路径必须位于 data 目录之内，否则拒绝。

### 网页抓取：HTML 不是给人看的

模型读不了原始 HTML——标签噪音远大于正文。净化三板斧：剥掉 script/style 块、剥掉所有标签、还原 HTML 实体（如 &amp;），最后压缩空白、截断 3000 字返回。

## 🛠 分步实现

### Step 1：tools_basic.py——安全计算器（本课最硬核的 20 行）

```python
# tools_basic.py：实用工具集四件套
import ast
import operator
import os
import re
import html as html_lib
from datetime import datetime

import httpx

from toolbox import tool

# ---------- 工具 1：安全计算器 ----------

# 白名单：运算符 AST 节点 -> 真正的运算函数
_BIN_OPS = {
    ast.Add: operator.add,       # +
    ast.Sub: operator.sub,       # -
    ast.Mult: operator.mul,      # *
    ast.Div: operator.truediv,   # /
    ast.Pow: operator.pow,       # **
    ast.Mod: operator.mod,       # %
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,      # +x
    ast.USub: operator.neg,      # -x
}


def _eval_node(node):
    # 递归求值：只允许数字、白名单运算符和括号通过
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):            # 数字常量（2、3.14）
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"不允许的常量类型：{type(node.value).__name__}")
    if isinstance(node, ast.BinOp):               # 双目运算：a op b
        op_type = type(node.op)
        if op_type not in _BIN_OPS:
            raise ValueError(f"不允许的运算符：{op_type.__name__}")
        return _BIN_OPS[op_type](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):             # 一元运算：-a、+a
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValueError(f"不允许的一元运算符：{op_type.__name__}")
        return _UNARY_OPS[op_type](_eval_node(node.operand))
    # Name（变量）、Call（函数调用）等一律拒绝——注入在这里被挡死
    raise ValueError(f"不允许的表达式节点：{type(node).__name__}")


@tool(description="安全的四则运算计算器，仅支持 + - * / ** % 和括号，expression 用字符串传入")
def safe_calculator(expression: str):
    '''计算一个数学表达式并返回结果'''
    try:
        tree = ast.parse(expression, mode="eval")   # 解析成 AST，绝不 eval
        result = _eval_node(tree)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return f"计算错误：{expression} 中除数为 0"
    except Exception as exc:
        return f"无法计算 {expression}：{type(exc).__name__}: {exc}"
```

_eval_node 是白名单思想的落地：四种节点类型逐个放行，落到最后的 raise 兜底——任何未知节点（变量名、函数调用、属性访问）都进不来。异常被 safe_calculator 捕获后转成说明文字返回，模型读到会自己改参数，这正是第 5 课说的自纠闭环。

### Step 2：当前时间工具

```python
# ---------- 工具 2：当前时间 ----------

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


@tool(description="获取当前日期时间，格式：YYYY-MM-DD HH:MM:SS 星期X")
def get_now_time() -> str:
    '''返回服务器当前时间'''
    now = datetime.now()
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} {WEEKDAYS[now.weekday()]}"
```

模型自己不知道「现在几点」——它没有时钟。这十行是 Agent 工具价值的最好注脚：把模型缺的事实喂给它。

### Step 3：文件读写（data 沙箱）

```python
# ---------- 工具 3：文件读写（./data 沙箱） ----------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _safe_path(filename: str) -> str:
    # 把任意传入的文件名限制在 data 目录内，防 ../ 越界
    full = os.path.realpath(os.path.join(DATA_DIR, filename))
    if not full.startswith(os.path.realpath(DATA_DIR) + os.sep):
        raise ValueError(f"非法路径：{filename}，只允许访问 data 目录")
    return full


@tool(description="读取 data 目录下的文本文件，filename 相对于 data 目录，如 note.txt")
def read_file(filename: str) -> str:
    '''读取指定文本文件的内容'''
    path = _safe_path(filename)
    if not os.path.exists(path):
        return f"文件 {filename} 不存在"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@tool(description="把内容写入 data 目录下的文本文件，返回写入字符数")
def write_file(filename: str, content: str) -> str:
    '''写入文本文件（自动创建目录）'''
    path = _safe_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已写入 {len(content)} 字符到 {filename}"
```

注意工具描述里明确写了「filename 相对于 data 目录」——模型对参数的理解完全来自描述与名字，描述写清楚能少一半纠错轮次。realpath 会把 note.txt 解析成绝对路径、把 ../secret.txt 解析到 data 之外，后者被 startswith 校验当场拦下。

### Step 4：网页抓取净化器

```python
# ---------- 工具 4：网页抓取（净化版） ----------


@tool(description="抓取网页 URL，去掉脚本与样式标签后返回纯文本正文，最多 3000 字")
def fetch_webpage(url: str) -> str:
    '''抓取网页并提取纯文本'''
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; AgentCourse/1.0)"}
        r = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        r.raise_for_status()                 # 4xx/5xx 直接抛异常
        if r.encoding is None:               # 响应头未声明编码时兜底 utf-8
            r.encoding = "utf-8"
        text = r.text
        # 净化三板斧：剥 script/style -> 剥所有标签 -> 还原 HTML 实体
        text = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html_lib.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:3000]
    except Exception as exc:
        # 失败也要返回信息：带上 URL 与原因，模型才能向用户解释清楚
        return f"抓取失败 {url}：{type(exc).__name__}: {exc}"
```

四个细节：User-Agent 别用默认值，不少站点会直接拒绝无 UA 的请求；timeout=10 防止挂死整个 Agent 循环；follow_redirects=True 处理 301/302；最后 3000 字截断呼应第 6 课「工具结果太大撑爆上下文」的坑。

### Step 5：demo_tools.py——Agent 四连问

```python
# demo_tools.py：给 Agent 装上四件真工具
from agent_core import Agent
from llm_client import LLMClient
from toolbox import ToolBox

from tools_basic import (
    safe_calculator, get_now_time, read_file, write_file, fetch_webpage,
)

llm = LLMClient()
box = ToolBox()
for t in (safe_calculator, get_now_time, read_file, write_file, fetch_webpage):
    box.register(t)

agent = Agent(llm, box)

questions = [
    "(128*46)/12 等于多少？",
    "现在是几点？星期几？",
    "帮我把会议纪要写进 data/note.txt，内容是：周三 15:00 项目评审会，3 楼会议室",
    "抓取 https://example.com 的正文，用一句话概括",
]

for i, q in enumerate(questions):
    print("=" * 60)
    print("问题:", q)
    # 第一个问题展示完整 ReAct 轨迹，其余只看最终回答
    print("回答:", agent.run(q, verbose=(i == 0)))
    print("累计 token:", llm.total_tokens)
```

## ▶️ 运行效果

```text
$ python demo_tools.py
============================================================
问题: (128*46)/12 等于多少？
🤔 第 1 步：模型决定调用 1 个工具
🔧 调用 safe_calculator({"expression": "(128*46)/12"})
👁 结果: (128*46)/12 = 490.6666666666667

✅ 第 2 步：模型给出最终回答
回答: (128*46)/12 ≈ 490.67。
累计 token: 415
============================================================
问题: 现在是几点？星期几？
回答: 现在是 2026-11-01 14:30:05，星期六。
累计 token: 671
============================================================
问题: 帮我把会议纪要写进 data/note.txt，内容是：周三 15:00 项目评审会，3 楼会议室
回答: 已完成，共写入 28 个字符到 data/note.txt。
累计 token: 1012
============================================================
问题: 抓取 https://example.com 的正文，用一句话概括
回答: 该页面是 IANA 保留的示例域名说明页，提示此域名用于文档示例。
累计 token: 1420
```

（输出因模型而异。`cat data/note.txt` 可以亲眼验证第三个问题真的落盘了。）

## ⚠️ 常见坑

1. **eval 计算器的注入风险**。现象：功能一样，但有人问「帮我执行 __import__('os')」时数据或命令就被带走/执行了。原因：eval 把字符串当代码。解法：ast 白名单（本课方案）。反面教材亲眼看看：

```python
# 危险的反面教材：千万别把这种实现交给 Agent
def evil_calculator(expression: str):
    return eval(expression)              # 字符串直接当代码执行！

# 模型（或被注入的指令）完全可能传进这样的表达式：
evil_calculator("__import__('os').listdir('.')")          # 目录被列出来
evil_calculator("__import__('os').system('touch pwned')") # 任意命令执行
```

2. **文件路径越界**。现象：模型传 note.txt 没事，传 ../settings.py 就读到了源码。原因：直接 open 拼接路径，没有归一化校验。解法：_safe_path 的 realpath + startswith 双保险，越界直接 ValueError，错误信息回传模型让它换路径。

3. **网页编码乱码**。现象：抓中文页面返回「æµ‹è¯•」这类乱码。原因：响应头没声明 charset，解码猜错。解法：r.encoding is None 时显式设为 utf-8 再取 r.text。

4. **URL 不可达时的异常文案**。现象：工具返回「Error」，模型对用户只会复读「出错了」。原因：异常信息没带上下文。解法：错误字符串里带上 URL 与异常类型（本课 fetch_webpage 的写法），模型就能告诉用户「该网址无法访问，原因是连接超时」。

## ✍️ 课后练习

1. （易）给 safe_calculator 扩展整除：在 _BIN_OPS 里加 ast.FloorDiv 对应 operator.floordiv，验证 7//2 = 3。
2. （中）给 read_file 加 max_chars: int = 5000 参数，超长截断并附「已截断」说明，防止大文件撑爆上下文。
3. （难）给 fetch_webpage 提取标题：先 re.search(r"<title>(.*?)</title>", text, re.I)，返回「标题：xxx\n正文：yyy」的结构，观察模型概括质量是否提升。

## ⏭ 下一课预告

工具多了，对话就长了：每轮全量重发历史，上下文窗口迟早被撑爆。第 8 课做短期记忆——上下文预算、滑动窗口与超阈值摘要压缩，让 20 轮长对话依然轻装上阵，且你的偏好不被丢掉。
""",
    },
    {
        "title": "第 8 课 · 短期记忆：上下文预算与对话压缩",
        "summary": "上下文窗口有限，长对话必然溢出。本课写 ShortTermMemory：滑动窗口保最新、超阈值才触发摘要压缩，20 轮长对话演示条数骤降，用户偏好不丢。",
        "difficulty": 2,
        "tags": ["Agent开发", "短期记忆", "上下文预算", "摘要压缩"],
        "duration_minutes": 20,
        "content": r"""## 🎯 本课目标

- 理解上下文窗口为什么是稀缺资源：每轮全量重发历史，越长越贵越慢
- 写出 est_tokens 极简估算与 ShortTermMemory：滑动窗口按预算裁剪
- 实现 maybe_summarize：超阈值才把老历史压成一条摘要（省钱开关）
- 跑通 20 轮长对话演示，亲眼看到摘要触发前后消息条数骤降、偏好不丢

## 📦 本课产出

| 产出 | 说明 | 备注 |
|------|------|------|
| memory_short.py | est_tokens + ShortTermMemory 类 | 窗口裁剪 + 摘要压缩双策略 |
| check_memory.py | 不调 LLM 的本地自检脚本 | 验证预算裁剪，零成本 |
| memory_demo.py | 短期记忆 + Agent 集成演示 | 20 轮长对话触发摘要 |

## 🔗 承接上一步

第 7 课之后，Agent 手里有四件真工具，能算、能看表、能读写文件、能抓网页——对话自然就越聊越长。但 Agent.run 每一轮都把全部历史重发给模型（第 3 课讲过：模型无状态，多轮全靠客户端重发），历史无限增长，窗口迟早爆。本课在 Agent 外面套一层记忆管理，不动 agent_core.py 一行代码。

## 📖 概念讲解

### 上下文窗口：Agent 的办公桌

窗口大小决定了模型一次「看得见」多少内容，各家差异巨大：

| 档位 | 典型窗口 | 粗略体感 |
|------|----------|----------|
| 入门档 | 8k tokens | 约 1 万多汉字，几轮长对话就紧张 |
| 主流档 | 32k~128k tokens | 日常够用，但 Agent 多步循环也吃紧 |
| 长文档 | 200k tokens | 一本小书，费用也按量上去了 |

三个压力随历史增长线性上升：费用（输入按 token 计价）、延迟（序列越长推理越慢）、风险（超过窗口直接 400 报错）。所以「记忆」不是可选项，是 Agent 工程的必修课。

### Token 粗估：est_tokens

课程采用极简口径：est_tokens(text) = len(text)。依据是中文大约 1 字折 1 token（实际常在 0.6 左右，所以按字符计偏保守），英文约 4 字符折 1 token。对中文偏保守意味着我们宁可早一点触发压缩也不撑爆窗口——粗估够用就好，不值得为精确引第三方库。

### 两种策略：滑动窗口 vs 摘要压缩

| 策略 | 做法 | 优点 | 代价 |
|------|------|------|------|
| 滑动窗口 | 从尾部往前装，预算装不下就丢最老 | 零额外调用、零延迟 | 最老的内容直接消失，早期约束会忘 |
| 摘要压缩 | 老历史请 LLM 压成一条摘要 | 保大意，可点名保留关键约束 | 多一次调用（花钱），摘要可能失真 |

本课两条都用，各有分工：get_messages() 做滑动窗口兜底（无论何时都不会超预算）；maybe_summarize() 在总 token 超阈值时才触发压缩——「超阈值才做」这个判断本身就是省钱开关。

### 摘要提示词必须点名「保留偏好」

普通摘要最容易丢的就是「我不吃榴莲」这类硬性约束，而它们恰恰是后续对话最需要的。所以压缩提示词里要显式要求：保留用户偏好与硬性要求。

## 🛠 分步实现

### Step 1：memory_short.py——估算与滑动窗口

```python
# memory_short.py：短期记忆——上下文预算与对话压缩


def est_tokens(text: str) -> int:
    # 极简口径：按字符数估算 token（对中文偏保守，够指导策略）
    return len(text)


class ShortTermMemory:
    '''短期记忆：带预算的消息列表，超预算可触发摘要压缩。'''

    def __init__(self, max_tokens: int = 6000):
        self.max_tokens = max_tokens
        self._messages = []               # 与 OpenAI 格式一致的字典列表

    def add(self, role: str, content: str):
        # 追加一条消息
        self._messages.append({"role": role, "content": content})

    def get_messages(self) -> list:
        # 滑动窗口：从尾部往前累计预算，装不下的最老消息不返回
        budget, kept = 0, []
        for msg in reversed(self._messages):
            cost = est_tokens(msg["content"])
            if budget + cost > self.max_tokens:
                break
            budget += cost
            kept.append(msg)
        kept.reverse()                    # 反着装进去的，正回来
        return kept

    def clear(self):
        self._messages = []
```

get_messages 是纯本地操作，不花一分钱：从最新消息倒着数，预算用完即止。注意它只是「视图」——_messages 原始数据还在，真正删数据的只有下面的 maybe_summarize。

### Step 2：maybe_summarize——超阈值才压缩

```python
    def maybe_summarize(self, llm, keep_last: int = 6) -> bool:
        # 总 token 超预算时：保留最近 keep_last 条，其余压成一条摘要
        total = sum(est_tokens(m["content"]) for m in self._messages)
        if total <= self.max_tokens:
            return False                  # 未超预算：什么都不做（省钱开关）
        if len(self._messages) <= keep_last:
            return False                  # 剩太少：摘要没有意义

        old = self._messages[:-keep_last]      # 要被压缩的老历史
        recent = self._messages[-keep_last:]   # 原样保留的最近几条

        transcript = "\n".join(
            f"[{m['role']}] {m['content']}" for m in old
        )
        # 摘要提示词：点名保留用户偏好与硬性要求
        prompt = (
            "把以下对话压缩成 200 字以内的要点备忘，"
            "必须保留用户偏好与硬性要求（如忌口、格式、限制、目标），"
            "只输出备忘本身：\n" + transcript
        )
        resp = llm.chat([{"role": "user", "content": prompt}], temperature=0.2)
        summary = resp.choices[0].message.content.strip()

        # 用一条摘要替换全部老历史，前缀 [历史摘要] 标明来源
        self._messages = [
            {"role": "system", "content": f"[历史摘要] {summary}"},
        ] + recent
        return True
```

三个分支各司其职：没超预算直接返回 False（这就是「每轮都摘要浪费钱」的解药）；消息太少摘要没意义；真正压缩时把老历史拼成文字稿，用 temperature=0.2 求稳定的要点输出。压缩后条数从几十条骤降到 keep_last + 1 条。

### Step 3：check_memory.py——先在本地验证，不花一分钱

```python
# check_memory.py：不调 LLM，纯本地验证滑动窗口
from memory_short import ShortTermMemory, est_tokens

mem = ShortTermMemory(max_tokens=100)
for i in range(1, 8):
    mem.add("user", f"第 {i} 条消息，长度 20 字符的一个句子示例。")

msgs = mem.get_messages()
print("原始条数:", len(mem._messages), "预算内保留:", len(msgs))
print("保留的第一条:", msgs[0]["content"])
print("估算 token:", sum(est_tokens(m["content"]) for m in msgs))
```

每条约 20 token、预算 100，恰好装下 5 条——最老 2 条被窗口丢掉。写记忆组件时先跑这种零成本自检，逻辑对了再接模型。

### Step 4：memory_demo.py——与 Agent 集成跑 20 轮

```python
# memory_demo.py：短期记忆 + Agent 的集成演示
from agent_core import Agent
from llm_client import LLMClient
from memory_short import ShortTermMemory, est_tokens

llm = LLMClient()
agent = Agent(llm, toolbox=None,
              system_prompt="你是一个长情陪练助手，记得住用户说过的偏好与要求。")
memory = ShortTermMemory(max_tokens=1500)   # 故意调小：20 轮内必然触发摘要


def run_with_memory(question: str) -> str:
    # 1) run 前：把记忆消息拼成上下文，随问题一起交给 Agent
    context = memory.get_messages()
    if context:
        lines = "\n".join(f"[{m['role']}] {m['content']}" for m in context)
        send = f"[此前对话记录]\n{lines}\n\n[当前问题]\n{question}"
    else:
        send = question
    answer = agent.run(send, verbose=False)
    # 2) 答后：本轮原始问答写回记忆（存原始版，避免上下文滚雪球）
    memory.add("user", question)
    memory.add("assistant", answer)
    # 3) 每轮检查：超预算才触发摘要
    compressed = memory.maybe_summarize(llm)
    total = sum(est_tokens(m["content"]) for m in memory._messages)
    print(f"[记忆] 全量条数={len(memory._messages)} "
          f"估算token={total} 本轮触发摘要={compressed}")
    return answer


# 20 轮长对话：提拉米苏教程陪练
for i in range(1, 21):
    q = f"第 {i} 步：请用一句话鼓励我继续做提拉米苏。"
    if i == 5:
        q = "记住：我不吃榴莲，以后推荐任何食谱都请避开榴莲。"
    run_with_memory(q)

# 终极验证：摘要触发之后，偏好还在吗？
print("\n最终验证：我有忌口吗？")
print(run_with_memory("我有忌口吗？是什么？"))
```

集成方式是「包装」而非改动：run 前把 memory.get_messages() 拼进问题上下文，答后 add 回记忆，每轮 maybe_summarize。第 5 轮埋了一颗「榴莲偏好」的种子，20 轮后提问验证——如果摘要提示词写对了，它应该活下来。

## ▶️ 运行效果

```text
$ python check_memory.py
原始条数: 7 预算内保留: 5
保留的第一条: 第 3 条消息，长度 20 字符的一个句子示例。
估算 token: 100

$ python memory_demo.py
[记忆] 全量条数=3 估算token=182 本轮触发摘要=False
[记忆] 全量条数=5 估算token=361 本轮触发摘要=False
[记忆] 全量条数=7 估算token=538 本轮触发摘要=False
[记忆] 全量条数=9 估算token=742 本轮触发摘要=False
[记忆] 全量条数=11 估算token=948 本轮触发摘要=False
[记忆] 全量条数=13 估算token=1160 本轮触发摘要=False
[记忆] 全量条数=8 估算token=1432 本轮触发摘要=True
[记忆] 全量条数=10 估算token=1641 本轮触发摘要=True
...
最终验证：我有忌口吗？
[记忆] 全量条数=8 估算token=1367 本轮触发摘要=True
是的，你不吃榴莲，推荐食谱时会避开榴莲。
```

（输出因模型而异。关注两点：触发摘要那几轮条数骤降；最终的忌口回答正确，说明偏好被摘要保住了。）

## ⚠️ 常见坑

1. **摘要丢关键约束**。现象：压缩后模型忘了用户的格式要求或忌口。原因：普通摘要只留「大意」，约束这种细节最先被牺牲。解法：提示词点名保留用户偏好与硬性要求（Step 2 写法）；再像演示那样在结尾用验证问题抽查。

2. **每轮都摘要，浪费钱**。现象：token 账单莫名翻倍。原因：无条件每轮调一次 llm.chat 做压缩，其实历史还远没满。解法：maybe_summarize 先算总量、超阈值才动手——判断那两行就是钱。

3. **摘要 system 与原 system 打架**。现象：模型行为分裂，一会儿遵守人设一会儿忘了。原因：把压缩摘要也做成一条 system 顶到最前，与 Agent 的 system_prompt 形成两份设定，谁后谁赢。解法：摘要用「[历史摘要]」前缀混在上下文里注入（Step 4 写法），人设只留 Agent 自己那一条；第 15 课组装时尤其注意。

4. **单条消息占满预算**。现象：用户粘了一篇长文后，get_messages 只剩这一条，其他全被裁掉。原因：滑动窗口按消息逐条装，一条巨无霸就把预算吃光。解法：add 时对超长 content 做预截断（保留首尾并注明省略），或提示用户拆开发送：

```python
# memory_short.py：add 里加超长消息预截断
MAX_MSG_CHARS = 2000

def add(self, role: str, content: str):
    if len(content) > MAX_MSG_CHARS:
        half = MAX_MSG_CHARS // 2
        content = (content[:half]
                   + f"…[中间省略 {len(content) - MAX_MSG_CHARS} 字]…"
                   + content[-half:])          # 首尾各留 1000 字
    self._messages.append({"role": role, "content": content})
```

## ✍️ 课后练习

1. （易）改进 est_tokens：连续 ASCII 字符按 len/4 计、汉字按 1 计（提示：用 ord(c) < 128 区分），对比新旧估算在同一对话上的差异。
2. （中）给 ShortTermMemory 加 pinned 机制：add 时若 content 含「记住」二字则进置顶列表，get_messages 永远先返回置顶再装普通消息。
3. （难）把 run_with_memory 封装成 MemoryAgent 类（继承 Agent），构造时接收 memory 参数——第 9 课还会再写一个带长期记忆的版本，届时对比两种继承设计。

## ⏭ 下一课预告

短期记忆关掉终端就没了：换个进程，Agent 把你忘得一干二净。第 9 课上长期记忆——标准库 SQLite 落盘 + 关键词检索，跨进程运行依然记得你对花生过敏。
""",
    },
    {
        "title": "第 9 课 · 长期记忆：SQLite 持久化与检索",
        "summary": "会话一关记忆清零？本课用标准库 SQLite 建长期记忆库，词元重合计分做关键词检索，MemoryAgent 答前注入、答后存摘要，跨进程仍记得你对花生过敏。",
        "difficulty": 2,
        "tags": ["Agent开发", "长期记忆", "SQLite", "关键词检索"],
        "duration_minutes": 20,
        "content": r"""## 🎯 本课目标

- 分清短期与长期记忆的边界：会话窗口内 vs 跨进程持久
- 用标准库 sqlite3 建记忆表，写 remember / recall / all / clear 四个操作
- 实现 MemoryAgent：答前检索相关记忆注入上下文，答后存问答摘要
- 跑两次进程演示：第一次「教」，第二次「考」，验证记忆真的跨会话

## 📦 本课产出

| 产出 | 说明 | 备注 |
|------|------|------|
| memory_long.py | LongTermMemory + MemoryAgent | 单文件 memory.db，零外部依赖 |
| check_memory_long.py | 不调 LLM 的检索自检 | 验证打分逻辑，零成本 |
| demo_memory_long.py | 跨进程记忆演示 | teach 与 recall 两种模式 |

## 🔗 承接上一步

第 8 课的 ShortTermMemory 很称职，但它住在内存里：终端一关、进程一退，user 的偏好、聊过的目标全部蒸发。真实助手必须「记得住人」——上周说过的过敏史，今天问零食时还能想起来。本课把记忆落盘到 SQLite，并给 Agent 加上「先回忆再回答、答完记一笔」的习惯。

## 📖 概念讲解

### 短期 vs 长期：两种记忆两种性格

| 维度 | 短期记忆（第 8 课） | 长期记忆（本课） |
|------|--------------------|------------------|
| 生命周期 | 本次会话窗口内 | 跨会话、跨进程、重启后仍在 |
| 存储位置 | 内存里的 messages 列表 | 磁盘上的单个 .db 文件 |
| 容量策略 | 上下文预算，超了压缩 | 落盘为主，几乎无限 |
| 注入方式 | 全量随每轮发送 | 只注入与当前问题相关的条目 |

最后一行是关键设计差异：短期记忆每轮全量随行（反正就几条），长期记忆必须**按需检索**——记忆库会越长越大，全量塞进上下文既贵又吵，只捞相关的。

### 为什么选 SQLite

三个理由：标准库（import sqlite3 就有，零安装，延续课程「少依赖」原则）、单文件（memory.db 拷走即备份，删掉即清空）、SQL 查询（想按时间筛、按类型筛都行）。等记忆上到百万条、需要语义检索，再升级专用存储也不迟——先把数据模型跑通。

### 关键词检索：最笨但最透明的打分

recall 的打分逻辑三步：query 按非字母数字字符切成词元（保留长度 ≥ 2 的片段，中英文都适用）；逐条记忆统计词元重合次数作为 score；按分数降序取前 K，score 为 0 的不返回。没有向量、没有神经网络，但完全可解释——哪条记忆为什么得分高，一眼看穿。它的天花板（同义改述召回不到）本课如实呈现，第 10 课的语义检索来补。

## 🛠 分步实现

### Step 1：memory_long.py——建表与写入

```python
# memory_long.py：长期记忆——SQLite 持久化与关键词检索
import re
import sqlite3


class LongTermMemory:
    '''长期记忆：SQLite 单文件存储 + 词元重合检索。'''

    def __init__(self, db_path: str = "memory.db"):
        # check_same_thread=False：允许跨线程使用同一连接（见常见坑 2）
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        self._conn.commit()

    def remember(self, text: str, kind: str = "fact"):
        # 写入一条记忆；kind 区分类型：fact / preference / qa / event……
        self._conn.execute(
            "INSERT INTO memories (kind, content) VALUES (?, ?)", (kind, text)
        )
        self._conn.commit()
```

表就四列：自增 id、类型 kind、内容 content、时间 created_at（默认当前时间）。CREATE TABLE IF NOT EXISTS 让重复运行不报错——脚本多次启动是常态。

### Step 2：recall——词元重合打分

```python
    @staticmethod
    def _tokens(text: str) -> list:
        # 极简分词：按非字母数字字符切开，保留长度 >= 2 的片段
        parts = re.split(r"[^0-9A-Za-z\u4e00-\u9fff]+", text)
        return [p.lower() for p in parts if len(p) >= 2]

    def recall(self, query: str, top_k: int = 3) -> list:
        # 关键词检索：query 切词元，逐条记忆数重合次数作为 score
        q_tokens = set(self._tokens(query))
        rows = self._conn.execute(
            "SELECT content FROM memories ORDER BY id DESC"
        ).fetchall()
        scored = []
        for (content,) in rows:
            c_tokens = self._tokens(content)
            score = sum(c_tokens.count(t) for t in q_tokens)
            if score > 0:
                scored.append((score, content))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [content for _, content in scored[:top_k]]

    def all(self) -> list:
        # 辅助：看库里到底存了什么（调试用）
        return self._conn.execute(
            "SELECT id, kind, content, created_at FROM memories ORDER BY id"
        ).fetchall()

    def clear(self):
        self._conn.execute("DELETE FROM memories")
        self._conn.commit()
```

_tokens 用 re.split 按「非字母数字汉字」切段：「推荐我一个零食，注意过敏」切成「推荐我一个零食」「注意过敏」两个片段；长度 1 的碎片（如「我」「个」单字被并入长段或被丢弃的边界情况）由 len >= 2 过滤掉噪音。打分用 sum(count)：query 里每个词元在记忆内容里出现几次就加几分——重合越多分越高。

### Step 3：check_memory_long.py——先验证检索，不调 LLM

```python
# check_memory_long.py：纯本地验证记忆库（内存库，不落盘）
from memory_long import LongTermMemory

mem = LongTermMemory(":memory:")          # :memory: = 临时内存库，测试专用
mem.remember("我对花生过敏", kind="preference")
mem.remember("我住在上海", kind="preference")
mem.remember("项目评审会在周三下午", kind="event")

print(mem.recall("推荐一个零食，注意我的过敏"))   # 应命中：花生过敏
print(mem.recall("我下周有什么会"))               # 应命中：评审会
print(mem.recall("今天天气怎么样"))               # 无重合：应返回 []
for row in mem.all():
    print(row)
```

预期：第一条命中「我对花生过敏」（「过敏」一词重合）；第二条命中评审会（「会」单独长度不足，但「评审会」作为整段重合）；第三条返回空列表——score 为 0 的记忆不返回，宁缺毋滥。

### Step 4：MemoryAgent——答前回忆，答后记账

```python
# memory_long.py 底部追加：带长期记忆的 Agent
from agent_core import Agent, DEFAULT_SYSTEM_PROMPT
from toolbox import ToolBox


class MemoryAgent(Agent):
    '''带长期记忆的 Agent：答前检索注入，答后写入摘要。'''

    def __init__(self, llm, memory: LongTermMemory,
                 toolbox: ToolBox | None = None,
                 system_prompt: str = DEFAULT_SYSTEM_PROMPT,
                 max_steps: int = 8):
        super().__init__(llm, toolbox=toolbox,
                         system_prompt=system_prompt, max_steps=max_steps)
        self.mem = memory

    def run_with_memory(self, question: str, verbose: bool = True) -> str:
        raw = question                       # 留一份原始问题，存库时用
        # 1) 答前：检索与问题相关的历史记忆
        hits = self.mem.recall(question, top_k=3)
        if hits:
            block = "\n".join(f"- {h}" for h in hits)
            if verbose:
                print(f"🧠 命中 {len(hits)} 条记忆：\n{block}")
            question = f"[相关记忆]\n{block}\n\n[问题]\n{question}"
        # 2) 正常走 ReAct 循环（父类的 run 一行没改）
        answer = self.run(question, verbose=verbose)
        # 3) 答后：本轮问答的一句话摘要存进长期记忆
        self.mem.remember(
            f"用户说过：{raw}；助手回答：{answer[:80]}", kind="qa"
        )
        return answer
```

继承 Agent 但不覆写 run：记忆逻辑包在 run_with_memory 外层——前检索、中执行、后落账。注入方式与第 8 课一致（拼进 question 而非另立 system），避免两份 system 打架。

### Step 5：demo_memory_long.py——跨进程演示

```python
# demo_memory_long.py：跨进程记忆演示——同一个脚本跑两次
import sys

from llm_client import LLMClient
from memory_long import LongTermMemory, MemoryAgent

llm = LLMClient()
mem = LongTermMemory("memory.db")            # 磁盘文件：进程退出数据还在
agent = MemoryAgent(llm, mem)

if "--teach" in sys.argv:
    # 第一次会话：教它一件关于你的事
    print(agent.run_with_memory("请记住：我对花生过敏，推荐食物必须避开花生。"))
else:
    # 第二次会话：全新进程，问题里不提「花生」二字
    print(agent.run_with_memory("推荐我一个零食"))
```

## ▶️ 运行效果

```text
$ python demo_memory_long.py --teach
🧠 命中 0 条记忆：（库里还没有内容）
✅ 第 1 步：模型给出最终回答
好的，已记住：你对花生过敏，之后推荐食物会避开花生。

$ python demo_memory_long.py
🧠 命中 1 条记忆：
- 用户说过：请记住：我对花生过敏，推荐食物必须避开花生。；助手回答：好的，已记住……
✅ 第 2 步：模型给出最终回答
推荐你试试原味米饼或海苔脆片——记得避开花生成分，选购时认准「不含花生」标识。
```

（输出因模型而异。第二次运行是新进程，数据来自上一次留下的 memory.db——这就是「长期」二字的含义。）

## ⚠️ 常见坑

1. **关键词检索召回差**。现象：问「我不能吃什么」检索不到「过敏」——字面没有重合词。原因：关键词法只认字面，同义改述是它的天花板。解法：课程阶段如实接受（可让用户换问法），根治靠第 10 课之后的 embedding 语义检索。

2. **sqlite 并发**。现象：Agent 跑在子线程里一读写就 ProgrammingError: SQLite objects created in a thread...。原因：连接默认只允许创建它的线程使用。解法：connect 时传 check_same_thread=False（本课已加），并自己保证「同一时刻只有一个线程在写」。

3. **记忆污染**。现象：某轮模型答错了，错答案被 remember 进库，下次检索出来以讹传讹。原因：答后无脑存问答对。解法：分级与过滤——用户明确表达的偏好存 kind="preference" 高优先；答案含「不知道」「无法」的不存；定期用 all() 抽查清理。

4. **检索空手而归时的表现**。现象：recall 返回空列表，Agent 答得没毛病但「像失忆」。原因：score=0 的条目全部被过滤，这是设计行为。解法：可以在空手时回退注入最近 2 条记忆（ORDER BY id DESC LIMIT 2），权衡「相关」与「新鲜」。

## ✍️ 课后练习

1. （易）给 LongTermMemory 加 delete(mem_id: int) 方法，配合 all() 做一个人工清理脚本。
2. （中）改造 run_with_memory 的落账逻辑：识别「记住：xxx」句式，把 xxx 以 kind="preference" 单独存一条，其余照旧存 qa。
3. （难）给 recall 加时间衰减：score 相同时新记忆排前，进一步给分数乘上 0.9 的「天数次方」（created_at 距今天数），验证旧记忆会慢慢沉底。

## ⏭ 下一课预告

关键词检索只认字面，同义改述就抓瞎；而且 Agent 该「开卷考试」的场景不止记忆——公司制度、产品文档都该先查再答。第 10 课 RAG：切分、2-gram、TF-IDF，让 Agent 回答前先查你的私有资料。
""",
    },
    {
        "title": "第 10 课 · RAG：让 Agent 先查资料再回答",
        "summary": "模型不知道你的私有文档，还会一本正经编造。本课手写极简 RAG：空行切段带 50 字重叠、2-gram 分词、TF-IDF 检索，先查资料再回答，开关 RAG 对比立见。",
        "difficulty": 2,
        "tags": ["Agent开发", "RAG", "TF-IDF", "检索增强"],
        "duration_minutes": 25,
        "content": r"""## 🎯 本课目标

- 说清 RAG 解决的三大痛点：知识截止、私有文档、幻觉
- 实现 add_text：空行切段 + 超 500 字滑动再切并带 50 字重叠
- 手写字符 2-gram 分词与 TF-IDF 打分（IDF = log(N/(1+df))），零依赖完成检索
- 用 knowledge.txt 灌入公司报销制度，对比开关 RAG 的回答质量差异

## 📦 本课产出

| 产出 | 说明 | 备注 |
|------|------|------|
| rag.py | RAG 类：切分、索引、检索、拼上下文 | 纯标准库，零外部依赖 |
| knowledge.txt | 公司报销制度示例文档 | RAG 的「私有知识库」 |
| rag_agent.py | 开/关 RAG 对比演示 | 亲眼看见「编造」变「有据」 |
| check_rag.py | 不调 LLM 的检索自检 | 先验检索质量再接模型 |

## 🔗 承接上一步

第 9 课结尾我们承认了关键词检索的天花板：只认字面，同义改述抓瞎。本课升级检索武器，并且把战场从「聊天记忆」扩展到「私有文档」——报销制度、产品手册这类从未进过模型训练集的知识。思想同源（词频打分），但加了两个关键组件：文档切分与 TF-IDF 加权。这套手写实现是未来升级 jieba 分词、embedding 向量、FAISS 索引的思想原型。

## 📖 概念讲解

### 为什么 RAG：模型的三个先天缺陷

| 痛点 | 表现 | RAG 的解法 |
|------|------|-----------|
| 知识截止 | 训练日期之后的事一概不知 | 资料随时可更新 |
| 私有文档 | 公司制度、内部数据从没进过训练集 | 灌进本地资料库 |
| 幻觉 | 不知道也要一本正经编一个 | 提示词强制「仅依据资料回答」 |

RAG = Retrieval-Augmented Generation（检索增强生成）。一句话：让模型从「闭卷凭记忆」改成「开卷查资料」。流程全图：

```text
knowledge.txt（私有文档）
   │ add_text()
   ▼
切分：空行切段；超 500 字滑动再切，段间留 50 字重叠
   │ _add_chunk()
   ▼
索引：每段算字符 2-gram 词频 TF；全局统计文档频率 DF
   │ retrieve(query)
   ▼
检索：query 切 2-gram → 逐段算 Σ(TF × IDF) → 取 Top-K
   │ build_context()
   ▼
拼提示词：【资料1·标题】内容… + 问题 + 「仅依据资料回答」
   │
   ▼
Agent 生成：资料不足就直说不知道，禁止编造
```

### 切分：为什么是 500 字 + 50 字重叠

chunk 是检索的最小单位，大小是精度与成本的平衡：太大——一个 chunk 混多个主题，检索粒度粗，拼进提示词还浪费窗口；太小——一句话被拦腰截断，语义不完整，检索到了也读不懂。50 字重叠则是保险：跨切点的句子在相邻两个 chunk 里都有备份，谁都不丢。

### 字符 2-gram：中文分词的零依赖近似

英文有空格天然分词，中文「住宿标准」连成一串。课程不引 jieba（保持零依赖），改用相邻两字符成词的 2-gram：「住宿标准」切出「住宿」「宿标」「标准」三个 gram。虽然「宿标」是无意义噪音，但「住宿」「标准」两个有效词都命中了，检索照样工作；噪音则交给 IDF 去稀释——常见 gram 天然低分。

### TF-IDF：让常见字闭嘴

打分 = Σ(TF × IDF)，逐词元求和。TF（词频）：这个词在当前 chunk 出现几次；IDF（逆文档频率）：log(N/(1+df))，N 是总 chunk 数，df 是含该词的 chunk 数——越常见的词 IDF 越接近 0。「公司」「制度」这种到处都有的词自动被稀释，而「花生」这种只在个别段落出现的词权重高。检索分高的含义：**罕见词在这个 chunk 里密集出现**。

## 🛠 分步实现

### Step 1：rag.py——切分与索引

```python
# rag.py：极简 RAG——切分、2-gram 索引、TF-IDF 检索
import math
import re


class RAG:
    '''零依赖 RAG：add_text 灌资料，retrieve / build_context 查资料。'''

    def __init__(self):
        self._chunks = []       # [{"title":..., "text":...}, ...]
        self._tfs = []          # 每个 chunk 的词频表 {gram: 次数}
        self._df = {}           # 文档频率：每个 gram 出现在多少个 chunk

    @staticmethod
    def _tokenize(s: str) -> list:
        # 中文没有空格分词，用字符 2-gram 近似：相邻两字符成一词
        s = re.sub(r"\s+", "", s)          # 先去掉空白，gram 更干净
        return [s[i:i + 2] for i in range(len(s) - 1)]

    def add_text(self, title: str, text: str):
        # 第一层切分：按空行切成自然段
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for para in paras:
            # 第二层切分：超 500 字的段落滑动再切，带 50 字重叠
            if len(para) <= 500:
                pieces = [para]
            else:
                pieces, step = [], 450          # 500 - 50 = 450
                for i in range(0, len(para), step):
                    pieces.append(para[i:i + 500])
                    if i + 500 >= len(para):
                        break
            for piece in pieces:
                self._add_chunk(title, piece)

    def _add_chunk(self, title: str, chunk_text: str):
        # 建 chunk 的词频表，并更新全局文档频率
        tf = {}
        for gram in self._tokenize(chunk_text):
            tf[gram] = tf.get(gram, 0) + 1
        self._chunks.append({"title": title, "text": chunk_text})
        self._tfs.append(tf)
        for gram in tf:
            self._df[gram] = self._df.get(gram, 0) + 1
```

两层切分各管一件事：空行切出语义天然完整的段落；超长段落按 450 步长滑动窗口再切，每片最多 500 字、相邻两片共享 50 字。_add_chunk 建 TF 表的同时把每个 gram 的 DF 加一——idf 公式里的 N 与 df 从这两份数据来。

### Step 2：retrieve——手写 TF-IDF 打分

```python
    def retrieve(self, query: str, top_k: int = 3) -> list:
        # 得分 = Σ query 词元的 TF × IDF（IDF = log(N / (1 + df))）
        n = len(self._chunks)
        if n == 0:
            return []
        grams = set(self._tokenize(query))
        scored = []
        for i, tf in enumerate(self._tfs):
            score = 0.0
            for g in grams:
                if g in tf:
                    idf = math.log(n / (1 + self._df[g]))
                    score += tf[g] * idf
            if score > 0:
                scored.append({
                    "title": self._chunks[i]["title"],
                    "text": self._chunks[i]["text"],
                    "score": round(score, 4),
                })
        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored[:top_k]
```

遍历每个 chunk：query 的每个 gram 若在该 chunk 出现，就累加 TF × IDF。分母用 1 + df 而不是 df，避免 df = 0 时除零；df = 0 时该 gram 根本不会出现在任何 chunk 的 tf 里，循环也到不了。score 为 0 的 chunk 不返回——和第 9 课一样，宁缺毋滥。

### Step 3：build_context——拼出提示词资料块

```python
    def build_context(self, query: str, top_k: int = 3) -> str:
        # 把检索结果拼成提示词里的【参考资料】块
        hits = self.retrieve(query, top_k=top_k)
        blocks = [f"【资料{i}·{h['title']}】\n{h['text']}"
                  for i, h in enumerate(hits, 1)]
        return "\n\n".join(blocks)
```

### Step 4：check_rag.py——先验证检索，再接模型

```python
# check_rag.py：不调 LLM，先确认检索打得准
from rag import RAG

rag = RAG()
rag.add_text("报销制度", "一线城市住宿上限每晚 600 元。\n\n其他城市住宿上限每晚 450 元。")
rag.add_text("考勤制度", "迟到 30 分钟以内不扣款，每月 3 次以内免罚。")

for h in rag.retrieve("出差住酒店一晚最多报多少钱"):
    print(h["score"], h["title"], h["text"][:30])
print("---")
print(rag.build_context("住宿报销上限"))
```

预期：「出差住酒店一晚最多报多少钱」与住宿标准段命中「住宿」等 gram，考勤段 score 为 0 不返回。检索准了，才轮到模型登场。

### Step 5：knowledge.txt + rag_agent.py——接入 Agent

先准备私有文档（text 代码块，保存为 knowledge.txt，段落之间用空行分隔）：

```text
# knowledge.txt：公司报销制度（节选示例）

## 交通标准

员工出差乘坐高铁一律二等座，单程 6 小时以上的行程可申请一等座。
经济舱机票需提前 5 天预订，全价机票不予报销。

## 住宿标准

一线城市（北京、上海、广州、深圳）住宿上限为每晚 600 元。
其他城市住宿上限为每晚 450 元，超标部分个人自付。
特殊情况需事先报部门总监审批后方可入住超标酒店。

## 餐补标准

出差期间餐补为每自然日 100 元，当天往返减半。
市内交通费实报实销，上限每自然日 80 元。
```

```python
# rag_agent.py：接入 Agent 的 RAG 问答——开关 RAG 对比
from agent_core import Agent
from llm_client import LLMClient
from rag import RAG

llm = LLMClient()
rag = RAG()

# 灌入私有文档：真实场景可以遍历目录逐个 add_text
with open("knowledge.txt", "r", encoding="utf-8") as f:
    rag.add_text("公司报销制度", f.read())

RAG_RULE = "回答规则：仅依据下方【参考资料】回答；资料不足就直说不知道，禁止编造。"


def ask(question: str, use_rag: bool) -> str:
    agent = Agent(llm, system_prompt="你是一个严谨的公司制度问答助手。")
    if use_rag:
        context = rag.build_context(question)
        prompt = f"{RAG_RULE}\n\n【参考资料】\n{context}\n\n【问题】\n{question}"
        return agent.run(prompt, verbose=False)
    return agent.run(question, verbose=False)     # 闭卷裸答：对照组


print("── 不开 RAG（模型裸答，容易编造）──")
print(ask("差旅住宿标准是多少", use_rag=False))
print("\n── 开 RAG（先查资料再回答）──")
print(ask("差旅住宿标准是多少", use_rag=True))
```

rag_agent.py 不需要工具调用——RAG 在这里走的是「检索后拼进提示词」的路线，Agent.run 只负责生成回答。第 15 课组装 AssistantCLI 时，会把 RAG 与工具、记忆一起接上。

## ▶️ 运行效果

```text
$ python check_rag.py
3.4657 报销制度 其他城市住宿上限每晚 450 元，超标部分个人自付。特殊情况需事先报部门总监审批后方可入住超标酒店。
2.7726 报销制度 一线城市（北京、上海、广州、深圳）住宿上限为每晚 600 元。
---
【资料1·报销制度】
一线城市（北京、上海、广州、深圳）住宿上限为每晚 600 元。

【资料2·报销制度】
其他城市住宿上限为每晚 450 元，超标部分个人自付。……

$ python rag_agent.py
── 不开 RAG（模型裸答，容易编造）──
一线城市每晚 800 元、其他城市 500 元，均不含服务费……（编造的制度）

── 开 RAG（先查资料再回答）──
根据公司报销制度：一线城市（北京、上海、广州、深圳）住宿上限为每晚 600 元，
其他城市为每晚 450 元，超标部分个人自付；特殊情况需事先报部门总监审批。
```

（输出因模型而异。关 RAG 时模型对私有制度一无所知，数字全靠猜；开 RAG 后回答与 knowledge.txt 逐字对得上——这就是「有据可查」。）

## ⚠️ 常见坑

1. **chunk 尺寸失衡**。现象：太大——检索到一段塞满无关内容，回答被带偏、窗口被浪费；太小——「住宿上限为每晚……」后半句在下一个 chunk，答案缺斤短两。解法：从 300~500 字起步按效果调；超长段落务必带 overlap。

2. **Top-K 过大引入噪音**。现象：K 拉到 10 后回答反而变差。原因：排名靠后的 chunk 相关性低，噪音稀释了有效信息，模型还要为垃圾 token 买单。解法：K 取 3~5，并加分数阈值，低分块宁可不进提示词：

```python
# retrieve 调用侧加分数阈值：低分块直接过滤
MIN_SCORE = 1.0

hits = [h for h in rag.retrieve(question, top_k=5)
        if h["score"] >= MIN_SCORE]
context = "\n\n".join(
    f"【资料{i}·{h['title']}】\n{h['text']}" for i, h in enumerate(hits, 1)
)
```

3. **检索分高 ≠ 回答正确**。现象：问「住宿超出标准找谁审批」，检索把「住宿上限」段排最前，但答案（总监审批）在同主题的另一段。原因：TF-IDF 只管字面相似，不理解段落间关系。解法：短期靠小 chunk + 高 K 兜底覆盖；根治用 rerank——先检索 10 条，再让模型把最相关的 3 条挑出来（放进 rag_agent.py 时记得补 import re）：

```python
# rerank 雏形：初检 10 条，让模型精选 3 条
candidates = rag.retrieve(query, top_k=10)
menu = "\n".join(f"{i}. {h['title']}：{h['text'][:50]}"
                 for i, h in enumerate(candidates, 1))
resp = llm.chat([{"role": "user", "content":
                  f"问题：{query}\n候选资料：\n{menu}\n"
                  "返回最相关的 3 个编号，逗号分隔，只输出编号。"}])
picks = [int(x) for x in re.findall(r"\d+", resp.choices[0].message.content)]
final = [candidates[i - 1] for i in picks[:3]]
```

4. **升级路线要心里有数**。本课 2-gram + TF-IDF 是检索的地基原型，工程化升级依次是：jieba 分词（词更准）、embedding 语义检索（同义改述也能召回，补第 9 课的天花板）、FAISS/Chroma 等向量库（百万级文档的吞吐）。每一步都建立在你今天手写的这套流程上，只是「打分函数」换掉。

## ✍️ 课后练习

1. （易）给 RAG 加 stats() 方法：打印 chunk 总数、词表大小（len(self._df)）与平均 chunk 长度。
2. （中）给 retrieve 加 min_score 参数：低于阈值的直接过滤；build_context 检测全部低于阈值时返回空串，并在 rag_agent.py 里对空串给出「资料库中没有相关内容」的明确提示。
3. （难）实现 rerank 雏形：retrieve(query, top_k=10) 取 10 条，把「编号 + 标题 + 首句」列表发给 llm.chat，让它返回最相关的 3 个编号，按编号重组返回。

## ⏭ 下一课预告

ReAct 是「边想边做」，任务一复杂就容易走偏、返工。第 11 课 Plan-and-Execute：先让模型列出完整计划，再逐步执行、按需修正——planner.py 让你的 Agent 学会谋定而后动。
""",
    },
]
