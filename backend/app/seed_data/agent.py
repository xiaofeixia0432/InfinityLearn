"""大模型 Agent 模块种子数据：《从零手写 AI Agent》15 课渐进式代码实战课程。

课程内容较长，按篇拆分在三个文件中，本文件负责汇合：
- agent_course_a.py：第 1-5 课（环境准备、LLM 客户端、多轮对话、手写 Function Calling、工具注册系统）
- agent_course_b.py：第 6-10 课（Agent 核心循环、实用工具集、短期记忆、长期记忆、RAG）
- agent_course_c.py：第 11-15 课（规划、多智能体、安全护栏、可观测与评估、毕业项目）
"""

from .agent_course_a import ARTICLES_A
from .agent_course_b import ARTICLES_B
from .agent_course_c import ARTICLES_C

MODULE = {
    "code": "agent",
    "name": "大模型 Agent",
    "description": "从零手写 AI Agent 的 15 课渐进式实战：从调用大模型到工具调用、记忆、RAG、规划、多智能体与安全护栏，最终组装出完整的 AssistantCLI 助手。",
    "icon": "🧠",
    "color": "#34d399",
    "sort_order": 10,
    "parent_code": None,
}

ARTICLES = [*ARTICLES_A, *ARTICLES_B, *ARTICLES_C]
