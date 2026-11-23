"""《从零手写 AI Agent》课程第 1-5 课种子数据：课程总览与环境准备、LLM 客户端封装、系统提示词与多轮对话管理、手写 Function Calling、工具注册系统。"""

ARTICLES_A = [
    {
        "title": "第 1 课 · 课程总览与环境准备：跑通第一个大模型调用",
        "summary": "从零开始的第一课：创建 agent_course 项目、装好 openai v1 SDK，写出全课程通用的 settings.py，12 行跑通第一个大模型调用，并给出 15 课路线图与 Agent、聊天机器人、工作流的概念对比。",
        "difficulty": 1,
        "tags": ["Agent开发", "环境搭建", "openai SDK", "课程地图"],
        "duration_minutes": 18,
        "content": """## 🎯 本课目标

- 建立 agent_course 项目目录与虚拟环境，安装 openai SDK 并验证版本号 ≥ 1.0
- 写出全课程通用的 settings.py：密钥走环境变量，BASE_URL / MODEL 可一键切换服务商
- 跑通 hello_llm.py 第一个调用，能读懂响应里的 choices、finish_reason 与 usage 三块信息
- 说清 OpenAI(...) 与 create(...) 的关键参数：timeout / max_retries / temperature / max_tokens
- 认识 SDK 异常家族，动手写出 20 行的迷你封装 ask_llm（第 2 课 LLMClient 的雏形）
- 记住 DeepSeek / GLM / Kimi / Ollama 四家的 base_url，随时换模型验证同一份代码

## 📦 本课产出

| 产出 | 说明 | 备注 |
|------|------|------|
| agent_course/ 项目目录 | 全部 15 课代码都住在这里 | 第三方依赖只有 openai（第 7 课前） |
| settings.py | API_KEY / BASE_URL / MODEL 三件套 | 全课程复用，写完不再改 |
| hello_llm.py | 第一个最小可用调用（约 12 行） | 本课主角 |
| .env（可选） | 密钥文件方案，python-dotenv 加载 | 必须同时配 .gitignore |
| hello_llm_v2.py | 拆开看响应结构的进阶版 | 帮你建立「响应长什么样」的手感 |
| hello_safe.py | 迷你封装 ask_llm + 异常分类处理 | 第 2 课 LLMClient 的直接雏形 |
| experiment_params.py | 玩转 temperature / max_tokens | 选做 |

## 🗺 课程地图与最终成果

动第一行代码之前，先看清要去哪儿。

这门课的理念只有一句话：**不用 LangChain 等任何 Agent 框架，从零手写，先懂原理再谈工程**。框架把魔法藏在黑盒里，你会用却不会修；而 15 课之后你会发现，Agent 的核心机制总共就那么几百行纯 Python，亲手写过一遍，任何框架的源码对你都不再神秘。

15 课结束时，你会在 agent_course 目录里得到一个完全由自己手写的 **AssistantCLI 智能助手**：它能调用真实工具（计算器、时间、文件读写、网页抓取），有短期与长期记忆，会先检索资料再回答（RAG），能先规划再执行，甚至能指挥多个子智能体协作，并且自带安全护栏与逐步追踪日志。

15 课路线图：

| 阶段 | 课号 | 产出文件 | 你将学会 |
|------|------|----------|----------|
| 基础设施 | 1 | settings.py、hello_llm.py | 环境准备与第一次调用 |
| 基础设施 | 2 | llm_client.py | 重试、流式与 Token 统计 |
| 基础设施 | 3 | conversation.py、chat_cli.py | 系统提示词与多轮对话管理 |
| 工具能力 | 4 | manual_tool_call.py | 手写 Function Calling 全流程 |
| 工具能力 | 5 | toolbox.py | @tool 装饰器与 ToolBox |
| Agent 内核 | 6 | agent_core.py | ReAct 循环与终止条件 |
| Agent 内核 | 7 | tools_basic.py | 计算器、时间、文件与网页抓取 |
| 记忆 | 8 | memory_short.py | 上下文预算与对话压缩 |
| 记忆 | 9 | memory_long.py | SQLite 持久化与检索 |
| 进阶能力 | 10 | rag.py | 先查资料再回答 |
| 进阶能力 | 11 | planner.py | 先规划再执行 |
| 进阶能力 | 12 | multi_agent.py | Worker、Reviewer 与 Orchestrator |
| 生产化 | 13 | guardrails.py | 白名单、预算与危险指令拦截 |
| 生产化 | 14 | tracing.py | 追踪每一步并自动打分 |
| 毕业项目 | 15 | assistant.py | 组装 AssistantCLI 智能助手 |

### Agent、聊天机器人、工作流：三个最容易混淆的词

| 维度 | 聊天机器人 | 工作流 | Agent |
|------|-----------|--------|-------|
| 控制流 | 一问一答 | 人提前写死每一步 | 模型在运行中自己决定下一步 |
| 工具使用 | 基本没有 | 固定接线，按流程触发 | 模型按需挑选并组合 |
| 迭代能力 | 无 | 无 | 有：观察结果、修正方向、循环推进 |
| 典型例子 | 客服 FAQ 问答 | 审批流、定时 ETL | 「帮我订机票」「写完这份报告并自检」 |

本课程造的就是第三列。而第 4 课的 Function Calling，正是让模型获得「挑工具」能力的那把钥匙。

## 📖 概念讲解

### 一切从 chat.completions.create 开始

好消息是：主流大模型厂商几乎都实现了 OpenAI 兼容协议。也就是说，你只需要学会 openai 这一个 SDK 的用法，改一个 base_url 就能换到几乎所有家（包括本地模型）。本课程示例统一使用 deepseek-chat，同样的代码在下列服务商上都能跑：

| 服务商 | base_url | 常用模型名 | 说明 |
|--------|----------|-----------|------|
| DeepSeek | https://api.deepseek.com | deepseek-chat | 课程默认示例 |
| 智谱 GLM | https://open.bigmodel.cn/api/paas/v4 | glm-4-flash 等 | 国内直连稳定 |
| Kimi（月之暗面） | https://api.moonshot.cn/v1 | moonshot-v1-8k 等 | 注意路径带 /v1 |
| Ollama（本地） | http://localhost:11434/v1 | qwen2.5:7b 等 | api_key 填 ollama 即可 |

模型名以各家官方文档为准，本课程代码不锁死任何模型。第 15 课的 AssistantCLI 换模型也只是改环境变量的事。

### messages：全课程最重要的数据结构

调用模型的核心参数是 messages，它是一个列表，每个元素是带 role 的字典。四种角色先混个脸熟：

| role | 谁在说话 | 例子 |
|------|----------|------|
| system | 程序员写的「设定」 | 你是一个严谨的天气助手 |
| user | 终端用户的输入 | 北京今天多少度？ |
| assistant | 模型的回复 | 今天北京晴，12~22°C |
| tool | 工具执行结果（第 4 课登场） | {"weather": "晴", ...} |

第 3 课会展开讲多轮对话时这个列表如何滚动增长，第 4 课会看到 assistant 与 tool 如何配对。今天只需要记住：**一次调用 = 把一组 messages 发给模型 = 收回一个响应对象**。

### 虚拟环境与环境变量：第一道工程素养关

**为什么要虚拟环境**：venv 的原理其实只有两步——在项目里生成一个 .venv 目录（内含独立的解释器副本与 site-packages 包目录），激活时把 PATH 指向它。之后 pip install 装进 .venv 而非系统 Python：项目之间包版本互不干扰；不想要了删掉 .venv 目录即等于干净卸载。AI 相关库迭代极快，虚拟环境是保命符。

**pip 太慢怎么办**：国内访问 PyPI 官方源经常龟速甚至超时，用清华镜像即可解决：

```bash
# 临时使用（单次安装有效）
pip install openai -i https://pypi.tuna.tsinghua.edu.cn/simple

# 一劳永逸：设为默认源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**密钥放哪里：export vs .env 文件**：两种主流方案效果等价，任选其一，settings.py 两种都兼容：

| 方案 | 做法 | 优点 | 注意事项 |
|------|------|------|----------|
| 终端 export | 每次开终端执行 export LLM_API_KEY=... | 零依赖、随开随用 | 换终端要重新 export |
| .env 文件 | 密钥写进项目根目录 .env，代码用 python-dotenv 加载 | 一次配置长期生效 | **必须加入 .gitignore，绝不能提交仓库** |

本课程正文以 export 为主（第 1 课少装一个依赖），.env 方案在 Step 2 给出完整写法，两种方式可随时互换。

## 🛠 分步实现

### Step 1：创建项目并安装依赖

```bash
# 0. 确认 Python 版本（需要 3.10+，课程代码的类型注解语法依赖它）
python3 --version

# 1. 建立项目目录并进入
mkdir agent_course && cd agent_course

# 2. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate
# Windows PowerShell 用户执行：.venv/Scripts/Activate.ps1

# 3. 安装 openai SDK（国内网络慢可追加清华镜像参数）
pip install openai
# pip install openai -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 验证：确认解释器来自 .venv，且 SDK 版本 >= 1.0
which python3
python3 -c "import openai; print(openai.__version__)"
```

两个验证都不要跳过：which python3 应指向 agent_course/.venv/bin/python3——新手最常见的事故就是忘了激活虚拟环境，pip 把包装进了系统 Python，然后 import openai 直接 ModuleNotFoundError。版本号若小于 1.0，执行 pip install -U openai 升级——新旧两代 SDK 的 API 完全不同，本课程全部使用 v1 风格。

### Step 2：settings.py——全课程的配置中枢

```python
# settings.py：全课程唯一的配置文件
# 密钥永远不要写死在代码里：优先读环境变量，没有设置时给一个占位提醒
import os

API_KEY = os.environ.get("LLM_API_KEY", "sk-你的密钥")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
```

逐行看：os.environ.get 的第二个参数是缺省值，环境变量没设置时用它兜底。这样密钥由运行环境注入，代码里不出现真实密钥，也方便用 export 随时切换服务商。启动前在终端执行一次：

```bash
export LLM_API_KEY="sk-你的真实密钥"    # macOS / Linux
# Windows PowerShell：$env:LLM_API_KEY = "sk-你的真实密钥"
```

如果更想把密钥存成文件，用 .env 方案（需先 pip install python-dotenv）：

```python
# settings.py（.env 版）：需要先 pip install python-dotenv
import os

from dotenv import load_dotenv

load_dotenv()  # 读取同目录 .env，把 KEY=value 注入环境变量

API_KEY = os.environ.get("LLM_API_KEY", "sk-你的密钥")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
```

```bash
# .env 文件（与 settings.py 同目录，格式就是 KEY=value，不要加 export）
LLM_API_KEY=sk-你的真实密钥
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

```text
# .gitignore（没有 git 可忽略；有则必须第一行就写上它）
.env
```

两个细节：load_dotenv 默认**不覆盖已存在的环境变量**，所以临时 export 永远比 .env 优先——调试时想临时换服务商，直接 export 即可，不用改文件；.env 放的是真实密钥，属于敏感文件，提交仓库前务必确认 .gitignore 生效。

### Step 3：hello_llm.py——12 行跑通第一次调用

```python
# hello_llm.py：人生第一个大模型调用
from openai import OpenAI

from settings import API_KEY, BASE_URL, MODEL

# 1) 创建客户端：密钥与服务商地址都来自 settings.py
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 2) 发起对话：messages 是列表，每个元素是带 role 的字典
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "用一句话介绍你自己"}],
)

# 3) 取出回答：choices 是候选列表，默认只返回 1 个
print(resp.choices[0].message.content)
print(resp.usage)     # 顺便看看这次花了多少 token
```

逐段解释：OpenAI(...) 创建的是「连接配置」，本身不发请求；chat.completions.create(...) 才是真正的一次对话调用；响应对象里的 choices[0].message.content 就是模型说的话，usage 里则是 token 计量。整个调用是同步阻塞的，网络往返一次通常一两秒。

### Step 4：看懂两个对象——client 怎么配，create 怎么调

hello_llm.py 里只有两行核心代码，但每一行都值得放大看。

**OpenAI(...)：一个可配置的连接器**。它创建时只保存配置，不发任何请求；真正决定「怎么连、连不上怎么办」的是这四个参数：

| 参数 | 作用 | 缺省行为 |
|------|------|----------|
| api_key | 密钥；不传时 SDK 会自己去找 OPENAI_API_KEY 环境变量 | 缺失则抛错 |
| base_url | 服务商端点根路径 | OpenAI 官方地址 |
| timeout | 单次请求超时秒数 | 600（太长了，建议显式调小） |
| max_retries | SDK 内置自动重试次数 | 2 |

```python
# 参数演示：给连接器上「保险」
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=30,      # 30 秒没响应就抛 APITimeoutError，别干等 10 分钟
    max_retries=2,   # SDK 内置的网络级重试
)
```

注意一个关键区别：SDK 内置的 max_retries 只处理连接失败、超时这类网络错误，**限流 429 与 401/400 业务报错它照样直接抛异常**——这正是第 2 课要自己再包一层重试的原因。

**chat.completions.create(...)：一次对话的全部选项**。本课程会用到其中六个，其余保持缺省：

| 参数 | 类型 | 作用 | 课程出场 |
|------|------|------|----------|
| model | str | 模型名 | 每一课 |
| messages | list[dict] | 对话内容，role + content 字典列表 | 每一课 |
| temperature | float 0~2 | 随机度：低=稳定，高=发散 | 第 1/6 课 |
| max_tokens | int | 回答最大 token 数，防止跑飞 | 第 1 课 |
| stream | bool | 流式返回 | 第 2 课 |
| tools | list | 工具清单（JSON Schema） | 第 4 课压轴登场 |

一个「全参数」调用长这样——先混个眼熟，注释掉的参数后面课程会逐一用到：

```python
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "你好"}],
    temperature=0.7,
    max_tokens=2000,
    # stream=True,   # 第 2 课：流式输出
    # tools=[...],   # 第 4 课：Function Calling
)
```

### Step 5：hello_llm_v2.py——把响应对象拆开看

```python
# hello_llm_v2.py：同样一次调用，把每一块信息都拆给你看
from openai import OpenAI

from settings import API_KEY, BASE_URL, MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        # system 放最前面：给模型一个「人设」，这次设定为说话极简
        {"role": "system", "content": "你是一个说话极简的助手，每次回答不超过 20 个字。"},
        {"role": "user", "content": "Python 是什么？"},
    ],
    temperature=0.3,     # 越低越稳定，越高越发散，取值 0~2
)

choice = resp.choices[0]
print("回答内容 :", choice.message.content)
print("结束原因 :", choice.finish_reason)   # stop=正常说完；length=被 max_tokens 截断
print("模型名称 :", resp.model)

usage = resp.usage
print("输入 token :", usage.prompt_tokens)      # 你的 messages 折算的输入量
print("输出 token :", usage.completion_tokens)  # 模型回答折算的输出量
print("总计 token :", usage.total_tokens)
```

finish_reason 从今天起值得你每次都瞄一眼：stop 是正常结束；length 说明回答被 max_tokens 硬生生掐断；到第 4 课还会见到关键的 tool_calls——它出现时意味着模型想用工具。

### Step 6：hello_safe.py——第一个迷你封装，把异常管起来

裸调用最怕出事：401 直接崩、429 直接崩、断网还是崩。工程化的第一步不是急着写类，而是先把「一次可能失败的操作」用 try/except 圈起来。openai SDK 的异常家族就住在顶层包里：

| 异常类型 | 触发场景 | 正确姿势 |
|----------|----------|----------|
| AuthenticationError | 401 密钥错 | 不重试，改配置 |
| RateLimitError | 429 限流 | 等一会再试（第 2 课自动化） |
| APITimeoutError | 请求超时 | 重试或换网络 |
| APIConnectionError | 连不上服务器 | 检查 base_url 与网络 |
| BadRequestError | 400 参数错 | 不重试，修代码 |

```python
# hello_safe.py：把「会失败的调用」圈进安全区
import time

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from settings import API_KEY, BASE_URL, MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=30)


def ask_llm(question: str, max_retries: int = 3) -> str:
    # 迷你封装：限流与网络异常自动重试，其他异常直接报给人看
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": question}],
            )
            return resp.choices[0].message.content
        except RateLimitError:
            wait = 2 ** attempt          # 指数退避：2s -> 4s -> 8s
            print(f"限流了，第 {attempt} 次重试，等 {wait} 秒...")
            time.sleep(wait)
        except (APITimeoutError, APIConnectionError):
            wait = 2 ** attempt          # 网络类错误同样值得重试
            print(f"网络异常，第 {attempt} 次重试，等 {wait} 秒...")
            time.sleep(wait)
        except AuthenticationError:
            raise SystemExit("密钥错误（401），重试没有意义，请检查 LLM_API_KEY")
    raise SystemExit(f"重试 {max_retries} 次仍失败，稍后再试")


if __name__ == "__main__":
    print(ask_llm("用一句话解释什么是大模型"))
```

逐段看懂三个设计决策：**指数退避**（wait = 2 ** attempt）让重试间隔翻倍增长，避免限流时疯狂撞墙；**异常分类**（值得重试的和重试也没用的分开处理）比一刀切的 except Exception 专业得多；**ask_llm 只接收 question 返回答案**（调用方完全不必知道重试的存在）。这个 20 行的函数已经有了「封装」的灵魂——第 2 课我们把它升级成 LLMClient 类，再加流式输出与 token 记账，就长成了全课程的地基。

### Step 7（选做）：experiment_params.py 动手摸参数

```python
# experiment_params.py：亲手感受两个最常用参数的作用
from openai import OpenAI

from settings import API_KEY, BASE_URL, MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def ask(question, temperature=0.7, max_tokens=200):
    # 最小封装：一次提问返回完整响应对象
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=temperature,
        max_tokens=max_tokens,
    )


# 实验 1：temperature=0，同一个问题问两遍，输出高度稳定
q = "用一句话解释什么是 Agent"
r1 = ask(q, temperature=0)
r2 = ask(q, temperature=0)
print("温度0-第一次:", r1.choices[0].message.content)
print("温度0-第二次:", r2.choices[0].message.content)

# 实验 2：temperature=1.5，输出明显更发散（允许范围 0~2）
r3 = ask(q, temperature=1.5)
print("温度1.5:", r3.choices[0].message.content)

# 实验 3：max_tokens=30 强制截断，finish_reason 会变成 length
r4 = ask("介绍一下 Python 的三大优势", max_tokens=30)
print("截断回答:", r4.choices[0].message.content)
print("结束原因:", r4.choices[0].finish_reason, "| 总 token:", r4.usage.total_tokens)
```

对 Agent 开发有个重要推论：temperature=0 能让模型决策更稳定，但代价是丧失创造性；第 6 课写 ReAct 循环时我们会讨论怎么权衡。

### Step 8：一键切换服务商

```bash
# 切到智谱 GLM（glm-4-flash 免费，适合练手）
export LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
export LLM_MODEL="glm-4-flash"
python hello_llm.py

# 切到本地 Ollama（先执行 ollama pull qwen2.5:7b 拉取模型）
export LLM_BASE_URL="http://localhost:11434/v1"
export LLM_MODEL="qwen2.5:7b"
export LLM_API_KEY="ollama"    # Ollama 不校验密钥，但 SDK 要求非空
python hello_llm.py
```

同一份代码，三个服务商全部能跑——这就是 OpenAI 兼容协议的价值，也是我们敢于「手写一切」的底气。

## ▶️ 运行效果

```text
$ python hello_llm.py
我是 DeepSeek 助手，由深度求索公司开发，专注于回答问题与完成任务。
CompletionUsage(completion_tokens=28, prompt_tokens=11, total_tokens=39)
```

```text
$ python hello_llm_v2.py
回答内容 : Python 是一种简洁易读的高级编程语言。
结束原因 : stop
模型名称 : deepseek-chat
输入 token : 22
输出 token : 15
总计 token : 37
```

```text
$ python hello_safe.py
用一句话解释：大模型是在海量文本上训练、能理解并生成自然语言的大型神经网络。
```

若恰好触发限流，你还能亲眼看到封装的价值——程序不再崩溃，而是自己缓过来：

```text
$ python hello_safe.py
限流了，第 1 次重试，等 2 秒...
限流了，第 2 次重试，等 4 秒...
用一句话解释：大模型是在海量文本上训练、能理解并生成自然语言的大型神经网络。
```

（输出内容因模型与随机性而异，字段结构一致。）

## ⚠️ 常见坑

1. **现象**：报 401 AuthenticationError。**原因**：密钥填错、没 export 就启动、或把别家的密钥配到了别家的 base_url。**解法**：先 echo $LLM_API_KEY 确认生效，再核对密钥与 base_url 是否同一家。
2. **现象**：404 或 model not found。**原因**：base_url 抄错——Kimi 少了结尾的 /v1、GLM 用成了别家路径、或把完整对话路径当成了 base_url。**解法**：对照上面表格逐字符检查，base_url 只填到端点根路径。
3. **现象**：AttributeError: module openai has no attribute ChatCompletion，或 OpenAI() got unexpected keyword。**原因**：装到了 0.x 旧版 SDK。**解法**：pip install -U openai 并确认版本 ≥ 1.0。
4. **现象**：APITimeoutError 连接超时。**原因**：国内访问部分境外服务不稳定。**解法**：优先用国内服务商或本地 Ollama；确需访问境外服务时配置稳定代理，并给 OpenAI(...) 传 timeout=60。
5. **现象**：密钥泄漏。**原因**：硬编码进了代码并提交到仓库。**解法**：坚持环境变量注入，把 .env 类文件加进 .gitignore；一旦泄漏立即在控制台重置密钥。
6. **现象**：ModuleNotFoundError: No module named openai。**原因**：忘了激活虚拟环境，pip 把包装进了系统 Python。**解法**：先 which python3 确认路径是否在 .venv 内，不在就重新 source .venv/bin/activate 后再安装。

## ✍️ 课后练习

1. （易）给 hello_llm.py 的 messages 前面加一条 system 消息，把模型设定成「只会押韵回答的诗人」，观察输出变化。参考骨架：

```python
messages = [
    {"role": "system", "content": "你是只会押韵回答的诗人，任何问题都用押韵句子回答。"},
    {"role": "user", "content": "介绍一下今天的天气"},
]
```

2. （中）打印 resp.model_dump()，找到 id 与 finish_reason 字段，各用一句话解释它们的作用。
3. （难）写 try_providers.py：把多家服务商的 base_url 与模型名放进列表循环请求，打印每家的成功或失败摘要。参考答案：

```python
# try_providers.py：依次探测多家服务商（注意：各家密钥相互独立，需分别准备）
import os

from openai import OpenAI

PROVIDERS = [
    ("DeepSeek", "https://api.deepseek.com", "deepseek-chat"),
    ("GLM", "https://open.bigmodel.cn/api/paas/v4", "glm-4-flash"),
    ("Kimi", "https://api.moonshot.cn/v1", "moonshot-v1-8k"),
]

for name, base_url, model in PROVIDERS:
    try:
        client = OpenAI(api_key=os.environ.get("LLM_API_KEY", ""), base_url=base_url, timeout=10)
        resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": "回复 OK"}])
        print(f"[成功] {name}: {resp.choices[0].message.content!r}")
    except Exception as exc:
        print(f"[失败] {name}: {type(exc).__name__} {str(exc)[:60]}")
```

## ⏭ 下一课预告

hello_llm.py 与 hello_safe.py 仍是「半裸奔」状态：重试逻辑写死在函数里没法复用、回答再长也只能等最后一次性吐出、token 用量要自己 print。第 2 课我们把 ask_llm 升级成 LLMClient——指数退避自动重试、流式逐字输出、token 自动记账，后面 13 课全部踩在这个类上。
""",
    },
    {
        "title": "第 2 课 · 封装 LLM 客户端：重试、流式与 Token 统计",
        "summary": "限流与网络抖动是常态而非意外。本课封装 LLMClient：指数退避自动重试 429 与超时、stream_chat 逐字流式输出、total_tokens 自动累计，是后续 13 课统一依赖的地基。",
        "difficulty": 1,
        "tags": ["Agent开发", "openai SDK", "重试机制", "流式输出"],
        "duration_minutes": 20,
        "content": """## 🎯 本课目标

- 说出哪三类异常值得重试（限流 429、连接失败、超时），哪两类重试毫无意义（401 密钥错、400 参数错）
- 手写指数退避：1s → 2s → 4s 加随机抖动，且有最大重试次数上限
- 按全课程统一签名实现 LLMClient：chat()、stream_chat()、total_tokens 三件套
- 用 demo_client.py 验证三大能力，用 test_retry.py 亲眼看到重试日志

## 📦 本课产出

| 文件 | 能力 | 被谁依赖 |
|------|------|----------|
| llm_client.py | 自动重试 + 流式输出 + token 统计 | 第 3~15 课所有需要调用模型的代码 |
| demo_client.py | 三大能力演示脚本 | 学习自查用 |
| test_retry.py | 人为制造断网观察重试 | 学习自查用 |

## 🔗 承接上一步

第 1 课的 hello_llm.py 已经能跑通调用，但它是「裸奔」状态：遇到 429 限流直接崩；回答再长也只能干等最后一次性输出；token 用量要自己 print。更麻烦的是，这些处理逻辑如果散落在后面 13 课的每个脚本里，改一次就得改十三处。本课把它们收进一个 LLMClient 类——第 3 课的对话管理、第 4 课的工具调用、直到第 15 课的毕业项目，所有模型调用都走它。这是全课程的地基文件，接口约定从今天锁定：

- LLMClient(api_key=None, base_url=None, model=None, max_retries=3)
- chat(messages, tools=None, temperature=0.7)：返回 openai 的 ChatCompletion 响应对象
- stream_chat(messages, temperature=0.7)：生成器，逐段 yield 增量文本

## 📖 概念讲解

### 失败不是异常，是日常

大模型 API 面向公网，高峰期限流、网络抖动、服务端排队都随时发生。写 Agent 前必须建立一个认知：**调用失败是常态，健壮性不是锦上添花而是及格线**。但也不是所有失败都该重试：

| 异常类型 | 典型场景 | 重试有用吗 |
|----------|----------|-----------|
| openai.RateLimitError（429） | 每分钟请求数超限 | 有，等一等就恢复 |
| openai.APIConnectionError | 网络抖动、DNS 失败、连接被拒 | 有，再试一次往往就通 |
| openai.APITimeoutError | 网络慢、服务端排队 | 有 |
| openai.AuthenticationError（401） | 密钥错误 | 没用，重试一万次也错 |
| openai.BadRequestError（400） | 参数格式写错 | 没用，得改代码 |

所以重试策略必须是「白名单制」：只捕获值得重试的三类，其余异常立刻抛出，让调用方第一时间看到真正的问题。

### 指数退避与抖动

收到 429 就立刻重发只会火上浇油。正确姿势是指数退避（Exponential Backoff）：每失败一次，等待时间翻倍。

| 第几次重试 | 等待时间 | 说明 |
|-----------|---------|------|
| 第 1 次 | 2**0 = 1 秒 + 抖动 | 快速试探，多数瞬时故障能过 |
| 第 2 次 | 2**1 = 2 秒 + 抖动 | 给服务端喘息窗口 |
| 第 3 次 | 2**2 = 4 秒 + 抖动 | 最后一次机会 |
| 重试用尽 | 抛出异常 | 让上层决定怎么办 |

抖动（jitter）是在等待时间上加一点随机量（比如 0~0.5 秒）。没有它，大量客户端会在同一时刻整齐划一地重试，形成「重试风暴」，反而加剧限流。

### 流式输出与 Token 统计

普通调用要等模型把整段回答生成完才一次性返回；流式（stream=True）则用 SSE 把回答切成一小段一小段推过来，每段叫一个 chunk，里面的 delta.content 是增量文本。对聊天产品来说首字延迟从数秒降到几百毫秒，体验天差地别。

Token 统计则是三件事的基础：算钱（计费按 token）、算长度（上下文窗口有限）、算预算（第 8 课做记忆压缩、第 14 课做成本评估都靠它）。响应对象的 resp.usage 里有 prompt_tokens、completion_tokens、total_tokens 三个字段。

一个要注意的事实：**流式响应默认不带 usage**（多数兼容服务商如此），所以本课只在普通调用里自动记账，流式的用量估算放到第 8 课结合上下文预算一起做。

## 🛠 分步实现

### Step 1：先看看不封装有多难受

```python
# 反面示例：每写一个脚本都要复读一遍重试逻辑
import time

import openai

for attempt in range(3):
    try:
        resp = client.chat.completions.create(model=MODEL, messages=messages)
        break
    except openai.RateLimitError:
        time.sleep(2 ** attempt)      # 手写一遍，下个脚本还得再手写一遍
```

业务逻辑被重试噪声淹没，而且这段代码还有个隐藏 bug：三次都失败时 resp 未定义却继续往下走。封装就是要让这些细节只存在一份、只对一次。

### Step 2：LLMClient 骨架与构造函数

```python
# llm_client.py：全课程统一的大模型客户端
import time
import random

import openai
from openai import OpenAI

from settings import API_KEY, BASE_URL, MODEL


class LLMClient:
    '''对 OpenAI 兼容接口的统一封装：自动重试、流式输出、token 统计。'''

    def __init__(self, api_key=None, base_url=None, model=None, max_retries=3):
        # 不传参数时回退到 settings.py 的默认配置；换服务商只需换构造参数
        self.api_key = api_key or API_KEY
        self.base_url = base_url or BASE_URL
        self.model = model or MODEL
        self.max_retries = max_retries     # 最大重试次数（不含首次请求）
        self.total_tokens = 0              # 跨调用累计的 token 总数
        # 内部持有官方 SDK 客户端，外部再也不用接触 openai 的细节
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
```

设计要点：构造参数全部带默认值且为 None 时回退到 settings.py，这样既满足「一行创建」的顺手，也保留「多服务商并存」的灵活性（第 12 课多智能体会同时用两个客户端）。

### Step 3：chat()——指数退避重试 + token 记账

```python
    def chat(self, messages, tools=None, temperature=0.7):
        # 普通调用：返回 openai 的 ChatCompletion 响应对象
        # 值得重试的异常只有三类：限流、连接失败、超时
        retryable = (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError)

        last_exc = None
        for attempt in range(self.max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                }
                if tools:                     # 第 4 课起会传入工具 schema
                    kwargs["tools"] = tools
                resp = self._client.chat.completions.create(**kwargs)
                if resp.usage is not None:    # 正常响应一定带 usage
                    self.total_tokens += resp.usage.total_tokens
                return resp
            except retryable as exc:
                last_exc = exc
                delay = 2 ** attempt          # 1s、2s、4s：指数退避
                delay += random.uniform(0, 0.5)   # 抖动：避免大家同时重试
                print(f"[LLMClient] 请求失败（{type(exc).__name__}），{delay:.1f}s 后第 {attempt + 1} 次重试")
                time.sleep(delay)

        # 重试用尽：把最后一次异常原样抛给调用方
        raise last_exc
```

三个细节值得咀嚼：其一，401、400 不在白名单里，会立刻穿透 try 抛出，绝不浪费 7 秒等待；其二，tools 参数从今天起就预留，第 4 课直接可用，接口不必再改；其三，raise last_exc 而不是 return None，让调用方明确知道「失败了」而不是拿到一个需要判空的返回值。

### Step 4：stream_chat()——逐段吐字

```python
    def stream_chat(self, messages, temperature=0.7):
        # 流式调用：生成器，逐段 yield 增量文本；调用方 for piece in ... 即可
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            # 流的末尾可能有只携带结束信息的空块，此时 choices 是空列表
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:       # 有的块只带 role 不带 content
                yield delta.content
```

生成器是 Python 的看家本领：yield 让函数「暂停-继续」，每收到一个 chunk 就吐出一段文本，调用方用 for 循环即可逐字打印，内存里永远只握着一小段。

### Step 5：demo_client.py 一次验证三能力

```python
# demo_client.py：验证 LLMClient 的三大能力
import time

from llm_client import LLMClient

llm = LLMClient()

# --- 能力 1：普通调用，token 自动记账 ---
resp = llm.chat([{"role": "user", "content": "用一句话解释什么是 API"}])
print("普通回答:", resp.choices[0].message.content)
print("累计 token:", llm.total_tokens)

# --- 能力 2：流式输出，逐字打印，首字更快 ---
print("流式回答: ", end="", flush=True)
start = time.perf_counter()
first_at = None
chars = 0
for piece in llm.stream_chat([{"role": "user", "content": "讲一个 20 字以内的冷笑话"}]):
    if first_at is None:
        first_at = time.perf_counter() - start   # 记录首字延迟
    print(piece, end="", flush=True)
    chars += len(piece)
print()
print(f"共 {chars} 字，首字延迟约 {first_at:.2f}s")

# --- 能力 3：换服务商 = 换两个构造参数（对应密钥需自备） ---
glm = LLMClient(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-flash",
)
print("GLM 客户端就绪:", glm.model, "| 与 DeepSeek 客户端互不影响")
```

### Step 6：test_retry.py 亲眼看见重试

```python
# test_retry.py：故意连一个不存在的本地端口，稳定制造 APIConnectionError
from llm_client import LLMClient

bad = LLMClient(base_url="http://localhost:9", max_retries=3)
try:
    bad.chat([{"role": "user", "content": "你好"}])
except Exception as exc:
    # 重试 3 次全部失败后，最后一次异常被原样抛出
    print("重试用尽，最终失败:", type(exc).__name__)
print("预期：看到 3 条重试日志，共等待约 1+2+4=7 秒")
```

本机不存在的端口会让连接立刻被拒，这比「拔网线」可控得多，是演示重试最安全的实验。

## ▶️ 运行效果

```text
$ python demo_client.py
普通回答: API 是不同软件之间约定好的调用接口，让程序互相「说上话」。
累计 token: 46
流式回答: 为什么程序员分不清万圣节和圣诞节？因为 OCT 31 == DEC 25。
共 33 字，首字延迟约 0.41s
GLM 客户端就绪: glm-4-flash | 与 DeepSeek 客户端互不影响
```

```text
$ python test_retry.py
[LLMClient] 请求失败（APIConnectionError），1.2s 后第 1 次重试
[LLMClient] 请求失败（APIConnectionError），2.3s 后第 2 次重试
[LLMClient] 请求失败（APIConnectionError），4.4s 后第 3 次重试
重试用尽，最终失败: APIConnectionError
预期：看到 3 条重试日志，共等待约 1+2+4=7 秒
```

（输出因模型而异；重试日志的延迟小数位含随机抖动。）

## ⚠️ 常见坑

1. **现象**：401 也触发重试，白白卡 7 秒。**原因**：except Exception 全捕全重试。**解法**：只捕获 RateLimitError、APIConnectionError、APITimeoutError 三类，其余直接抛。
2. **现象**：服务端长时间故障时程序永远不返回。**原因**：重试没有上限或写成了 while True。**解法**：max_retries 封顶 + 循环结束 raise last_exc，把决定权交还上层。
3. **现象**：流式打印偶发 IndexError。**原因**：流末尾的空块 choices 为空列表，直接取 [0] 越界。**解法**：先判 if not chunk.choices: continue。
4. **现象**：以为 total_tokens 是单次消耗，越算越糊涂。**原因**：它是跨调用累计值。**解法**：看单次用 resp.usage.total_tokens，看进程总账用 self.total_tokens，语义要分开。
5. **现象**：在 stream_chat 里找不到 usage。**原因**：流式响应默认不带 usage（为 None）。**解法**：不要在流式里硬取 usage；需要流式用量时先估算，第 8 课给出工程化方案。

## ✍️ 课后练习

1. （易）给 chat() 增加 timeout 参数并透传给 create()，把超时调到 1 秒感受 APITimeoutError 与重试的配合。参考骨架：

```python
def chat(self, messages, tools=None, temperature=0.7, timeout=60):
    # ...原逻辑不变，组装 kwargs 时加一行：
    kwargs["timeout"] = timeout      # 单位：秒
```

2. （中）给 LLMClient 增加 self.calls 列表：每次调用成功后追加一个 (model, tokens) 元组，失败也记录 (model, -1)，再加一个 report() 方法打印调用次数、成功次数、token 总量。参考骨架：

```python
# 在 chat() 成功分支里追加记录
self.calls.append((self.model, resp.usage.total_tokens))
# 在 except retryable 分支里记录失败
self.calls.append((self.model, -1))

def report(self):
    # 打印调用小结：总次数、成功次数、token 总量
    ok = [c for c in self.calls if c[1] > 0]
    print(f"共 {len(self.calls)} 次调用，成功 {len(ok)} 次，token 总量 {sum(c[1] for c in ok)}")
```
3. （难）写 estimate_tokens(text) 函数粗估中文文本的 token 数（经验值：1 个汉字约 1.5 个 token，英文约 4 个字符 1 个 token），并用它给 stream_chat 做「流式用量估算」——生成器结束后把估算值累加进 total_tokens。

## ⏭ 下一课预告

模型有个反直觉的事实：它完全无状态，所谓多轮对话只是客户端每轮把全部历史重发一遍。第 3 课我们写 Conversation 类管好历史，并做出第一个能连续聊天、流式回答的命令行助手 chat_cli.py。
""",
    },
    {
        "title": "第 3 课 · 系统提示词与多轮对话管理",
        "summary": "模型本身无状态，多轮对话靠客户端每轮重发全部历史。本课实现 Conversation 管理历史与四种角色消息，讲透 system prompt 如何塑造行为，并写出第一个流式命令行聊天助手。",
        "difficulty": 1,
        "tags": ["Agent开发", "多轮对话", "系统提示词", "CLI"],
        "duration_minutes": 20,
        "content": """## 🎯 本课目标

- 用实验证明「模型无状态」：两次独立调用互不相识
- 说清 system / user / assistant / tool 四种角色的分工、顺序与配对关系
- 按全课程统一签名实现 Conversation：user / assistant / tool / get_messages / clear
- 写出 chat_cli.py：流式打印的命令行多轮聊天助手，/exit 退出

## 📦 本课产出

| 文件 | 能力 | 被谁依赖 |
|------|------|----------|
| conversation.py | 多轮对话历史管理 | 第 4 课的 tool 消息、第 6 课 Agent 内核 |
| chat_cli.py | 第一个可连续对话的 CLI | 你后续所有实验的试验台 |
| raw_multi_turn.py | 无状态实验脚本 | 一次性理解用 |

## 🔗 承接上一步

第 2 课的 LLMClient 已经把「调模型」变得可靠：重试、流式、token 记账全自动。但它每次都要求调用方手动拼一个 messages 列表——聊第二句时第一句去哪了？system 要不要每次都带？本课在 LLMClient 之上加一层 Conversation 专门管历史，再用几十行代码包出一个命令行聊天助手。第 4 课 Function Calling 要往历史里塞的 tool 消息，就直接复用本课的 Conversation.tool() 方法。

## 📖 概念讲解

### 反直觉的事实：模型是无状态的

很多人以为「对话」是服务器替你记着。真相是：**API 不保存任何会话状态，每一次请求都是独立的**。所谓多轮对话，是客户端每轮把全部历史重新发送一遍。历史像滚雪球：

```text
第 1 轮请求： [system, user:我叫小明]                          → assistant:你好小明
第 2 轮请求： [system, user:我叫小明, assistant:你好小明, user:我叫啥?] → assistant:小明
第 3 轮请求： [system, ...以上全部..., user:...]               → ...
                  ↑ 历史每轮整体重发，越滚越大
```

这就是「模型记得你」的全部真相——不是它记得，是你的代码记得。也立刻能推出两个结论：第一，历史必须由客户端管理，这正是本课 Conversation 的职责；第二，历史越长，每次请求的输入 token 越多、越贵、越容易撞上上下文上限，这为第 8 课的「上下文预算与压缩」埋下伏笔。

### 四种角色各司其职

| role | 谁在说 | 典型内容 | 顺序约定 |
|------|--------|----------|----------|
| system | 程序员的设定 | 人设、规则、输出格式 | 永远第一条，只出现一次 |
| user | 终端用户 | 问题、指令 | 追加在历史末尾 |
| assistant | 模型 | 上一轮的回答 | 紧跟在触发它的 user 之后 |
| tool | 你的代码 | 工具执行结果 | 必须与 assistant 消息里的 tool_call 配对（第 4 课） |

### system prompt 如何塑造行为

system prompt 是你在模型「开口前」递给它的剧本，三类要素最有用：

| 要素 | 作用 | 示例 |
|------|------|------|
| 人设 | 定语气与专业域 | 你是严谨的中文天气助手 |
| 规则 | 划行为边界 | 不确定就说不知道；回答不超过 100 字 |
| 输出格式 | 方便程序解析 | 每次以 JSON 格式回答，含 answer 字段 |

对 Agent 来说 system prompt 更是「操作手册」：第 6 课的 ReAct 循环会在 system 里告诉模型「你有这些工具、该怎么思考」；第 12 课的多智能体里，每个角色（Worker、Reviewer）的区别本质上就是 system prompt 的区别。

## 🛠 分步实现

### Step 1：先做无状态实验

```python
# raw_multi_turn.py：证明「模型不记得你」
from openai import OpenAI

from settings import API_KEY, BASE_URL, MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def ask(content):
    # 每次只发当前这一句，不带任何历史
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content}],
    )
    return resp.choices[0].message.content


print("A:", ask("我叫小明，请记住我的名字。"))
print("B:", ask("我叫什么名字？"))    # 大概率答不上来，甚至瞎编一个
```

运行后 B 的回答几乎不会是「小明」——两次请求对模型来说毫无关系，这就是无状态。

### Step 2：正确姿势是把历史一起发

```python
# 修复版：把两轮内容放进同一个 messages 再请求
messages = [
    {"role": "user", "content": "我叫小明，请记住我的名字。"},
    {"role": "user", "content": "我叫什么名字？"},
]
resp = client.chat.completions.create(model=MODEL, messages=messages)
print(resp.choices[0].message.content)    # 这次答对：小明
```

同一秒钟，「失忆」与「记得」只差一个历史列表。接下来要做的，就是让历史管理这件事自动化。

### Step 3：conversation.py——历史管理类

```python
# conversation.py：多轮对话历史管理（全课程复用）
class Conversation:
    '''维护 messages 列表：system 固定第一条，其余按时间顺序追加。'''

    def __init__(self, system_prompt=""):
        self._messages = []
        if system_prompt:
            # 关键约定：system 永远放第一条，且整个会话只写这一次
            self._messages.append({"role": "system", "content": system_prompt})

    def user(self, text):
        # 追加一条用户消息
        self._messages.append({"role": "user", "content": text})

    def assistant(self, text):
        # 追加一条模型回复（由调用方拿到完整回复后写入）
        self._messages.append({"role": "assistant", "content": text})

    def tool(self, tool_call_id, name, content):
        # 追加一条工具结果消息：第 4 课 Function Calling 的主角
        # tool_call_id 必须与 assistant 消息里对应 tool_call 的 id 一一配对
        self._messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": content,
        })

    def get_messages(self):
        # 返回浅拷贝：外部拿到的是副本，误改不会污染内部历史
        return list(self._messages)

    def clear(self):
        # 清空对话；保留 system 人设，让「新开一轮」不必重新设定
        if self._messages and self._messages[0]["role"] == "system":
            self._messages = [self._messages[0]]
        else:
            self._messages = []
```

两个设计决策说明：get_messages 返回浅拷贝是为了防御性——外部循环里万一顺手改了列表，内部历史不至于被污染；clear 保留 system 是因为「清空对话」通常意味着「换个话题」而不是「换个人设」。

### Step 4：chat_cli.py——第一个聊天助手

```python
# chat_cli.py：命令行多轮聊天助手（流式输出）
from conversation import Conversation
from llm_client import LLMClient

SYSTEM_PROMPT = '''你叫小助，是一个简洁友好的中文助手。
规则：
1. 每次回答不超过 100 字；
2. 不确定的事直接说不知道，绝不编造。'''


def main():
    conv = Conversation(system_prompt=SYSTEM_PROMPT)
    llm = LLMClient()
    print("开始对话吧！输入 /exit 退出。")

    while True:
        try:
            text = input("\n你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/exit":
            break

        conv.user(text)                    # 1) 用户消息进历史
        print("小助 > ", end="", flush=True)
        reply = ""                         # 2) 流式接收并逐字打印
        for piece in llm.stream_chat(conv.get_messages()):
            print(piece, end="", flush=True)
            reply += piece
        print()
        # 3) 关键一步：流式打印结束后，把完整回复写回历史
        #    （漏掉这步，下一轮模型就「失忆」了）
        conv.assistant(reply)

    print(f"会话结束，共 {len(conv.get_messages())} 条消息，累计 token：{llm.total_tokens}")


if __name__ == "__main__":
    main()
```

主循环的三拍节奏要形成肌肉记忆：user() 进历史 → stream_chat 拿 get_messages() 的快照去请求 → assistant() 写回完整回复。任何一拍缺失，多轮对话就会露馅。

### Step 5：脚本式连聊验证（不依赖终端交互）

chat_cli.py 需要终端交互，不方便自动化验证。同样的三拍节奏写进脚本，就能一行命令回归测试「多轮记忆」：

```python
# scripted_multi_turn.py：脚本式连聊两轮，验证历史真的被带上了
from conversation import Conversation
from llm_client import LLMClient

conv = Conversation(system_prompt="你是一个简洁的中文助手。")
llm = LLMClient()

for question in ["我叫小明，请记住我的名字。", "我叫什么名字？"]:
    conv.user(question)                    # 第一拍：用户消息进历史
    reply = ""                             # 第二拍：带着全部历史请求
    for piece in llm.stream_chat(conv.get_messages()):
        reply += piece
    print(f"你: {question}")
    print(f"小助: {reply}")
    conv.assistant(reply)                  # 第三拍：完整回复写回历史

print("第二轮若能答出「小明」，说明多轮记忆闭环工作正常")
```

## ▶️ 运行效果

```text
$ python chat_cli.py
开始对话吧！输入 /exit 退出。

你 > 你叫什么名字？
小助 > 我叫小助，一个简洁友好的中文助手，很高兴为你服务。

你 > 我刚才问你什么了？
小助 > 你刚才问的是「我叫什么名字」——哦不对，你问的是我叫什么名字。

你 > /exit
会话结束，共 6 条消息，累计 token：587
```

（输出因模型而异。第二条提问能被正确回答，正是因为上一轮的问答都躺在历史里被整体重发了。）

## ⚠️ 常见坑

1. **现象**：聊几十轮后请求报错或越来越慢、账单飙升。**原因**：历史无限增长——每轮重发全部历史，token 线性上涨，最终撞上下文窗口上限。**解法**：心里先有数，第 8 课实现上下文预算与对话压缩。
2. **现象**：模型人设错乱或行为漂移。**原因**：每轮都往 messages 里追加一条新的 system，或者把 system 放在了中间。**解法**：system 只放第一条且只放一次。
3. **现象**：用户一句话就让模型「改规矩」。**原因**：把用户输入用 f-string 拼进了 system prompt，等于让用户改写你的剧本（提示注入）。**解法**：用户输入永远走 user 角色，system 只由代码控制。
4. **现象**：模型下一轮「忘了」自己刚说过什么。**原因**：流式打印后忘了 conv.assistant(reply) 写回历史。**解法**：打印结束立即写回，三拍节奏缺一不可。
5. **现象**：外部改了 get_messages() 的返回值，历史却没变（或相反）。**原因**：混淆了浅拷贝与内部列表。**解法**：约定只通过 user/assistant/tool 方法修改历史，get_messages 只读。

## ✍️ 课后练习

1. （易）给 chat_cli.py 加 /clear 命令：清空历史但保留人设。参考：

```python
        if text == "/clear":
            conv.clear()
            print("（已清空对话历史，人设保留）")
            continue
```

2. （中）再加一个 /history 命令，打印每条消息的序号、role 和内容前 30 个字符，直观感受「历史滚雪球」：

```python
        if text == "/history":
            for i, m in enumerate(conv.get_messages()):
                preview = (m.get("content") or "(无文本内容)")[:30]
                print(f"{i}. [{m['role']}] {preview}")
            continue
```

3. （难）把 SYSTEM_PROMPT 改成要求「每次回答必须是合法 JSON，含 answer 与 confidence 两个字段」，观察遵守程度；再故意写入一条互相矛盾的规则（比如「回答不超过 10 字」与「必须完整解释原理」），观察模型如何取舍，并写两行笔记记录结论。

## ⏭ 下一课预告

会聊天只是及格线。第 4 课 Function Calling：让模型输出「我要调用 get_weather(北京)」这样的结构化指令，由你的代码执行后把结果喂回去——这是 Agent 与聊天机器人的真正分水岭。
""",
    },
    {
        "title": "第 4 课 · 手写 Function Calling：让模型学会用工具",
        "summary": "Function Calling 是 Agent 的心脏：模型只输出「要调用什么工具」的结构化意图，执行权永远在你手里。本课手写工具 schema 与完整调用循环，吃透消息回传顺序与 finish_reason 的含义。",
        "difficulty": 2,
        "tags": ["Agent开发", "Function Calling", "工具调用", "openai SDK"],
        "duration_minutes": 25,
        "content": """## 🎯 本课目标

- 建立「模型不执行函数，只输出调用意图」的核心认知，明白执行权在你手里的安全意义
- 手写符合 JSON Schema 规范的 tools 参数，说清 name / description / parameters / required 各自作用
- 跑通完整循环：请求 → tool_calls → 本地执行 → role 为 tool 的消息回传 → 再请求 → 最终回答
- 吃透两个关键点：assistant 的 tool_calls 消息必须先 model_dump() 写回历史；finish_reason 的含义

## 📦 本课产出

| 产出 | 说明 |
|------|------|
| manual_tool_call.py | 手写 Function Calling 完整可运行脚本 |
| 一张全课程反复引用的流程图 | 第 6 课 Agent 的 ReAct 循环就是它的工程化版本 |

## 🔗 承接上一步

第 3 课之后，我们的助手能连续聊天了，但它只会「说」不会「做」——问它天气，它只能坦白「我查不了」或者编一个。本课给它第一双手：Function Calling。第 3 课 Conversation 类里预留的 tool() 方法（往历史里追加 role 为 tool 的消息）马上就要派上用场；第 5 课再把本课手写的 schema 自动化。写完这课你会发现：所谓 Agent 循环，拆开看就是本课这个 while 循环的加强版。

## 📖 概念讲解

### 最重要的认知：模型不执行函数

Function Calling 容易被误解成「模型在服务器上帮我跑了函数」。真相是：

- 模型只做一件事：**根据你的问题，输出一段结构化数据，表达「我想调用 get_weather，参数是 北京」**
- 函数从不执行——它只是模型的一个「点菜」动作
- 真正执行的是你的 Python 代码，执行完把结果作为消息回传，模型再基于结果继续说话

这个设计正是安全性的基石：**执行权永远在你手里**。你可以拒绝危险请求、加白名单、做预算控制（第 13 课的护栏全部建立在这一点上）。

### 完整流程图（全课程反复出现）

```text
   你（Python 代码）                                模型（deepseek-chat）
        │                                                │
        │ ① 发送 messages + tools(schema)                │
        ├───────────────────────────────────────────────▶│
        │                                                │ 思考：该查天气了
        │ ② 返回 tool_calls（结构化调用意图）              │
        │◀──── get_weather({"city": "北京"}) ─────────────┤
        │                                                │
        │ ③ 你在本地真正执行 get_weather("北京")
        │                                                │
        │ ④ 把结果以 role:"tool" 消息回传                  │
        ├───────────────────────────────────────────────▶│
        │                                                │ 思考：有数据了，组织回答
        │ ⑤ 返回最终自然语言回答                           │
        │◀──────────── content:"北京今天晴…" ─────────────┤
```

注意 ①→② 和 ④→⑤ 各是一次独立的模型请求：每次都要把之前全部消息（包括工具结果）重发过去——这正是第 3 课「无状态」的直接体现。

### tools schema：给模型看的「工具说明书」

| 字段 | 作用 |
|------|------|
| type: "function" | 固定值，声明这是函数型工具 |
| function.name | 工具名，模型会在 tool_calls 里原样输出它 |
| function.description | 决定模型「何时想到用这个工具」，写得越准调用越准 |
| function.parameters | JSON Schema：有哪些参数、类型、说明 |
| required | 必填参数列表 |

### finish_reason：模型这次想干什么

| finish_reason | 含义 | 你该做什么 |
|---------------|------|-----------|
| stop | 正常说完 | 直接展示 content |
| tool_calls | 模型想用工具 | 执行并把结果回传，继续循环 |
| length | 被 max_tokens 截断 | 加大上限或让它接着说 |
| content_filter | 触发内容过滤 | 按业务策略处理 |

本课代码用 if msg.tool_calls 分支判断（比判断 finish_reason 更直接），但你要知道两者说的是同一件事。

## 🛠 分步实现

### Step 1：本地工具函数——真正干活的人

```python
# manual_tool_call.py：手写 Function Calling 完整流程
import json

from openai import OpenAI

from settings import API_KEY, BASE_URL, MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ---------- 第 1 步：本地工具函数（真正干活的是我们，不是模型） ----------
def get_weather(city):
    # 演示用：返回写死的示例数据；真实项目里这里会请求天气 API 或读本地缓存
    fake_db = {
        "北京": {"weather": "晴", "temp": "12~22°C", "wind": "西北风 3 级"},
        "上海": {"weather": "小雨", "temp": "16~20°C", "wind": "东风 2 级"},
        "广州": {"weather": "多云", "temp": "21~28°C", "wind": "南风 2 级"},
    }
    return fake_db.get(city, {"weather": "暂无该城市数据", "temp": "-", "wind": "-"})


def calculator(a, b, op):
    # 第二个工具：四则运算，用于演示一次对话调用多个不同工具
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ValueError("除数不能为 0")
        return a / b
    raise ValueError(f"不支持的运算符: {op}")
```

注意 calculator 里我们主动抛异常——稍后主循环会演示「工具出错也要回话」的处理方式，这是新手最容易漏掉的一环。

### Step 2：手写 tools schema——把函数翻译给模型听

```python
# ---------- 第 2 步：手写 schema（第 5 课将自动化这一步） ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气，包括天气现象、气温范围和风力",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，例如：北京",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算两个数的四则运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数"},
                    "b": {"type": "number", "description": "第二个数"},
                    "op": {"type": "string", "description": "运算符：+ - * / 之一"},
                },
                "required": ["a", "b", "op"],
            },
        },
    },
]
```

数一数：两个工具用了 40 多行。schema 占了全部篇幅的九成，而且全靠手抄、极易抄错——这正是下一课要用装饰器自动化掉的痛点。

### Step 3：先偷看一眼模型返回了什么

```python
# 调试技巧：第一次写 Function Calling 时，先把结构打印出来再往下写
# print(resp.choices[0].finish_reason)      # tool_calls
# print(msg.model_dump())
# 典型输出长这样（节选）：
# {'role': 'assistant', 'content': None,
#  'tool_calls': [{'id': 'call_0_abc123', 'type': 'function',
#    'function': {'name': 'get_weather', 'arguments': '{"city": "北京"}'}}]}
```

三个字段记住：tc.id 是这次调用的唯一编号（回传结果时必须带上）；tc.function.name 是工具名；tc.function.arguments 是**JSON 字符串**（不是字典！）。

### Step 4：完整主循环——Agent 的雏形

```python
# ---------- 第 3 步：完整循环：问模型 → 执行工具 → 回传 → 再问 ----------
messages = [
    {"role": "system", "content": "你是天气与计算小助手，回答前先用工具查询真实数据。"},
    {"role": "user", "content": "北京和上海今天哪个更热？另外帮我算算 128 乘 4 减 100。"},
]

while True:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
    )
    msg = resp.choices[0].message

    if msg.tool_calls:
        # 关键点 1：先把带 tool_calls 的 assistant 消息原样写回历史！
        # 漏掉这一步，下一条 tool 消息就找不到主人，请求会直接报 400
        messages.append(msg.model_dump())

        # 关键点 2：模型可能一次要求调用多个工具，必须逐个回答
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)   # arguments 是 JSON 字符串
            print(f"[工具调用] {name}({args})")

            # 路由：按名字找到本地函数并执行；出错也把错误当结果回传
            try:
                if name == "get_weather":
                    result = get_weather(**args)
                elif name == "calculator":
                    result = calculator(**args)
                else:
                    result = {"error": f"未注册的工具: {name}"}
            except Exception as exc:
                # 工具异常不崩溃：把错误信息作为「工具结果」喂回去，模型会自行调整
                result = {"error": f"{type(exc).__name__}: {exc}"}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,     # 与 assistant 消息里的调用一一配对
                "name": name,
                "content": json.dumps(result, ensure_ascii=False),
            })
        # 带着全部工具结果继续 while 循环，让模型决定下一步
        continue

    # 没有 tool_calls：模型给出了最终回答
    print("助手:", msg.content)
    print("结束原因:", resp.choices[0].finish_reason)
    break
```

逐段读：while True 的每一圈是一次完整的模型请求；if msg.tool_calls 成立时，先 model_dump() 写回 assistant 消息，再为每一个 tool_call 追加一条 role 为 tool 的消息，然后 continue 进入下一圈；只有当模型不再要求工具时，才打印 content 并 break。这个「请求-执行-回传-再请求」的循环，就是第 6 课 Agent 类的 run() 方法的原型。

## ▶️ 运行效果

```text
$ python manual_tool_call.py
[工具调用] get_weather({'city': '北京'})
[工具调用] get_weather({'city': '上海'})
[工具调用] calculator({'a': 128, 'b': 4, 'op': '*'})
[工具调用] calculator({'a': 512, 'b': 100, 'op': '-'})
助手: 今天上海（16~20°C）比北京（12~22°C）的最高温略低、最低温更高，
     综合来看北京白天更热、昼夜温差更大；至于计算，128×4−100 = 412。
结束原因: stop
```

（输出因模型而异：模型可能把两次 calculator 调用合并成一次先乘后减的拆解方式，也可能分更多轮调用。）

## ⚠️ 常见坑

1. **现象**：报 400 invalid_request_error，提示 tool 消息没有对应的 tool_calls。**原因**：忘了先 messages.append(msg.model_dump()) 写回 assistant 消息，tool 消息成了「没有主人的回复」。**解法**：永远先写回 assistant 消息，再追加 tool 消息，顺序不可颠倒。
2. **现象**：TypeError: the JSON object must be str, bytes or bytearray, not dict，或 string indices must be integers。**原因**：把 arguments 当字典用——它是 JSON **字符串**。**解法**：args = json.loads(tc.function.arguments)。
3. **现象**：只回答了一个工具调用，下一轮报 400 或模型混乱。**原因**：模型一次返回多个 tool_calls，你只 append 了一条 tool 消息。**解法**：for tc in msg.tool_calls 逐个执行、逐个回答，一条都不能少。
4. **现象**：工具一抛异常整个程序崩溃。**原因**：网络请求、文件读取都可能失败，没做异常处理。**解法**：try/except 把错误字符串当作工具结果回传——模型会读到错误并自行调整参数重试，这本身就是 Agent 自纠能力的雏形。
5. **现象**：模型不调用工具，或调用时传错参数。**原因**：description 太敷衍（比如只写「工具」），或者 schema 里的名字与本地函数对不上。**解法**：description 写清「什么时候该用、参数什么含义」；名字严格一致；第 5 课让 schema 从代码自动生成，从根上消灭手抄错误。

## ✍️ 课后练习

1. （易）把用户问题改成「现在几点了？北京天气怎样？」，并新增一个 get_now_time 工具（返回当前时间字符串），观察模型是否在一次响应里同时要求两个工具。

```python
# 练习提示：新增工具的 schema 骨架
{"type": "function", "function": {
    "name": "get_now_time",
    "description": "获取当前日期时间",
    "parameters": {"type": "object", "properties": {}, "required": []},
}}
```

2. （中）把 calculator 的除法改成传 op="/" 且 b=0 的提问（比如「帮我算 5 除以 0」），观察错误字符串回传后模型如何向用户解释——亲眼看一遍「异常回传自纠」机制。
3. （难）把主循环封装成函数 run_with_tools(question, tools, max_rounds=6) -> str：返回最终回答，并统计总共请求了几次模型。想一想为什么必须有 max_rounds 上限——它就是第 6 课 Agent(max_steps=8) 的雏形。

## ⏭ 下一课预告

手写一个工具的 schema 要 20 行，10 个工具呢？第 5 课用 inspect 与类型注解自动生成 JSON Schema：@tool 装饰器加 ToolBox，让「注册一个工具」变成给函数贴一张标签的事。
""",
    },
    {
        "title": "第 5 课 · 工具注册系统：@tool 装饰器与 ToolBox",
        "summary": "手写 schema 繁琐易错？本课用 inspect 与类型注解自动生成 JSON Schema：@tool 装饰器加 ToolBox，注册、导出、执行三件套，异常回传让模型自纠，为第 6 课 Agent 内核铺路。",
        "difficulty": 2,
        "tags": ["Agent开发", "装饰器", "JSON Schema", "工具注册"],
        "duration_minutes": 22,
        "content": """## 🎯 本课目标

- 说清第 4 课手写 schema 的三大痛点：繁琐、易抄错、与函数本体脱节
- 掌握用 inspect.signature 加类型注解自动生成 JSON Schema 的完整方法
- 按全课程统一签名实现 @tool 装饰器与 ToolBox：register / get_schemas / execute
- 让工具异常自动转成错误字符串回传给模型，实现「自纠」闭环

## 📦 本课产出

| 文件 | 能力 | 被谁依赖 |
|------|------|----------|
| toolbox.py | @tool 装饰器 + ToolBox 注册/导出/执行 | 第 6 课 Agent 的直接部件 |
| demo_toolbox.py | 注册三个工具并打印自动生成的 schema | 学习自查用 |

## 🔗 承接上一步

第 4 课我们手写了两个工具的 schema，花了 40 多行，还得维护「schema 名字」与「本地函数」的路由 if/elif——每加一个工具都要三处同步：写函数、抄 schema、加路由。本课把这三处收敛成一处：函数本身带着签名、类型注解和 docstring，这些信息足够程序自动生成 schema；ToolBox 接管注册与执行，路由 if/elif 彻底消失。第 6 课的 Agent(llm, toolbox) 将直接吃下今天的 ToolBox，这是进入 Agent 内核前最后一块拼图。

## 📖 概念讲解

### schema 从哪来？函数自己就有

一个函数天生携带三份信息：签名里有参数名，注解里有类型，docstring 里有用途说明。用标准库 inspect 把它们读出来，就能拼出 JSON Schema：

```python
import inspect

def add(a: float, b: float = 1.0):
    '''计算两个数的和'''
    pass

sig = inspect.signature(add)
for name, param in sig.parameters.items():
    print(name, param.annotation, param.default)
# a <class 'float'> <class 'inspect._empty'>   → 无默认值 → required
# b <class 'float'> 1.0                        → 有默认值 → 可选
```

有默认值的参数不该进 required——这正是从签名里免费读出来的语义。

### 类型映射表

JSON Schema 的类型名与 Python 不一致，需要一张映射表：

| Python 注解 | JSON Schema | 取值示例 |
|-------------|-------------|----------|
| str | string | "北京" |
| int | integer | 3 |
| float | number | 3.14 |
| bool | boolean | true |
| list | array | [1, 2] |
| dict | object | {"k": "v"} |

注解缺失时只能退化为 string——这是新手最常见的坑，本课结尾专门讲。

### @tool 与 ToolBox 的分工

| 组件 | 职责 |
|------|------|
| @tool 装饰器 | 给函数挂上 _tool_name / _tool_description 元数据（可覆盖缺省值） |
| ToolBox.register | 把带元数据的函数收进名册 |
| ToolBox.get_schemas | 一键导出 OpenAI tools 格式，直接传给 chat(..., tools=...) |
| ToolBox.execute | 按名字执行工具，任何异常都转成错误字符串返回给模型 |

## 🛠 分步实现

### Step 1：类型映射表与 schema 生成器

```python
# toolbox.py：工具注册系统——@tool 装饰器 + ToolBox
import json
import inspect
import functools

# Python 类型 -> JSON Schema 类型的映射表
TOOL_SCHEMA_TYPES = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _schema_from_signature(func):
    # 由函数签名自动生成 (properties, required, description) 三元组
    sig = inspect.signature(func)
    properties = {}
    required = []
    for param_name, param in sig.parameters.items():
        if param_name == "self":        # 万一注册的是实例方法，跳过 self
            continue
        # 注解缺失时退化为 string：能跑，但模型可能传错类型（见常见坑 3）
        json_type = TOOL_SCHEMA_TYPES.get(param.annotation, "string")
        prop = {"type": json_type}
        if param.default is not inspect.Parameter.empty:
            prop["default"] = param.default    # 有默认值：写进 schema 并视为可选
        else:
            required.append(param_name)
        properties[param_name] = prop
    # docstring 第一行作为工具描述
    doc = inspect.getdoc(func) or ""
    description = doc.splitlines()[0] if doc else ""
    return properties, required, description
```

这一步是全课的心脏：遍历签名参数，逐个翻译成 JSON Schema 的 property；default 为 inspect.Parameter.empty 说明没有默认值，归入 required；docstring 第一行提取为描述。

### Step 2：@tool 装饰器——贴一张标签

```python
def tool(name=None, description=None):
    # 用法：@tool() 或 @tool(name="xxx", description="yyy")，括号不能省
    def decorator(func):
        doc = inspect.getdoc(func) or ""
        first_line = doc.splitlines()[0] if doc else ""
        # 缺省规则：工具名取函数名，描述取 docstring 首行；显式传入则覆盖
        func._tool_name = name or func.__name__
        func._tool_description = description or first_line

        @functools.wraps(func)      # 保留原函数的名字、签名等元信息
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # 元信息也要挂到 wrapper 上，注册与导出 schema 时都读得到
        wrapper._tool_name = func._tool_name
        wrapper._tool_description = func._tool_description
        return wrapper
    return decorator
```

为什么装饰器要写成三层？最外层 tool(name=None, description=None) 接收配置；中间层 decorator 接收函数；wrapper 用 functools.wraps 包装原函数——虽然这里只是透传调用，但wraps保住了 __name__ 与签名信息，让 Step 1 的 inspect 在 wrapper 上依然工作正常。

### Step 3：ToolBox——注册、导出、执行三件套

```python
class ToolBox:
    '''工具箱：统一注册、导出 schema、按名执行。'''

    def __init__(self):
        self._tools = {}            # 工具名 -> 可调用对象

    def register(self, func):
        # 注册一个用 @tool 标记过的函数；普通函数也容忍（用函数名兜底）
        name = getattr(func, "_tool_name", func.__name__)
        self._tools[name] = func
        return func                 # 返回原函数，方便在装饰器场景下继续使用

    def get_schemas(self):
        # 导出 OpenAI tools 格式，可直接传给 chat(..., tools=...)
        schemas = []
        for name, func in self._tools.items():
            properties, required, doc_description = _schema_from_signature(func)
            # @tool 显式指定的描述优先于 docstring 自动提取
            description = getattr(func, "_tool_description", "") or doc_description
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })
        return schemas

    def execute(self, name, arguments_json):
        # 按名字执行工具；任何异常都转成字符串回传给模型，让它自行纠正
        if name not in self._tools:
            available = "、".join(self._tools) if self._tools else "（空）"
            return f"错误：未注册工具「{name}」。当前可用工具：{available}"
        func = self._tools[name]
        try:
            args = json.loads(arguments_json) if arguments_json else {}
            result = func(**args)
            if isinstance(result, str):
                return result
            try:
                return json.dumps(result, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(result)       # 不可序列化对象兜底转字符串
        except Exception as exc:
            # 注意：这里故意不 raise！错误信息是给模型看的反馈，
            # 模型读到后会修正参数再次调用——这就是自纠闭环
            return f"工具 {name} 执行失败：{type(exc).__name__}: {exc}"
```

execute 的三个分支值得记住：名字不存在 → 返回可用工具列表提示；结果可 JSON 序列化 → ensure_ascii=False 保留中文；任何异常 → 错误字符串原样回传。对模型来说，「工具失败的原因」与「工具的正常输出」同样是有效信息。

### Step 4：demo_toolbox.py——见证自动化

```python
# demo_toolbox.py：注册三个工具并打印自动生成的 schema
import json
from datetime import datetime

from toolbox import tool, ToolBox

box = ToolBox()


@tool()
def add(a: float, b: float):
    '''计算两个数的和'''
    return a + b


@tool(description="获取当前日期时间，格式：YYYY-MM-DD HH:MM:SS")
def get_now_time() -> str:
    '''返回服务器当前时间'''
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool()
def get_weather(city: str):
    '''查询城市天气（演示数据）'''
    return {"city": city, "weather": "晴", "temp": "12~22°C"}


def sub(a: float, b: float):
    '''计算两个数的差'''
    return a - b

box.register(sub)     # 不用装饰器也能注册：register 是公开接口

# 1) 打印自动生成的 schema，和第 4 课手写的对比一下
print(json.dumps(box.get_schemas(), ensure_ascii=False, indent=2))

# 2) 直接执行工具试试
print(box.execute("add", '{"a": 1, "b": 2}'))          # 3
print(box.execute("get_now_time", "{}"))               # 当前时间
print(box.execute("get_weather", '{"city": "北京"}'))   # 中文 JSON 字符串
print(box.execute("not_exist", "{}"))                  # 未注册工具提示
print(box.execute("add", '{"a": 1}'))                  # 缺参数：错误回传给模型
```

同样的信息量，函数本身 4 行搞定，schema 一个字都不用抄。

## ▶️ 运行效果

```text
$ python demo_toolbox.py
[
  {
    "type": "function",
    "function": {
      "name": "add",
      "description": "计算两个数的和",
      "parameters": {
        "type": "object",
        "properties": {
          "a": {"type": "number"},
          "b": {"type": "number"}
        },
        "required": ["a", "b"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_now_time",
      "description": "获取当前日期时间，格式：YYYY-MM-DD HH:MM:SS",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  }
]
3
2026-11-01 10:23:45
{"city": "北京", "weather": "晴", "temp": "12~22°C"}
错误：未注册工具「not_exist」。当前可用工具：add、get_now_time、get_weather、sub
工具 add 执行失败：TypeError: add() missing 1 required positional argument: 'b'
```

（schema 输出为节选，get_weather 与 sub 的条目类似；时间与错误信息因环境而异。）

## ⚠️ 常见坑

1. **现象**：生成的 schema 里 description 是空字符串，模型不知道何时该用这个工具。**原因**：函数没写 docstring，@tool 也没传 description。**解法**：养成习惯——每个工具函数第一行写一句人话 docstring，或显式传 description。
2. **现象**：execute 返回的对象打印出的是类名字符串，模型读到一脸茫然。**原因**：返回了 datetime、自定义类等不可 JSON 序列化的对象，走了 str() 兜底。**解法**：工具返回值统一用 str / int / float / bool / list / dict；时间对象先 strftime 成字符串。
3. **现象**：模型给 int 参数传了 "3"（字符串），函数内部报错。**原因**：参数没写类型注解，schema 里全部退化成 string。**解法**：每个参数都写注解；即便偶尔传错，execute 会把异常回传，模型通常下一轮就能自纠——但你不能依赖运气。
4. **现象**：@tool 不带括号（写成 @tool）直接把函数当成了 name 参数。**原因**：这是带参装饰器，必须先调用再装饰。**解法**：统一写 @tool()；想同时支持两种写法需要额外判断，不建议为省两个字符引入复杂度。
5. **现象**：同名工具后注册的覆盖了先注册的。**原因**：ToolBox 用名字做主键，重复注册静默覆盖。**解法**：工具名保持全局唯一；需要时可在 register 里检查重名并抛错（留给课后练习）。

## ✍️ 课后练习

1. （易）注册一个 multiply(x: float, y: float) 工具并用 execute 调用；再故意传 {"x": 1} 观察错误回传的完整文本。
2. （中）给 ToolBox 加两个方法：names() 返回所有工具名列表；remove(name) 删除工具（不存在时返回 False）。参考骨架：

```python
    def names(self):
        # 返回全部已注册工具名
        return list(self._tools)

    def remove(self, name):
        # 删除指定工具；返回是否删除成功
        return self._tools.pop(name, None) is not None
```

3. （难）用 ToolBox 重写第 4 课的 run_with_tools：主循环里不再有 if/elif 路由，工具执行一律交给 box.execute(name, arguments)。写完后对比两版代码行数——差值就是这套注册系统替你省下的样板代码，第 6 课它将成为 Agent 构造函数的直接参数。

## ⏭ 下一课预告

积木齐了：LLMClient 负责可靠调用，Conversation 负责历史，ToolBox 负责工具。第 6 课把三者组装进 Agent 类——ReAct 循环与终止条件，你的第一个真正意义的 Agent 将在 100 行内诞生。
""",
    },
]
