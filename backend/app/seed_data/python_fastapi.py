"""Python FastAPI 后端开发模块种子数据：从第一个接口到可部署的待办事项 API，15 课渐进式实战。"""

MODULE = {
    "code": "python_fastapi",
    "name": "FastAPI 后端开发",
    "description": "从零写一个可部署的待办事项 API：路由、Pydantic v2 校验、依赖注入、SQLAlchemy 2.0 异步、JWT 鉴权、WebSocket、pytest 与 Docker 上线，15 课覆盖现代 Python 后端全链路。",
    "icon": "⚡",
    "color": "#14b8a6",
    "sort_order": 8,
    "parent_code": "python",
}

ARTICLES = [
    {
        "title": "第 1 课：FastAPI 是什么与第一个接口",
        "summary": "建好虚拟环境、配好国内镜像，用 40 行代码跑通第一个 FastAPI 接口，并搞懂它与 Flask、Django 的选型差异。",
        "difficulty": 1,
        "tags": ["FastAPI", "环境搭建", "uvicorn"],
        "duration_minutes": 25,
        "content": """## 🎯 本课目标

- 在 fastapi_todo 目录里建好虚拟环境，pip 配好清华镜像，装齐 fastapi 与 uvicorn
- 写出 hello.py，用 uvicorn 启动，浏览器访问 `/` 与 `/docs` 都返回正确结果
- 说清 FastAPI、Flask、Django 三者的定位差异，知道什么场景该选 FastAPI
- 理解 ASGI 与 uvicorn 的关系：框架负责处理请求，服务器负责监听端口
- 记住 15 课结束时你要交付的完整项目全貌，知道每一课在拼哪一块

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| fastapi_todo/ | 全课程项目根目录，15 课都在里面迭代 |
| .venv/ | 项目专属虚拟环境，绝不提交仓库 |
| requirements.txt | 依赖清单，随课程增长 |
| hello.py | 第一个可运行应用（本课主角） |
| .gitignore | 排除 .venv、*.db、.env 等敏感与临时文件 |

## 承接上一课

本课是「FastAPI 后端开发」模块的起点，从空目录开始；第 6 课会长出 database.py 与 models.py，第 14 课再把它们整理成标准的包结构，一直到第 15 课部署上线。

## 📖 概念讲解

### FastAPI 到底解决了什么问题

写一个 Web 接口，本质上只做三件事：**接收 HTTP 请求、校验参数、返回 JSON**。Flask 让你手写这三件事，FastAPI 把后两件用类型注解自动完成了：

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}
```

仅仅因为写了 `item_id: int`，FastAPI 就自动做了四件事：把路径里的字符串转成整数、类型不对直接返回 422、把这个参数登记进 OpenAPI 文档、在 `/docs` 页面生成可点击的调试表单。这是它和 Flask 最本质的差别——**类型注解就是接口契约**。

整个技术栈可以拆成三层看：

| 层次 | 本课程使用 | 职责 |
| --- | --- | --- |
| 应用框架 | FastAPI | 路由、参数校验、依赖注入、生成文档 |
| 数据校验 | Pydantic v2 | 请求体与响应体的模型定义、序列化 |
| 协议与服务器 | ASGI + uvicorn | 异步协议标准与真正监听端口的进程 |

**ASGI 是什么**：它是 Python 异步 Web 的接口标准，规定了「服务器怎样把请求交给应用、应用怎样把响应交回去」。FastAPI 是一个 ASGI 应用，自己不会监听端口，必须由 uvicorn 这样的 ASGI 服务器来跑。所以启动命令永远是 `uvicorn 模块名:变量名`，而不是 `python hello.py`。

### FastAPI、Flask、Django 怎么选

| 维度 | FastAPI | Flask | Django |
| --- | --- | --- | --- |
| 异步支持 | 原生 async/await | 需插件，支持有限 | 3.1 后部分支持 |
| 参数校验 | Pydantic 自动完成 | 手写或装插件 | Form/DRF 序列化器 |
| 自动文档 | 内置 /docs、/redoc | 需扩展 | 需 DRF + drf-spectacular |
| 自带功能 | 极简，按需拼装 | 极简 | ORM、后台、迁移全带 |
| 典型场景 | API、微服务、AI 服务 | 小工具、原型 | 内容型全栈网站 |

一句话总结：**要写 API 且在意性能与文档，选 FastAPI；要快速拼个小服务，Flask 够用；要一个带后台管理的完整网站，Django 更省事。** 近两年 AI 服务、模型网关几乎清一色用 FastAPI，因为它天生适合「高并发 + JSON + 异步调用外部服务」这类工作。

### 本课程的最终形态

15 课不是零散 demo，而是同一个 `fastapi_todo` 项目逐步长大：第 1~5 课做路由、校验、响应、依赖；第 6~8 课接数据库、做注册登录与权限；第 9~12 课加上传、后台任务、WebSocket 与日志；第 13~14 课补测试与工程化分层；第 15 课用 Docker 部署上线。每一课的代码都是下一课的地基，所以**不要跳课，也不要每课重造文件**。

## 🛠 Step 1：建项目与虚拟环境

```bash
# 1. 确认 Python 版本，本课程要求 3.11 及以上
python3 --version

# 2. 创建项目目录并进入
mkdir fastapi_todo && cd fastapi_todo

# 3. 创建虚拟环境：解释器副本与独立包目录都会放进 .venv
python3 -m venv .venv

# 4. 激活虚拟环境（macOS / Linux）
source .venv/bin/activate
# Windows PowerShell 用：.venv/Scripts/Activate.ps1

# 5. 确认当前 python3 来自 .venv，而不是系统解释器
which python3
python3 -m pip --version

# 6. 配置国内镜像，之后所有 pip 安装都走清华源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 7. 安装 fastapi 与 uvicorn（[standard] 会带上热重载所需的依赖）
pip install "fastapi[standard]" "uvicorn[standard]"

# 8. 冻结依赖，换台机器一条命令就能复现环境
pip freeze > requirements.txt
```

逐条解释关键点：

- **第 3 步**：venv 会在项目里生成 `.venv/`，里面有独立的解释器与 site-packages。以后所有包装进这里，删掉目录就等于干净卸载，不污染系统 Python。
- **第 5 步**：`which python3` 必须指向 `fastapi_todo/.venv/bin/python3`。如果还显示 `/usr/bin/python3`，说明激活失败，后面所有命令都会装错地方。
- **第 6 步**：国内直连 PyPI 常常几 KB 每秒甚至超时，配好镜像后安装速度提升非常明显。配置写在 `~/.config/pip/pip.conf`，只需执行一次。
- **第 7 步**：`uvicorn[standard]` 里的方括号是「额外依赖」语法，会额外装上 `uvloop`、`httptools`、`watchfiles`，热重载与性能都靠它们；不加也能跑，但 `--reload` 会退化成轮询。
- **第 8 步**：`requirements.txt` 要跟着课程每装一个新库就更新一次，这是第 15 课 Docker 镜像构建的输入。

顺手建一个 `.gitignore`，三行就够：

```text
.venv/
__pycache__/
*.db
.env
```

## 🛠 Step 2：写出 hello.py

```python
# hello.py：全课程的第一个应用，后面会逐步长成 main.py
from fastapi import FastAPI
from pydantic import BaseModel

# 应用实例：title 与 version 会直接显示在 /docs 页面顶部
app = FastAPI(
    title="FastAPI Todo API",
    description="无限学堂 FastAPI 课程项目，15 课逐步完善",
    version="0.1.0",
)


class HelloResponse(BaseModel):
    # 用模型声明响应结构，/docs 里就能看到字段说明
    message: str
    version: str


@app.get("/")
async def read_root() -> HelloResponse:
    # async def：请求处理期间可以让出事件循环去干别的
    return HelloResponse(message="Hello FastAPI", version="0.1.0")


@app.get("/health")
async def health_check() -> dict[str, str]:
    # 健康检查接口：第 15 课部署后给负载均衡和监控用
    return {"status": "ok"}


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict[str, object]:
    # 路径里的 item_id 声明为 int，FastAPI 会自动做类型转换与校验
    return {"item_id": item_id, "name": "item-" + str(item_id)}


@app.get("/items")
async def list_items() -> list[dict[str, object]]:
    # 返回列表时，可以写成 list[ItemSummary] 让文档显示元素结构
    return [
        {"item_id": 1, "name": "item-1"},
        {"item_id": 2, "name": "item-2"},
    ]


if __name__ == "__main__":
    # 直接 python hello.py 也能启动，调试时少敲一条命令
    # 生产环境仍然用 uvicorn 命令，方便配 worker 与代理头
    import uvicorn

    uvicorn.run("hello:app", host="127.0.0.1", port=8000, reload=True)
```

逐段解释：

- **`app = FastAPI(...)`**：整个应用只有这一个实例。`title`、`description`、`version` 不是装饰性的，它们会渲染进 `/docs` 与 `/openapi.json`，是给前端和调用方看的接口说明。
- **`class HelloResponse(BaseModel)`**：继承 Pydantic 的 BaseModel，作用是「声明返回什么」。返回值写成这个模型实例后，FastAPI 会校验字段、序列化成 JSON，并在文档里列出字段类型。
- **`@app.get("/")`**：装饰器把函数注册到「GET 方法 + 根路径」上。装饰器只负责登记，函数仍然是普通函数，可以直接调用测试。
- **`async def`**：本课程统一用异步函数。只要函数体内有 `await`（查库、调外部 API）就必须是 `async def`；纯计算的函数写成 `async def` 反而会阻塞事件循环，那种情况后面会讲怎么处理。
- **`item_id: int`**：这行注解同时做了三件事——类型转换、校验（`/items/abc` 直接 422）、文档生成。
- **`if __name__ == "__main__"`**：这个入口只在 `python hello.py` 时执行，被 uvicorn import 时不会跑。注意 `uvicorn.run` 里的字符串是模块路径，不要写成 `__main__:app`，否则 reload 会失效。

## 🛠 Step 3：启动并验证

```bash
# 在 fastapi_todo 目录下启动，--reload 表示改代码自动重启（仅开发用）
uvicorn hello:app --reload --port 8000

# 另开一个终端验证
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/items/42
```

`hello:app` 的读法是「模块名:应用变量名」，冒号前是文件名去掉 `.py`，冒号后是 `FastAPI()` 赋给的变量。如果文件在子目录里，要写成 `app.main:app` 这种点分路径——这也是第 14 课重构目录后启动命令会变的原因。

## 运行效果

```text
$ uvicorn hello:app --reload --port 8000
INFO:     Will watch for changes in these directories: ['/Users/me/fastapi_todo']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [48231] using WatchFiles
INFO:     Started server process [48233]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

$ curl http://127.0.0.1:8000/items/42
{"item_id":42,"name":"item-42"}

$ curl -i http://127.0.0.1:8000/items/abc
HTTP/1.1 422 Unprocessable Entity
{"detail":[{"type":"int_parsing","loc":["path","item_id"],
"msg":"Input should be a valid integer, unable to parse string as an integer",
"input":"abc"}]}
```

打开 `http://127.0.0.1:8000/docs`，会看到一个 Swagger UI 页面，三个接口都能点「Try it out」直接发请求。`/redoc` 是另一种风格的文档。这两个页面**不需要写任何文档代码**，全部由类型注解和 Pydantic 模型推导而来。

## 常见坑

**忘了激活虚拟环境**：`pip install` 装进系统 Python，`uvicorn` 命令找不到或 import 报错。判断方法就是 `which python3`，路径里必须有 `.venv`。每开一个新终端都要重新 `source .venv/bin/activate`。

**`--reload` 用在生产环境**：热重载会常驻一个文件监听进程，占内存、拖性能，还可能因为文件变动导致服务抖动。生产启动见第 15 课，去掉 `--reload`，改用多 worker。

**在错误目录启动**：`uvicorn hello:app` 必须在 `hello.py` 所在目录执行，否则报 `Could not import module "hello"`。模块路径是相对当前工作目录解析的，跟你在哪个终端无关。

**`async def` 里写 `time.sleep` 或同步 requests**：这会卡住整个事件循环，所有并发请求排队等待。异步函数里只能用 `await asyncio.sleep()` 和 `httpx.AsyncClient`，第 10 课会专门讲这个陷阱。

**访问 `/docs` 报 404**：先确认路径是 `/docs` 不是 `/doc`；其次如果给 `FastAPI(docs_url=None)` 关过文档，自然打不开。默认配置下它一定在。

## 课后练习

1. 给 hello.py 增加一个 `/about` 接口，返回作者名、学习日期和一个字符串列表（比如三个学习目标），并用 Pydantic 模型声明响应结构。
2. 增加 `/items/{item_id}/comments/{comment_id}` 双路径参数接口，两个参数都声明为 `int`，分别用 `/items/1/comments/x` 和 `/items/1/comments/2` 请求一次，观察 422 与 200 的差别，并解释 `loc` 字段的含义。
3. 把 `uvicorn hello:app --port 8000` 改成 `--port 9000`，并用 `curl` 验证；再故意用已被占用的端口启动一次，记录报错信息。

## 下一课预告

下一课我们把 hello.py 里的三个接口扩展成一套完整的增删改查路由，讲清路径参数、查询参数、枚举与校验器，以及那个几乎人人都踩过的「路径顺序陷阱」。""",
    },
    {
        "title": "第 2 课：路由与路径/查询参数",
        "summary": "掌握路径参数的类型转换、Query 的校验约束、Enum 枚举筛选与路由声明顺序，写出规范的列表与详情接口。",
        "difficulty": 1,
        "tags": ["FastAPI", "路由", "Query 校验"],
        "duration_minutes": 28,
        "content": """## 🎯 本课目标

- 分清路径参数、查询参数、请求体三类数据来源，知道 FastAPI 靠什么自动判断
- 用 `Path` 与 `Query` 给参数加约束（`ge`、`le`、`max_length`），让非法请求在入口被拦下
- 用 `Enum` 限定状态值，避免接口收到「active / actived / ACTIVE」这类脏数据
- 理解并复现「路径顺序陷阱」，知道为什么 `/items/latest` 会被 `/items/{item_id}` 抢走
- 把第 1 课的 hello.py 改造成带列表、筛选、分页、详情的 items 路由

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| main.py | 由 hello.py 改名而来，本课及后续课程的主应用文件 |
| data.py | 临时内存数据（第 6 课接数据库前的过渡） |

## 承接上一课

把第 1 课的 `hello.py` 重命名为 `main.py`（`git mv hello.py main.py`），保留 `/` 与 `/health` 两个接口不动，本课开始往里加 items 相关路由；启动命令随之变成 `uvicorn main:app --reload`。

## 📖 概念讲解

### 参数从哪来，FastAPI 怎么判断

FastAPI 判断参数来源的规则非常朴素：**看名字有没有出现在路径模板里，看类型是不是 Pydantic 模型**。

| 参数写法 | 来源 | 例子 |
| --- | --- | --- |
| 名字出现在 `{}` 中 | 路径参数 | `@app.get("/items/{item_id}")` + `item_id: int` |
| 普通标量且有默认值 | 查询参数（可选） | `limit: int = 10` |
| 普通标量无默认值 | 查询参数（必填） | `q: str` |
| 类型是 BaseModel | 请求体 | `item: ItemCreate` |
| 类型是 `UploadFile` | 文件上传 | 第 9 课展开 |

这张表值得背下来。新手最常见的困惑是「为什么我的参数跑到 URL 问号后面去了」，答案就是它没有出现在路径模板里，FastAPI 只能把它当查询参数。

### 为什么要给参数加约束

只在函数体里 `if limit > 100: raise ...` 也能工作，但有两个问题：一是校验逻辑散落在业务代码里，二是 `/docs` 上看不到任何约束说明。用 `Query`、`Path` 声明约束后，**校验前移到框架层，文档自动生成**：

```python
limit: Annotated[int, Query(ge=1, le=100)] = 20
```

`Annotated[类型, 元数据]` 是 Python 3.9+ 的标准写法，也是 FastAPI 现在官方推荐的风格：类型写在第一个位置，校验规则作为元数据附加，函数签名读起来更干净。老写法 `limit: int = Query(20, ge=1, le=100)` 仍然可用，本课程统一用 `Annotated`。

### 路由匹配是「先声明先匹配」

FastAPI（底层是 Starlette）按**注册顺序**逐条匹配路由，第一条匹配上就直接执行，不会继续往下找。所以：

- `/items/latest` 必须写在 `/items/{item_id}` **前面**；
- 否则 `latest` 会被当作 `item_id` 的值送进详情接口，返回 422（如果类型是 int）或者查不到数据（如果类型是 str）。

这不是 bug，是设计。所有 Web 框架的路由都遵循这个规则，把它当成「更具体的路径要写在更宽泛的路径之前」即可。

## 🛠 Step 1：准备内存数据与类型定义

```python
# data.py：第 6 课接数据库前的临时数据源
from enum import Enum


class ItemStatus(str, Enum):
    # 继承 str 让枚举值直接序列化成字符串，JSON 里就是 "active"
    active = "active"
    done = "done"
    archived = "archived"


ITEMS: list[dict[str, object]] = [
    {"id": 1, "name": "写 FastAPI 课程", "status": "active", "price": 0.0},
    {"id": 2, "name": "买牛奶", "status": "done", "price": 12.5},
    {"id": 3, "name": "整理笔记", "status": "active", "price": 0.0},
    {"id": 4, "name": "跑五公里", "status": "archived", "price": 0.0},
]


def find_item(item_id: int) -> dict[str, object] | None:
    # 用生成器表达式找第一条匹配的记录，找不到返回 None
    return next((item for item in ITEMS if item["id"] == item_id), None)
```

要点说明：

- **枚举继承 `str`**：这样 `ItemStatus.active == "active"` 成立，Pydantic 序列化时直接输出字符串，不用额外转换。Python 3.11 也可以用 `StrEnum`，效果一致。
- **`ITEMS` 用列表而不是字典**：顺序稳定，方便演示分页切片；真实项目里这层会被第 6 课的数据库查询替代。
- **`find_item` 抽成函数**：路由里只写业务语义，第 6 课把函数体换成 `select` 语句时，路由几乎不用改。

## 🛠 Step 2：写路径参数与顺序陷阱

```python
# main.py：本课重点在 items 路由
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query

from data import ITEMS, ItemStatus, find_item

app = FastAPI(title="FastAPI Todo API", version="0.2.0")


def to_public(item: dict[str, object]) -> dict[str, object]:
    # 统一出口结构：感兴趣字段才返回，price 留作内部数据
    return {
        "id": item["id"],
        "name": item["name"],
        "status": item["status"],
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


# 注意：这条必须写在 /items/{item_id} 之前，否则 latest 会被当成 id
@app.get("/items/latest")
async def read_latest_item() -> dict[str, object]:
    return to_public(ITEMS[-1])


@app.get("/items/count")
async def count_items() -> dict[str, int]:
    # 固定路径同样要排在参数路径之前
    return {"total": len(ITEMS)}


@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(ge=1, description="待办事项 ID，从 1 开始")],
) -> dict[str, object]:
    item = find_item(item_id)
    if item is None:
        # 找不到就 404，异常信息会出现在响应体的 detail 字段里
        raise HTTPException(status_code=404, detail="Item not found")
    return to_public(item)
```

关键点逐条看：

- **`Path(ge=1)`**：路径参数 ID 至少为 1。请求 `/items/0` 会被框架直接拒绝并返回 422，连函数体都不会进。
- **`description`**：会显示在 `/docs` 的参数说明里，是给调用方看的，写清楚比写「id」有价值得多。
- **`raise HTTPException`**：这是 FastAPI 里中断请求的标准方式，参数是状态码与 detail。它不会返回 500，而是按你指定的状态码返回。
- **`to_public` 先收口**：现在只有三个接口，看不出价值；等第 4 课加了 `response_model`、第 6 课接了数据库，这个函数就是防止内部字段泄露的最后一道手工闸门。
- **顺序**：如果把 `/items/latest` 或 `/items/count` 挪到详情路由后面，访问它们必然返回 422，因为 `latest`、`count` 都无法转成 int。这是本课最值得记住的一个细节。

## 🛠 Step 3：查询参数、校验与枚举筛选

```python
@app.get("/items")
async def list_items(
    q: Annotated[str | None, Query(max_length=20, description="按名称模糊搜索")] = None,
    status: ItemStatus | None = None,
    skip: Annotated[int, Query(ge=0, description="跳过多少条")] = 0,
    limit: Annotated[int, Query(ge=1, le=50, description="每页条数")] = 10,
) -> dict[str, object]:
    # 1. 先按名称过滤，q 为空时不做过滤
    result = [item for item in ITEMS if q is None or q in str(item["name"])]

    # 2. 再按状态过滤，枚举值在比较时就是字符串
    if status is not None:
        result = [item for item in result if item["status"] == status.value]

    # 3. 最后分页：先算总数，再切片
    total = len(result)
    page = result[skip : skip + limit]

    return {"total": total, "skip": skip, "limit": limit, "items": page}
```

这段代码值得逐行拆开：

- **`str | None` 加默认值 `None`**：表示这个查询参数可以不传。类型里的 `None` 与默认值必须同时出现，只写 `str | None` 而给默认值 `""` 会让文档显示成必填。
- **`Query(max_length=20)`**：字符串长度上限。搜索词不设上限，恶意用户传一个几十 KB 的字符串就能让数据库做全表 LIKE，这是最廉价的防护。
- **`limit` 的 `le=50`**：分页接口不做上限，等于允许 `?limit=1000000` 一次拖垮服务。**任何分页参数都必须有上限**，这是生产环境的硬规矩。
- **`status: ItemStatus | None = None`**：枚举参数。传 `?status=done` 能通过，传 `?status=finished` 直接 422，并在错误信息里列出所有合法值。这就是用枚举代替裸字符串的价值。
- **`result[skip : skip + limit]`**：内存分页用切片；第 6 课换成 SQL 的 `offset` / `limit`，接口契约完全不变。

## 运行效果

```text
$ uvicorn main:app --reload
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

$ curl "http://127.0.0.1:8000/items?limit=2"
{"total":4,"skip":0,"limit":2,"items":[
 {"id":1,"name":"写 FastAPI 课程","status":"active","price":0.0},
 {"id":2,"name":"买牛奶","status":"done","price":12.5}]}

$ curl "http://127.0.0.1:8000/items?status=done"
{"total":1,"skip":0,"limit":10,"items":[{"id":2,"name":"买牛奶",...}]}

$ curl "http://127.0.0.1:8000/items/latest"
{"id":4,"name":"跑五公里","status":"archived","price":0.0}

$ curl -i "http://127.0.0.1:8000/items?limit=999"
HTTP/1.1 422 Unprocessable Entity
{"detail":[{"type":"less_than_equal","loc":["query","limit"],
"msg":"Input should be less than or equal to 50","input":"999"}]}
```

注意最后一条：`loc` 是 `["query", "limit"]`，明确告诉你出错位置在查询参数的第 limit 项。排错时先看 `loc`，再看 `msg`，比读整段 JSON 快得多。

## 常见坑

**路径顺序写反**：`/items/{item_id}` 写在 `/items/latest` 前面，前者会把 `latest` 吃掉。记住原则：**固定路径永远写在参数路径之前**。

**尾斜杠导致 307**：`/items/` 与 `/items` 是两个不同路径，访问前者会收到 307 重定向。前端如果没跟随重定向就会报错，接口文档里最好统一不带尾斜杠。

**把校验写成业务判断**：`if limit > 50: raise HTTPException(400)` 也能拦住，但状态码语义错了（这是参数格式问题不是业务问题），而且文档上看不到。约束就该写在 `Query` 里。

**`Optional` 与默认值不匹配**：`q: str | None` 却不给默认值，FastAPI 会认为它是必填，不传就 422。要么 `q: str`（必填），要么 `q: str | None = None`（可选），别混着写。

**枚举值大小写**：`?status=Done` 不匹配 `done`，因为枚举是精确比较。如果要大小写不敏感，需要在枚举里同时定义，或者在依赖里先 `lower()`，不要指望框架兜底。

## 课后练习

1. 给 `/items` 增加 `min_price` 与 `max_price` 两个查询参数（`ge=0`），实现价格区间过滤，并保证 `min_price > max_price` 时返回 422 而不是空列表。
2. 新增 `/items/stats` 接口，返回各状态的数量（`active`、`done`、`archived` 三个键），把它放在 `/items/{item_id}` 之前并验证顺序的必要性。
3. 把 `q` 的匹配改成大小写不敏感（提示：比较时统一转小写），并说明为什么不能直接对 `ITEMS` 原地修改。

## 下一课预告

参数校验只能解决「单个值合不合法」，而创建接口通常要接收一整个 JSON 对象——下一课用 Pydantic v2 定义请求体模型，一次性解决字段校验、嵌套结构与错误提示。""",
    },
    {
        "title": "第 3 课：Pydantic v2 请求体模型",
        "summary": "用 BaseModel 定义请求体，掌握 Field 校验、嵌套模型、默认值与 model_config，读懂 422 错误结构。",
        "difficulty": 1,
        "tags": ["FastAPI", "Pydantic v2", "请求体校验"],
        "duration_minutes": 30,
        "content": """## 🎯 本课目标

- 用 `BaseModel` 定义创建与更新用的请求体，让 JSON 解析、类型转换、校验一次完成
- 掌握 `Field` 的常用约束：长度、数值范围、正则、示例值
- 写出嵌套模型（地址、标签列表），理解 Pydantic 如何递归校验
- 分清「可选字段」与「可为 None 字段」，知道 `model_dump(exclude_unset=True)` 的用途
- 能独立读懂 422 响应里的 `type`、`loc`、`msg`、`input` 四个字段

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| schemas.py | 所有请求体与响应模型，后续课程持续扩充 |
| main.py | 新增 `POST /items` 创建接口 |

## 承接上一课

第 2 课的 `data.py` 与 items 查询接口保持不变，本课新建 `schemas.py`，并在 `main.py` 里加上创建接口——它接收的不再是查询参数，而是一个完整的 JSON 对象。

## 📖 概念讲解

### 为什么请求体要单独定义模型

创建一条待办事项，客户端会发来这样的 JSON：

```json
{"name": "买牛奶", "price": 12.5, "tags": ["生活"], "owner": {"name": "小明"}}
```

如果用 `name: str, price: float` 一个个接，会遇到三个麻烦：嵌套结构没法表达、校验规则散落、文档里看不出整体结构。用模型声明则一次性解决：

| 能力 | 手写参数 | Pydantic 模型 |
| --- | --- | --- |
| 结构校验 | 自己判断 key 是否存在 | 自动 |
| 嵌套对象 | 需要拆成多个参数 | 直接嵌套模型 |
| 多余字段 | 会被静默忽略 | 默认忽略，可配置为报错 |
| 文档展示 | 参数列表，看不出层级 | 完整 JSON Schema |

### 模型分层：Base、Create、Update、Read

现实项目里同一种资源通常需要四个模型，这是业内的通用做法：

| 模型 | 用途 | 特点 |
| --- | --- | --- |
| `ItemBase` | 公共字段 | 只有业务字段，不含 id、时间 |
| `ItemCreate` | 创建请求体 | 继承 Base，补上必填约束 |
| `ItemUpdate` | 更新请求体 | 所有字段可选，支持部分更新 |
| `ItemRead` | 响应体 | 含 id 与时间，`from_attributes=True` |

这样拆的好处是**字段只写一遍**，改一个字段名只改一处；坏处是文件会长一点，但换来的是可维护性。第 14 课接入数据库后，`ItemRead` 还要承担把 ORM 对象转成 JSON 的职责，那时 `from_attributes` 就派上用场了。

### 可选字段的两种语义

这两个写法看起来差不多，语义完全不同：

- `description: str | None = None`：字段可以**不传**，也可以传 `null`，默认 `null`；
- `description: str = ""`：字段可以不传，但不能传 `null`，默认空字符串。

做部分更新（PATCH）时还要区分第三种情况：**字段没传**。此时要看 `model_dump(exclude_unset=True)`——它只输出客户端真正传了的字段，没传的不会出现在字典里。如果直接用 `model_dump()`，没传的字段会以默认值出现，导致「我没改价格，价格却被重置成 0」。

## 🛠 Step 1：定义 schemas.py

```python
# schemas.py：请求体与响应模型集中管理
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Owner(BaseModel):
    # 嵌套模型：请求体里可以带一个对象，Pydantic 会递归校验
    name: Annotated[str, Field(min_length=1, max_length=20)]
    email: str | None = None


class ItemBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50, description="事项名称")]
    price: Annotated[float, Field(ge=0, le=100000, description="价格，单位元")] = 0.0
    tags: Annotated[list[str], Field(max_length=5, description="最多 5 个标签")] = []
    owner: Owner | None = None


class ItemCreate(ItemBase):
    # 创建时额外要求一个优先级，只允许三个字面量
    priority: Literal["low", "normal", "high"] = "normal"

    @field_validator("tags")
    @classmethod
    def strip_tags(cls, value: list[str]) -> list[str]:
        # 去掉标签两端空白，同时过滤空字符串
        cleaned = [tag.strip() for tag in value if tag.strip()]
        if len(cleaned) != len(value):
            raise ValueError("标签不能为空字符串")
        return cleaned


class ItemUpdate(BaseModel):
    # 更新模型所有字段可选，None 表示「这一项不改」
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    price: Annotated[float | None, Field(ge=0)] = None
    tags: list[str] | None = None


class ItemRead(ItemBase):
    # from_attributes 让 ORM 对象可以直接喂给这个模型（第 6 课用到）
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
```

逐段解释：

- **`Owner` 单独成模型**：如果写成 `owner_name: str`，以后要加邮箱、电话就得不断加字段。嵌套模型让结构可扩展，且 422 报错能精确到 `body.owner.email`。
- **`Field(min_length=1, max_length=50)`**：字符串长度约束。注意 Pydantic v2 里长度用 `min_length`/`max_length`，不再是 v1 的 `min_items`/`max_items`（列表长度现在也用 `min_length`）。
- **`Field(max_length=5)` 用在列表上**：v2 统一了语义，列表的最大元素个数也是 `max_length`。写 `max_items` 会直接报错。
- **`Literal["low", "normal", "high"]`**：比 Enum 更轻量的枚举写法，适合只有几个固定值的场景，文档里会列出可选值。
- **`@field_validator("tags")`**：字段级校验器，在类型校验之后执行。必须加 `@classmethod`，返回值会替换原值。抛 `ValueError` 时，Pydantic 会把它包装成 422 错误。
- **`ConfigDict(from_attributes=True)`**：允许从对象属性读取数据（ORM 实例、dataclass 都行），替代 v1 的 `orm_mode = True`。
- **可变默认值 `[]`**：Pydantic 会为每个实例深拷贝，不会出现 Python 函数默认参数那种「所有实例共享一个列表」的经典 bug。

## 🛠 Step 2：在 main.py 里接收请求体

```python
# main.py：新增创建接口
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status

from data import ITEMS
from schemas import ItemCreate, ItemRead

app = FastAPI(title="FastAPI Todo API", version="0.3.0")


@app.post("/items", status_code=status.HTTP_201_CREATED, response_model=ItemRead)
async def create_item(payload: ItemCreate) -> dict[str, object]:
    # 1. 生成新 ID：真实项目由数据库自增，这里先取最大值加一
    new_id = max((item["id"] for item in ITEMS), default=0) + 1

    # 2. model_dump 把模型转成普通字典，嵌套的 owner 也会变成字典
    record = payload.model_dump()

    # 3. 补齐服务端生成的字段，客户端传什么都不算数
    record.update(
        id=new_id,
        status="active",
        created_at=datetime.now(timezone.utc),
    )

    ITEMS.append(record)
    return record


@app.get("/items/{item_id}", response_model=ItemRead)
async def read_item(item_id: int) -> dict[str, object]:
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
```

重点说明：

- **`payload: ItemCreate`**：参数类型是 BaseModel，FastAPI 就知道「从请求体 JSON 里取数据」。请求体必须是合法 JSON，否则返回 422 而不是 500。
- **`status_code=201`**：创建成功用 201 Created，这是 HTTP 语义。用 `status.HTTP_201_CREATED` 常量比写数字可读。
- **`response_model=ItemRead`**：声明响应结构。它会做三件事：过滤掉模型里没定义的字段、校验返回数据、把结构写进文档。**这是数据脱敏的主要手段**，第 4 课会重点讲。
- **`max(..., default=0)`**：空列表时 `max` 会抛异常，`default=0` 保证第一次创建也能拿到 id=1。
- **`model_dump()`**：v2 的方法名，v1 的 `dict()` 已废弃。嵌套模型会被递归转换成字典。
- **`record.update(...)`**：服务端字段（id、status、created_at）必须由后端生成，绝不能允许客户端传——否则用户可以伪造 id 篡改别人的数据。

## 运行效果

```text
$ curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name":"写周报","price":0,"tags":["工作"],"owner":{"name":"小明"},"priority":"high"}'
{"name":"写周报","price":0.0,"tags":["工作"],"owner":{"name":"小明","email":null},
 "priority":"high","id":5,"created_at":"2026-11-12T02:31:07.512Z"}

$ curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name":"","price":-1,"priority":"urgent"}'
HTTP/1.1 422 Unprocessable Entity
{"detail":[
 {"type":"string_too_short","loc":["body","name"],"msg":"String should have at least 1 character","input":""},
 {"type":"greater_than_equal","loc":["body","price"],"msg":"Input should be greater than or equal to 0","input":-1},
 {"type":"literal_error","loc":["body","priority"],"msg":"Input should be 'low', 'normal' or 'high'","input":"urgent"}]}
```

注意 422 会**一次性返回所有错误**，而不是遇到第一个就停。这对前端表单非常友好：一次请求就能把三个字段的错误同时标红。`loc` 的 `["body", "name"]` 表示「请求体里的 name 字段」，嵌套时会是 `["body", "owner", "email"]`。

## 常见坑

**用 v1 的 API 写 v2**：`class Config: orm_mode = True`、`.dict()`、`min_items` 全部失效或报错。v2 的对应写法是 `model_config = ConfigDict(from_attributes=True)`、`model_dump()`、`min_length`。

**把 `response_model` 当成可选**：不声明也能返回，但字段会原样泄露。只要模型里有 password、token、内部备注这类字段，就一定要用 `response_model` 或 `response_model_exclude` 收口。

**误以为不传的字段等于 None**：PATCH 场景必须用 `model_dump(exclude_unset=True)`，否则默认值会把数据库里的原值覆盖掉，这是「改个名字结果价格归零」的典型原因。

**在 validator 里做数据库查询**：`field_validator` 是同步的、只该做纯数据清洗（去空格、格式规整）。查库判重请放到路由或依赖里，否则校验器会变成隐藏的 IO 黑洞。

**给 list 字段用可变默认值却忘了 Pydantic 的保护**：Pydantic 会深拷贝默认值，所以 `tags: list[str] = []` 是安全的；但如果默认值写成模块级常量 `DEFAULT_TAGS`，多个实例就会共享同一个列表，务必注意。

## 课后练习

1. 给 `ItemCreate` 增加 `due_date: datetime | None`，要求它必须是未来时间（提示：用 `field_validator` 比较 `datetime.now(timezone.utc)`，注意时区）。
2. 增加 `ItemUpdate` 的 PATCH 接口 `/items/{item_id}`，用 `model_dump(exclude_unset=True)` 只更新客户端传了的字段，并验证「只传 name 时 price 不变」。
3. 故意提交一个 `owner` 里多带 `age` 字段的请求，观察是否被忽略；然后给 `Owner` 加 `model_config = ConfigDict(extra="forbid")`，再请求一次，解释行为差异。

## 下一课预告

模型定义好输入，还得管好输出——下一课用 `response_model`、状态码与自定义异常处理器，把「返回什么、出错怎么回」这套规则彻底定下来。""",
    },
    {
        "title": "第 4 课：响应处理与状态码",
        "summary": "用 response_model 收口返回结构、按语义选状态码，配合 HTTPException 与自定义异常处理器统一错误格式。",
        "difficulty": 1,
        "tags": ["FastAPI", "response_model", "异常处理"],
        "duration_minutes": 28,
        "content": """## 🎯 本课目标

- 用 `response_model` 控制输出字段，实现数据脱敏与结构稳定
- 按 HTTP 语义选择状态码：200、201、204、400、404、409、422
- 用 `HTTPException` 表达业务错误，并用 `responses` 参数把错误写进文档
- 自定义异常类与全局异常处理器，让所有错误响应格式统一
- 理解为什么**不能让异常堆栈直接返回给客户端**

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| exceptions.py | 业务异常类与统一错误响应体 |
| main.py | 注册异常处理器，补充删除接口与 204 响应 |

## 承接上一课

第 3 课的 `schemas.py` 里已有 `ItemRead`，本课把它全面用到查询与创建接口上；新增 `exceptions.py`，第 5 课起的依赖注入会复用这里的异常类型。

## 📖 概念讲解

### 响应模型是「出口的安检机」

请求进来有 Pydantic 校验，响应出去也要有。`response_model` 干的就是这件事：

```python
@app.get("/items/{item_id}", response_model=ItemRead)
```

它会做三件事，缺一不可：

1. **过滤**：只输出模型里声明的字段。函数里多返回了 `internal_note`、`password_hash`，也不会泄露。
2. **校验**：返回数据不符合模型时直接报错，能在开发阶段就发现「说好返回 int 结果给了 None」这类问题。
3. **文档**：`/docs` 里展示完整的响应结构，前端照着写类型定义就行。

在真实项目里，**只要有用户表，就必须有 `UserRead` 且不含密码字段**。这不是可选项，是底线。

### 状态码不是装饰，是契约

| 状态码 | 语义 | 本课程用在哪 |
| --- | --- | --- |
| 200 | 请求成功 | 查询、更新 |
| 201 | 已创建 | POST 创建资源 |
| 204 | 成功但无内容 | DELETE 删除 |
| 400 | 请求本身有问题 | 业务规则冲突（如重复名称） |
| 401 | 未认证 | 第 7 课：没带 token 或 token 失效 |
| 403 | 已认证但无权限 | 第 8 课：普通用户访问管理接口 |
| 404 | 资源不存在 | 详情、更新、删除找不到 |
| 409 | 冲突 | 注册时用户名已存在 |
| 422 | 参数校验失败 | 框架自动返回 |

写接口时先问自己「这个结果用哪个码最准确」，而不是一律 200 然后在 body 里写 `{"code": 500}`。后者会让所有网关、监控、重试策略全部失效。

### 异常分三层，处理方式不同

| 异常类型 | 例子 | 谁处理 |
| --- | --- | --- |
| 框架异常 | 参数类型不对 | FastAPI 自动转 422 |
| 业务异常 | 待办不存在、名称重复 | 我们主动抛，转 404 / 409 |
| 未预期异常 | 数据库连接断了、代码 bug | 全局兜底，返回 500 并记日志 |

前两层要给出**明确的、可被前端消费的错误信息**；第三层只返回一句「服务器内部错误」，细节全部写进日志。把堆栈泄露给客户端，等于把表结构、文件路径、依赖版本一起送给了攻击者。

## 🛠 Step 1：定义业务异常与统一错误格式

```python
# exceptions.py：业务异常与统一错误响应体
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    # 所有错误响应都用这一个结构，前端只需写一次解析逻辑
    code: str
    message: str
    detail: object | None = None


class AppError(Exception):
    # 业务异常基类：带上状态码与错误码，由处理器统一转成 JSON
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


class ItemNotFoundError(AppError):
    def __init__(self, item_id: int) -> None:
        super().__init__(
            status_code=404,
            code="ITEM_NOT_FOUND",
            message="待办事项 " + str(item_id) + " 不存在",
        )


class DuplicateItemError(AppError):
    def __init__(self, name: str) -> None:
        super().__init__(
            status_code=409,
            code="ITEM_DUPLICATE",
            message="名称 " + name + " 已存在",
        )
```

逐段说明：

- **`ErrorResponse` 也是模型**：可以在异常处理器里 `model_dump()` 后返回，也能挂到 `responses` 上生成文档，一举两得。
- **`AppError` 带 `status_code`**：异常自己知道该映射成哪个 HTTP 状态码，处理器就不用写一长串 `isinstance` 分支。
- **`code` 是给机器看的**：前端拿 `code` 做判断，拿 `message` 展示给用户。只有一个 message 时，前端只能做字符串匹配，一改文案就崩。
- **继承而非直接抛 HTTPException**：业务层（第 6 课的 crud、第 7 课的 service）不应该依赖 Web 框架。抛自定义异常，Web 层再翻译成 HTTP，分层才干净。

## 🛠 Step 2：注册异常处理器并补全接口

```python
# main.py：异常处理器与完整 CRUD
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from data import ITEMS
from exceptions import AppError, DuplicateItemError, ErrorResponse, ItemNotFoundError
from schemas import ItemCreate, ItemRead

app = FastAPI(title="FastAPI Todo API", version="0.4.0")


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    # 业务异常统一转成约定格式，HTTP 状态码取自异常自身
    body = ErrorResponse(code=exc.code, message=exc.message).model_dump()
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # 把框架的 422 也包装成同一套格式，前端就不用写两套解析
    body = ErrorResponse(
        code="VALIDATION_ERROR",
        message="请求参数校验失败",
        detail=exc.errors(),
    ).model_dump()
    return JSONResponse(status_code=422, content=body)


def get_or_404(item_id: int) -> dict[str, object]:
    # 查询并抛异常的动作收敛成一个函数，避免每个接口重复写
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise ItemNotFoundError(item_id)


@app.post("/items", status_code=status.HTTP_201_CREATED, response_model=ItemRead)
async def create_item(payload: ItemCreate) -> dict[str, object]:
    if any(item["name"] == payload.name for item in ITEMS):
        raise DuplicateItemError(payload.name)
    record = payload.model_dump()
    record.update(id=len(ITEMS) + 1, status="active")
    ITEMS.append(record)
    return record


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    # 204 表示成功但没有响应体，函数返回 None 即可
    target = get_or_404(item_id)
    ITEMS.remove(target)
```

关键点：

- **`@app.exception_handler(AppError)`**：注册后，任何地方 `raise ItemNotFoundError(3)` 都会被它接住，统一序列化。子类会自动匹配父类的处理器，不用为每个子类写一遍。
- **`exc.errors()` 里可能含不可序列化对象**：Pydantic v2 的 errors 里 `ctx` 有时带异常实例，真实项目里建议用 `jsonable_encoder(exc.errors())` 包一层。本课的数据结构足够简单，先直接返回。
- **`status_code=204` 配 `-> None`**：204 响应不能有 body。函数返回 None、不声明 `response_model`，FastAPI 会返回真正的空响应。
- **`JSONResponse` 里手动 `model_dump()`**：异常处理器返回的是 Response 对象而非模型，所以序列化要自己做，这是与普通路由最不一样的细节。
- **`get_or_404` 抽函数**：删除、更新、查询三处都要「找不到就 404」，抽出来只写一次。真实项目里这层会变成 `crud.get_item`。

## 🛠 Step 3：把错误写进接口文档

```python
@app.get(
    "/items/{item_id}",
    response_model=ItemRead,
    responses={404: {"model": ErrorResponse, "description": "待办不存在"}},
)
async def read_item(item_id: int) -> dict[str, object]:
    return get_or_404(item_id)
```

`responses` 参数不会改变运行时行为，它的价值在文档：调用方打开 `/docs` 能看到「这个接口可能返回 404，结构长这样」。**接口文档里只写成功响应，是新手最常犯的协作问题**——前端只能靠猜错误格式，联调时必然反复。

## 运行效果

```text
$ curl http://127.0.0.1:8000/items/99
HTTP/1.1 404 Not Found
{"code":"ITEM_NOT_FOUND","message":"待办事项 99 不存在","detail":null}

$ curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name":"买牛奶"}'
HTTP/1.1 409 Conflict
{"code":"ITEM_DUPLICATE","message":"名称 买牛奶 已存在","detail":null}

$ curl -X DELETE http://127.0.0.1:8000/items/2 -i
HTTP/1.1 204 No Content

$ curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name":""}'
HTTP/1.1 422 Unprocessable Entity
{"code":"VALIDATION_ERROR","message":"请求参数校验失败",
 "detail":[{"type":"string_too_short","loc":["body","name"],...}]}
```

三种错误、三种状态码，但 body 结构完全一致。前端只要写一个错误解析函数，全站通用。

## 常见坑

**用 200 包住错误**：`{"code": 404, "msg": "不存在"}` 配 HTTP 200，会让所有重试、熔断、监控策略失效。状态码必须在 HTTP 层体现。

**忘记 `response_model` 导致字段泄露**：直接把 ORM 对象 return，SQLAlchemy 模型的全部列（包括 `password_hash`）都会被序列化。第 7 课的用户接口尤其危险。

**异常处理器里再抛异常**：处理器本身抛错会变成 500，且原始错误信息丢失。处理器内只做序列化，不要查库、不要做复杂逻辑。

**把 `str(e)` 直接返回**：数据库报错里常含表名、SQL、连接串。对外只回「服务器内部错误」，细节写日志（第 12 课会完整实现）。

**204 接口声明了 response_model**：会导致响应体与状态码冲突，客户端解析报错。204 就老老实实返回 None。

## 课后练习

1. 增加 `PUT /items/{item_id}` 更新接口，用第 3 课的 `ItemUpdate` 做部分更新，返回 200 与更新后的对象；找不到时返回统一的 404 结构。
2. 再定义一个 `ItemForbiddenError`（403），当试图删除 `status` 为 archived 的事项时抛出，验证它被父类处理器自动捕获。
3. 给 `POST /items` 的文档加上 409 的 `responses` 声明，打开 `/docs` 确认错误示例已经出现。

## 下一课预告

现在每个接口都要重复「查数据、判存在、造响应」的样板代码——下一课用依赖注入把这些横切逻辑抽出来，一次性解决参数复用、数据库会话与登录态。""",
    },
    {
        "title": "第 5 课：依赖注入 Depends",
        "summary": "用 Depends 抽掉重复逻辑：函数依赖、类依赖、子依赖与 yield 会话管理，并搞懂依赖缓存到底缓存了什么。",
        "difficulty": 1,
        "tags": ["FastAPI", "依赖注入", "Depends"],
        "duration_minutes": 30,
        "content": """## 🎯 本课目标

- 理解依赖注入解决的是什么问题：把「每个接口都要做的准备动作」抽出来复用
- 写出函数依赖、类依赖、子依赖三种形态，知道各自的适用场景
- 用 `yield` 依赖管理资源生命周期，为第 6 课的数据库会话打好模板
- 说清依赖缓存机制：同一请求内同一个依赖只执行一次，以及 `use_cache=False` 的用途
- 把分页参数、当前时间、数据仓库三块逻辑从路由里剥离到 `deps.py`

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| deps.py | 全课程依赖集中地，第 6~8 课持续扩充 |
| main.py | 路由签名改用 `Depends`，业务代码显著变短 |

## 承接上一课

第 4 课的 `main.py`、`schemas.py`、`exceptions.py` 全部保留；本课新增 `deps.py`，把 `get_or_404` 改造成可注入的仓库依赖，接口路径与响应格式保持不变，只改内部组织方式。

## 📖 概念讲解

### 依赖注入解决的三个重复

没有依赖注入时，一个接口往往长这样：

```python
@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10, token: str = Header(...)):
    user = decode_token(token)          # 每个接口都写一遍
    db = SessionLocal()                  # 每个接口都写一遍
    try:
        ...
    finally:
        db.close()                       # 每个接口都写一遍
```

三段样板代码在 20 个接口里重复 20 次，改一次要改 20 处。依赖注入把这三种横切关注点变成可复用的「零件」：

| 重复逻辑 | 抽成依赖 | 收益 |
| --- | --- | --- |
| 解析并校验 token | `get_current_user` | 改鉴权规则只改一处 |
| 打开/关闭数据库会话 | `get_db`（yield 依赖） | 不会漏关连接 |
| 分页参数校验 | `Pagination` 类依赖 | 全站分页规则一致 |

### 依赖的三种形态

| 形态 | 写法 | 适用场景 |
| --- | --- | --- |
| 函数依赖 | `def get_settings()` | 无状态计算、读配置 |
| 类依赖 | `class Pagination` | 需要多个参数组合成一个对象 |
| 子依赖 | 依赖的参数里再写 `Depends` | 依赖之间有层级，如「当前用户」依赖「解码 token」 |

关键点是：**依赖可以依赖别的依赖**，FastAPI 会自动按拓扑顺序解析，同一请求内相同依赖只执行一次。

### yield 依赖：资源的生命周期管理器

```python
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
```

`yield` 之前是「请求开始前」的准备，`yield` 之后是「响应返回后」的清理。即使路由里抛了异常，`finally` 也一定执行——这就是它比手写 try/finally 更可靠的原因。数据库会话、文件句柄、临时目录都应该这么管。

**注意**：`yield` 依赖的清理代码在响应发送后执行。如果清理里要抛异常（比如提交事务失败），在 FastAPI 0.106+ 之后要格外小心，通常建议在路由函数内部显式提交，把错误暴露在请求处理阶段。

## 🛠 Step 1：写 deps.py

```python
# deps.py：依赖集中管理，第 6 课会把 get_db 换成真实数据库会话
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, Query

from data import ITEMS
from exceptions import ItemNotFoundError


@dataclass
class Pagination:
    # 类依赖：把 skip/limit 打包成一个对象，路由里只写一个参数
    skip: int
    limit: int

    @property
    def offset(self) -> int:
        return self.skip


def get_pagination(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(10, ge=1, le=50, description="每页条数"),
) -> Pagination:
    # 这个函数本身就是依赖：它的参数会被 FastAPI 当作查询参数解析
    return Pagination(skip=skip, limit=limit)


def get_now() -> datetime:
    # 时间也做成依赖：测试时可以 override 成固定时间
    return datetime.now(timezone.utc)


class ItemRepository:
    # 仓库依赖：把数据访问封装起来，第 6 课换成数据库时路由不用改
    def __init__(self, items: list[dict[str, object]]) -> None:
        self.items = items

    def list(self, skip: int, limit: int) -> tuple[int, list[dict[str, object]]]:
        return len(self.items), self.items[skip : skip + limit]

    def get(self, item_id: int) -> dict[str, object]:
        for item in self.items:
            if item["id"] == item_id:
                return item
        raise ItemNotFoundError(item_id)

    def add(self, record: dict[str, object]) -> dict[str, object]:
        record["id"] = max((i["id"] for i in self.items), default=0) + 1
        self.items.append(record)
        return record

    def delete(self, item_id: int) -> None:
        self.items.remove(self.get(item_id))


def get_repo() -> ItemRepository:
    # 生产环境这里返回数据库仓库；当前阶段用内存列表顶着
    return ItemRepository(ITEMS)
```

逐段说明：

- **`@dataclass` 的 Pagination**：依赖的返回值可以是任意对象，路由拿到的是一个已校验好的分页对象，不用再关心 skip/limit 从哪来。
- **`get_pagination` 的参数写 `Query(...)`**：依赖函数的参数同样参与参数解析与校验，`le=50` 的限制自动生效，`/docs` 里也会显示。
- **`get_now` 单独成依赖**：看起来有点小题大做，但它是可测试性的关键——第 13 课的测试里 `app.dependency_overrides[get_now] = lambda: 固定时间` 就能锁死时间。
- **`ItemRepository` 是普通类**：依赖不要求是函数，任何可调用对象都行。用类的好处是方法语义清晰，将来注入真实 session 时改动最小。
- **`get_repo` 是唯一的「接线处」**：路由只依赖 `get_repo`，不关心底层是内存还是 MySQL。这就是依赖注入最重要的价值——**把变化隔离在一个函数里**。

## 🛠 Step 2：改写 main.py 的路由

```python
# main.py：路由只保留业务语义
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, status

from deps import ItemRepository, Pagination, get_now, get_pagination, get_repo
from schemas import ItemCreate, ItemRead

app = FastAPI(title="FastAPI Todo API", version="0.5.0")

RepoDep = Annotated[ItemRepository, Depends(get_repo)]
PageDep = Annotated[Pagination, Depends(get_pagination)]


@app.get("/items")
async def list_items(
    repo: RepoDep,
    page: PageDep,
) -> dict[str, object]:
    # 分页与数据访问都来自依赖，函数体只剩 3 行
    total, items = repo.list(skip=page.skip, limit=page.limit)
    return {"total": total, "skip": page.skip, "limit": page.limit, "items": items}


@app.get("/items/{item_id}", response_model=ItemRead)
async def read_item(item_id: int, repo: RepoDep) -> dict[str, object]:
    return repo.get(item_id)


@app.post("/items", status_code=status.HTTP_201_CREATED, response_model=ItemRead)
async def create_item(
    payload: ItemCreate,
    repo: RepoDep,
    now: Annotated[datetime, Depends(get_now)],
) -> dict[str, object]:
    record = payload.model_dump()
    record.update(status="active", created_at=now)
    return repo.add(record)


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, repo: RepoDep) -> None:
    repo.delete(item_id)
```

关键点：

- **`RepoDep = Annotated[ItemRepository, Depends(get_repo)]`**：把「类型 + 依赖」定义成别名，签名里只写 `repo: RepoDep`，读起来就像普通类型注解。这是 FastAPI 官方推荐的现代写法。
- **依赖和普通参数混用**：`item_id: int` 来自路径，`repo: RepoDep` 来自依赖，`now` 来自另一个依赖，FastAPI 能同时处理，声明顺序不影响解析。
- **`now: Annotated[datetime, Depends(get_now)]`**：这就是「子依赖」的实际用法——依赖函数本身不需要接收 `now`，而是由路由把两个依赖并列注入，谁需要谁声明，耦合最低。

## 🛠 Step 3：验证依赖缓存

```python
# 临时演示：同一个依赖在一请求内被调用几次
from fastapi import Depends, FastAPI

app = FastAPI()
call_count = {"n": 0}


def trace() -> str:
    call_count["n"] += 1
    return "dep-" + str(call_count["n"])


@app.get("/cache-demo")
async def cache_demo(
    a: Annotated[str, Depends(trace)],
    b: Annotated[str, Depends(trace)],
) -> dict[str, str]:
    # a 与 b 会是同一个值，说明 trace 只执行了一次
    return {"a": a, "b": b, "calls": str(call_count["n"])}
```

请求 `/cache-demo` 得到 `{"a": "dep-1", "b": "dep-1", "calls": "1"}`。这就是**依赖缓存**：同一个请求内，同一个可调用对象 + 相同参数只会执行一次，结果被复用。

需要每次都执行时（例如「每次都要取一个新的数据库连接」），可以关闭缓存：

```python
a: Annotated[str, Depends(trace, use_cache=False)]
```

## 运行效果

```text
$ curl "http://127.0.0.1:8000/items?skip=1&limit=2"
{"total":4,"skip":1,"limit":2,"items":[
 {"id":2,"name":"买牛奶","status":"done","price":12.5},
 {"id":3,"name":"整理笔记","status":"active","price":0.0}]}

$ curl "http://127.0.0.1:8000/items?limit=0"
HTTP/1.1 422 Unprocessable Entity
{"detail":[{"type":"greater_than_equal","loc":["query","limit"],
"msg":"Input should be greater than or equal to 1","input":"0"}]}

$ curl "http://127.0.0.1:8000/items/99"
{"code":"ITEM_NOT_FOUND","message":"待办事项 99 不存在","detail":null}
```

注意第二个请求：`limit=0` 的错误来自依赖函数里的 `Query(ge=1)`，但对外表现与写在路由里完全一样。**依赖不是黑盒，它参与完整的参数校验与文档生成**。

## 常见坑

**在依赖里 `raise HTTPException` 又在路由里捕获**：依赖抛出的异常不会被路由的 try/except 捕获，因为依赖在进入函数体之前就执行了。要统一格式，用第 4 课的全局异常处理器。

**yield 依赖里忘了 try/finally**：`yield` 之后直接 `close()`，一旦路由抛异常，`close` 不会执行，连接泄漏。正确写法一定是 `try: yield x finally: cleanup()`。

**以为依赖缓存是「跨请求」的**：缓存只在单次请求内有效，请求结束即销毁。想缓存全局数据（如配置、连接池）应该用模块级变量或 `lru_cache`，不要指望依赖缓存。

**在依赖里做重活**：每个接口都执行的依赖如果去查一次大表，整体性能会被拖垮。依赖只做「准备动作」，真正的查询放在路由或 service 层。

**`Annotated` 里类型和依赖不匹配**：`Annotated[ItemRepository, Depends(get_repo)]` 中，`get_repo` 的返回值必须能赋给 `ItemRepository`。写错类型时编辑器不报错，运行时才暴露，建议开启 mypy 检查。

## 课后练习

1. 写一个 `get_request_id` 依赖，从请求头 `X-Request-ID` 读取并返回，没有就生成一个 uuid 字符串；在三个接口里注入它并放进响应头。
2. 写一个 `get_current_user_stub` 依赖，从 `Authorization` 头读取 `Bearer demo`，不匹配就抛 401；把它加在删除接口上，验证 401 响应格式。
3. 把 `deps.py` 里的 `ItemRepository` 改成构造时接收 `skip`/`limit`，用 `Depends(ItemRepository)` 直接注入类，对比与当前工厂函数写法的差异。

## 下一课预告

有了 `get_db` 这个模板，下一课把内存列表换成真正的数据库：SQLAlchemy 2.0 异步引擎、声明式模型、CRUD 与分页查询，接口签名一行都不用改。""",
    },
    {
        "title": "第 6 课：数据库接入（SQLAlchemy 2.0 async）",
        "summary": "把内存列表换成真正的数据库：异步引擎、声明式模型、CRUD 与分页查询，事务提交与回滚一次讲透。",
        "difficulty": 2,
        "tags": ["FastAPI", "SQLAlchemy 2.0", "异步数据库"],
        "duration_minutes": 35,
        "content": """## 🎯 本课目标

- 用 `create_async_engine` + `async_sessionmaker` 搭出异步数据库层，默认 SQLite，可一行切到 MySQL
- 用 SQLAlchemy 2.0 的 `Mapped` / `mapped_column` 定义 `User` 与 `Item` 两个模型
- 用 `select()` + `await session.execute()` 写分页查询，并用 `func.count()` 单独取总数
- 说清事务边界：会话依赖负责提交与回滚，路由里不要再手动 commit
- 把第 5 课的 `get_repo` 换成 `get_db`，接口的 URL 与响应结构保持不变

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| database.py | 异步引擎、会话工厂、Base、get_db 依赖 |
| models.py | User / Item 两张表 |
| crud.py | 所有数据库读写函数 |
| deps.py | 增加 `DbDep`，删除内存仓库 |
| main.py | 改用 lifespan 建表，路由改用数据库 |

## 承接上一课

第 5 课的 `deps.py` 里有一个 `get_repo` 工厂，它背后是内存列表；本课把它的实现整体替换为「SQLAlchemy 会话 + crud 函数」，`main.py` 里的路由只把 `repo` 换成 `db`，其余逻辑不动。

## 📖 概念讲解

### 同步 ORM 在异步框架里会出什么事

SQLAlchemy 传统的 `Session` 是同步阻塞的。在 `async def` 路由里直接用它，每次查库都会卡住事件循环，并发能力退化成单线程。解决办法是使用**异步驱动 + 异步会话**：

| 层次 | 同步写法 | 异步写法 |
| --- | --- | --- |
| 引擎 | `create_engine` | `create_async_engine` |
| 驱动 | pymysql / psycopg2 | aiomysql / asyncpg / aiosqlite |
| 会话 | `sessionmaker` | `async_sessionmaker` |
| 查询 | `session.execute(stmt)` | `await session.execute(stmt)` |

异步只是把「等待 IO」的控制权交回事件循环。写代码时记住一条：**所有涉及数据库的调用前都要加 `await`**，漏一个就会拿到协程对象而不是数据。

### 数据库 URL 与驱动

| 数据库 | URL 示例 | 需要安装 |
| --- | --- | --- |
| SQLite（默认） | `sqlite+aiosqlite:///./todo.db` | `aiosqlite` |
| MySQL | `mysql+aiomysql://user:pwd@127.0.0.1:3306/todo` | `aiomysql` |
| PostgreSQL | `postgresql+asyncpg://user:pwd@127.0.0.1:5432/todo` | `asyncpg` |

URL 里 `+` 后面就是驱动名，**不写驱动会默认走同步版本**，然后在 await 时报出让人摸不着头脑的错误。本课程默认 SQLite，因为它零安装、单文件，学完换 MySQL 只改一行环境变量。

### 声明式模型：Mapped 与 mapped_column

SQLAlchemy 2.0 用类型注解描述列：

```python
name: Mapped[str] = mapped_column(String(50), index=True)
price: Mapped[float] = mapped_column(Float, default=0.0)
owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
```

`Mapped[str]` 表示「非空字符串列」，`Mapped[int | None]` 表示「可空整数列」——**可空性由类型里的 None 决定**，不需要再写 `nullable=True`。这是 2.0 最舒服的改进：类型与数据库约束保持一致，编辑器还能给出补全。

## 🛠 Step 1：database.py——引擎与会话

```python
# database.py：数据库连接层，全课程唯一入口
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# 默认用 SQLite；换 MySQL 只需改这一行，例如：
# mysql+aiomysql://root:123456@127.0.0.1:3306/todo?charset=utf8mb4
DATABASE_URL = "sqlite+aiosqlite:///./todo.db"

# echo=True 会把执行的 SQL 打到终端，学习阶段强烈建议打开
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # 取连接前先探活，避免 MySQL 8 小时断连
)

# expire_on_commit=False：提交后对象仍可读，响应序列化不会触发额外查询
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    # 所有 ORM 模型的基类，Base.metadata 里收集全部表结构
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # yield 依赖：请求开始时开会话，结束时提交，出错则回滚
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

逐段说明：

- **`echo=True`**：能看到每条 SQL 与参数，排查「为什么查出来是空」时非常有用。上线前记得关掉或改由日志级别控制，否则日志量会很吓人。
- **`pool_pre_ping=True`**：MySQL 默认 8 小时断开空闲连接，连接池里可能躺着死连接。开启后每次取连接先 ping 一下，代价很小，收益很大。
- **`expire_on_commit=False`**：默认提交后对象属性会过期，下次访问触发懒加载；在异步里懒加载会直接抛 `MissingGreenlet`。关掉它是异步项目的标配。
- **`async with SessionLocal()`**：会话本身是异步上下文管理器，退出时自动关闭连接，比手写 close 更安全。
- **`try / except / raise`**：异常时回滚再原样抛出，交给第 4 课的全局处理器；**不要吞掉异常**，否则前端会收到 500 但日志里什么都没有。
- **提交放在依赖里**：这是本课程的选择——所有写操作在请求结束时统一提交。好处是路由不用记 commit，多个写操作天然在同一事务里；代价是如果提交失败，错误发生在响应生成之后，所以第 15 课的生产清单里会加「关键写操作用显式事务块」。

## 🛠 Step 2：models.py——两张表

```python
# models.py：ORM 模型定义
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # 一对多：删除用户时级联删除他的待办
    items: Mapped[list["Item"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # 外键允许为空：允许先存在「无主」的历史数据
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User | None"] = relationship(back_populates="items")
```

关键点：

- **`__tablename__` 必须写**：不写会报 `Class does not have a __tablename__`，SQLAlchemy 不会猜表名。
- **`String(50)` 与 `index=True`**：字符串列必须给长度（MySQL 强要求）；`name` 与 `status` 建索引，因为列表接口常按这两列过滤。
- **`server_default=func.now()`**：由数据库生成时间，避免应用服务器时钟不一致。注意它和 `default=` 的区别：前者写进建表语句，后者是 Python 侧的默认值。
- **`Mapped[list["Item"]]`**：字符串前向引用，解决 User 定义时 Item 还没定义的问题。
- **`cascade="all, delete-orphan"`**：删除用户时一并删除其待办，避免出现指向不存在用户的外键脏数据。这个级联是 ORM 层行为，不是数据库外键的 ON DELETE。

## 🛠 Step 3：crud.py 与路由改造

```python
# crud.py：所有数据库操作集中在这里
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Item
from schemas import ItemCreate


async def list_items(
    db: AsyncSession,
    skip: int,
    limit: int,
    status: str | None = None,
) -> tuple[int, list[Item]]:
    # 1. 基础语句：select(Item) 等价于 SELECT * FROM items
    stmt = select(Item)
    count_stmt = select(func.count()).select_from(Item)

    # 2. 条件要同时加到两条语句上，否则总数会对不上
    if status is not None:
        stmt = stmt.where(Item.status == status)
        count_stmt = count_stmt.where(Item.status == status)

    # 3. 先取总数，再取当前页
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(Item.id).offset(skip).limit(limit)
    )
    return total, list(result.scalars().all())


async def get_item(db: AsyncSession, item_id: int) -> Item | None:
    # db.get 按主键查询，比手写 where 更快也更简洁
    return await db.get(Item, item_id)


async def create_item(db: AsyncSession, payload: ItemCreate, owner_id: int | None) -> Item:
    item = Item(**payload.model_dump(), owner_id=owner_id)
    db.add(item)
    # flush 把 INSERT 发出去并回填自增 id，但不提交事务
    await db.flush()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item: Item) -> None:
    await db.delete(item)
    await db.flush()
```

然后是 `main.py` 的启动与路由：

```python
# main.py：接入数据库
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import models  # noqa: F401  确保模型被导入，Base.metadata 才知道有哪几张表
from crud import create_item, delete_item, get_item, list_items
from database import Base, engine, get_db
from schemas import ItemCreate, ItemRead

DbDep = Annotated[AsyncSession, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表；真实项目用第 14 课的 Alembic 迁移代替
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="FastAPI Todo API", version="0.6.0", lifespan=lifespan)


@app.get("/items")
async def read_items(
    db: DbDep,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
) -> dict[str, object]:
    total, items = await list_items(db, skip=skip, limit=limit, status=status)
    # from_attributes 允许直接把 ORM 对象交给 Pydantic 校验
    return {
        "total": total,
        "items": [ItemRead.model_validate(item) for item in items],
    }


@app.post("/items", status_code=status.HTTP_201_CREATED, response_model=ItemRead)
async def add_item(payload: ItemCreate, db: DbDep) -> models.Item:
    return await create_item(db, payload, owner_id=None)


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(item_id: int, db: DbDep) -> None:
    item = await get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await delete_item(db, item)
```

关键点：

- **`import models` 不是多余的**：`Base.metadata` 只有被导入过的模型才会登记。忘了导入，建表时数据库里一张表都没有，而且不报错。
- **`lifespan` 替代 `@app.on_event("startup")`**：后者已废弃，新版官方推荐用异步上下文管理器，启动与关闭逻辑写在一处。
- **`ItemRead.model_validate(item)`**：把 ORM 对象转成模型实例。如果路由直接声明 `response_model=ItemRead` 并返回 ORM 对象，FastAPI 内部也会做这一步，两种方式等价。
- **`await list_items(...)`**：crud 函数全是 async，漏掉 await 会返回协程对象，序列化时报 `Object of type coroutine is not JSON serializable`。
- **没有 commit**：提交在 `get_db` 里统一做。删除接口调用 `db.delete` 后直接返回 204，事务由依赖兜底。

## 运行效果

```text
$ pip install sqlalchemy aiosqlite
$ uvicorn main:app --reload
INFO:     Application startup complete.

$ curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name":"买牛奶","price":12.5}'
2026-11-12 10:41:02,113 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-11-12 10:41:02,114 INFO sqlalchemy.engine.Engine INSERT INTO items (name, price, status, created_at, owner_id) VALUES (?, ?, ?, ?, ?)
2026-11-12 10:41:02,114 INFO sqlalchemy.engine.Engine [generated in 0.00021s] ('买牛奶', 12.5, 'active', None, None)
2026-11-12 10:41:02,116 INFO sqlalchemy.engine.Engine COMMIT
HTTP/1.1 201 Created
{"id":1,"name":"买牛奶","price":12.5,"tags":[],"owner":null,"created_at":"2026-11-12T02:41:02"}

$ curl "http://127.0.0.1:8000/items?limit=5"
INFO sqlalchemy.engine.Engine SELECT count(*) AS count_1 FROM items
INFO sqlalchemy.engine.Engine SELECT items.id, items.name, ... FROM items ORDER BY items.id LIMIT ? OFFSET ?
{"total":1,"items":[{...}]}
```

注意最后两行 SQL：一条 count，一条分页查询，这正是 `list_items` 里两条语句的对应输出。看到 `BEGIN (implicit)` 说明事务由会话自动开启，`COMMIT` 则来自依赖。

## 常见坑

**驱动没装或 URL 写错**：`sqlite:///./todo.db` 是同步写法，异步必须写 `sqlite+aiosqlite:///`。报错通常是 `MissingGreenlet` 或 `No module named aiosqlite`，先检查 URL 与依赖。

**在异步里访问未加载的关系属性**：`item.owner.email` 会触发懒加载，异步会话直接抛 `MissingGreenlet`。要么在查询时 `selectinload(Item.owner)` 预加载，要么只返回外键 id。

**路由里再 `await db.commit()`**：依赖里已经提交，路由再提交一次虽然不报错，但事务边界变得模糊；出问题时不知道是哪次提交生效。**一处提交，别分散**。

**`expire_on_commit` 保持默认 True**：提交后对象属性全部过期，序列化响应时又去查库，触发懒加载错误。异步项目请显式设成 False。

**建表时用了 `create_all` 就以为万事大吉**：它只建不存在的表，**不会修改已有表结构**。加字段必须靠第 14 课的 Alembic 迁移，否则线上表结构会与代码不一致。

## 课后练习

1. 给 `list_items` 增加 `min_price` 与 `max_price` 过滤，并保证 count 与列表使用同一组 where 条件；用两条数据验证 total 正确。
2. 给 `Item` 增加 `priority` 列（`String(16)`，默认 `normal`），用 `create_all` 重建数据库并观察表结构；再说明为什么线上不能这么做。
3. 把 `DATABASE_URL` 改成从环境变量读取，默认值保持 SQLite；用 `DATABASE_URL=sqlite+aiosqlite:///./test.db uvicorn main:app` 验证切换成功。

## 下一课预告

数据库里有了 users 表，但还没有任何注册登录逻辑——下一课实现密码哈希、JWT 签发与 `get_current_user`，让待办事项真正归属于某个人。""",
    },
    {
        "title": "第 7 课：用户注册与 JWT 登录",
        "summary": "从密码哈希到 JWT 签发校验，实现注册、登录与 get_current_user，让接口知道「你是谁」。",
        "difficulty": 2,
        "tags": ["FastAPI", "JWT", "认证"],
        "duration_minutes": 35,
        "content": """## 🎯 本课目标

- 用 bcrypt 做密码哈希，理解为什么数据库里绝不能存明文密码
- 实现 `POST /auth/register` 与 `POST /auth/login` 两个接口
- 用 PyJWT 签发带 `sub`、`exp` 的 access token，并正确校验过期与签名
- 写出 `get_current_user` 依赖，配合 `OAuth2PasswordBearer` 完成 Bearer 认证
- 把待办事项的创建与查询绑定到当前登录用户，实现数据隔离

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| security.py | 密码哈希、JWT 签发与解码 |
| schemas.py | 新增 UserCreate、UserRead、Token |
| deps.py | 新增 oauth2_scheme 与 get_current_user |
| main.py | 注册、登录接口；items 接口改为需登录 |

## 承接上一课

第 6 课的 `models.py` 里 `User` 表已经建好（含 `hashed_password` 与 `is_admin`），`database.py` 的 `get_db` 继续使用；本课只往里填认证逻辑，不改表结构。

## 📖 概念讲解

### 认证与授权的区别

| 概念 | 回答的问题 | 本课/下节课 |
| --- | --- | --- |
| 认证 Authentication | 你是谁 | 本课：登录拿 token |
| 授权 Authorization | 你能干什么 | 第 8 课：角色与权限 |

先认证再授权是固定顺序。401 表示「没认出你是谁」，403 表示「认出来了但不许你这么干」，两者不能混用。

### 为什么用 JWT 而不是服务端 Session

| 维度 | Session + Cookie | JWT |
| --- | --- | --- |
| 状态存放 | 服务端（内存/Redis） | 客户端持有签名串 |
| 横向扩展 | 需要共享存储 | 无状态，天然可扩展 |
| 主动失效 | 删 session 即生效 | 只能等过期或维护黑名单 |
| 跨端支持 | 浏览器友好 | 移动端、第三方调用都方便 |

JWT 的代价是**无法单条撤销**，所以有效期要短（本课程 30 分钟），需要长效登录时配 refresh token。这个取舍在选型时必须说清楚，别把它当成「更先进的 Session」。

JWT 由三段 Base64 组成：header.payload.signature。payload 是**明文可读**的，只是不能篡改。因此：

- 可以放 `sub`（用户 id）、`exp`（过期时间）、`iat`（签发时间）；
- 绝不能放密码、手机号、身份证号等敏感信息；
- 签名密钥必须保密，泄露等于任何人都能伪造身份。

### 密码哈希的三条铁律

1. **用专门的哈希算法**：bcrypt、argon2，不要用 md5、sha256。后者太快，适合校验文件完整性，不适合存密码。
2. **每个用户独立加盐**：bcrypt 内置随机盐，同一密码两次哈希结果不同，这是正常现象。
3. **校验用 `verify` 而不是比较哈希值**：`pwd_context.verify(明文, 哈希)` 会自动提取盐并做恒定时间比较。

## 🛠 Step 1：security.py——哈希与 JWT

```python
# security.py：密码与令牌
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

# 生产环境必须从环境变量读取，且长度足够随机
SECRET_KEY = "dev-only-secret-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # bcrypt 只处理前 72 字节，超长密码要先截断或改用 argon2
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 恒定时间比较，避免时序攻击
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, is_admin: bool = False) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),                        # subject：用户标识
        "admin": is_admin,                          # 自定义声明，省一次查库
        "iat": now,                                 # 签发时间
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, object]:
    # 校验签名与 exp，失败会抛 jwt.PyJWTError 的子类
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

逐段说明：

- **`CryptContext(schemes=["bcrypt"])`**：passlib 的哈希上下文，`deprecated="auto"` 让旧算法哈希在下次登录时自动升级。
- **`sub` 必须是字符串**：PyJWT 2.10 起对 `sub` 做了类型校验，传 int 会在解码时被拒绝。这是很多人升级后突然 401 的原因。
- **`exp` 用 UTC 时间**：`datetime.now(timezone.utc)`，不要用本地时间，否则跨时区部署会提前或延后过期。
- **`algorithms=[ALGORITHM]`**：解码时必须显式指定算法列表，这是防止「算法混淆攻击」的关键——绝不能从 token 头部读取算法。
- **额外放 `admin` 声明**：可以让权限判断少查一次库，但代价是**改了权限要等 token 过期才生效**。数据敏感的场景应每次查库，本课程第 8 课就是这么做的。

## 🛠 Step 2：schemas 与 deps 的认证部分

```python
# schemas.py 追加
class UserCreate(BaseModel):
    email: Annotated[str, Field(min_length=5, max_length=120)]
    password: Annotated[str, Field(min_length=8, max_length=64)]


class UserRead(BaseModel):
    # 只有这两个字段会出现在响应里，hashed_password 永远不出去
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

```python
# deps.py 追加
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from security import decode_token

DbDep = Annotated[AsyncSession, Depends(get_db)]

# tokenUrl 只用于文档里的授权按钮，指向登录接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbDep,
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        # 签名错、过期、格式错都归到这里，不向客户端区分原因
        raise credentials_error

    subject = payload.get("sub")
    if subject is None:
        raise credentials_error

    user = await db.get(User, int(subject))
    if user is None:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
```

关键点：

- **`OAuth2PasswordBearer`**：它只做一件事——从 `Authorization: Bearer xxx` 里取出 token，取不到就自动返回 401。它不负责校验，校验在 `get_current_user` 里。
- **为什么要统一错误文案**：如果「用户不存在」和「token 过期」返回不同提示，攻击者可以借此枚举有效用户 id。统一文案、统一 401。
- **`headers={"WWW-Authenticate": "Bearer"}`**：401 的标准响应头，某些客户端与网关依赖它判断认证方式。
- **`db.get(User, int(subject))`**：每次请求都查库确认用户仍然存在。用户被删除后 token 立刻失效，这比把用户信息全塞进 token 更安全。
- **`CurrentUser` 别名**：后面所有需要登录的接口写 `user: CurrentUser` 即可，语义一目了然。

## 🛠 Step 3：注册与登录接口

```python
# main.py：认证相关接口
from fastapi.security import OAuth2PasswordRequestForm

from schemas import Token, UserCreate, UserRead
from security import create_access_token, hash_password, verify_password


@app.post("/auth/register", status_code=201, response_model=UserRead)
async def register(payload: UserCreate, db: DbDep) -> User:
    # 1. 先查重，邮箱唯一
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="邮箱已被注册")

    # 2. 只存哈希，明文密码用完即弃
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbDep,
) -> Token:
    # OAuth2 规范用 form-data 提交 username / password
    user = await db.scalar(select(User).where(User.email == form.username))
    if user is None or not verify_password(form.password, user.hashed_password):
        # 不区分「用户不存在」和「密码错误」
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    return Token(access_token=create_access_token(user.id, user.is_admin))


@app.get("/items/mine", response_model=list[ItemRead])
async def my_items(user: CurrentUser, db: DbDep) -> list[Item]:
    result = await db.execute(select(Item).where(Item.owner_id == user.id))
    return list(result.scalars().all())
```

还需要在 `create_item` 里绑上归属人：

```python
@app.post("/items", status_code=201, response_model=ItemRead)
async def add_item(payload: ItemCreate, user: CurrentUser, db: DbDep) -> Item:
    # owner_id 来自 token 解出的用户，客户端无法伪造
    return await create_item(db, payload, owner_id=user.id)
```

逐条说明：

- **`OAuth2PasswordRequestForm` 用 `Depends()` 无参数写法**：这个类本身就是依赖，FastAPI 会自动从 form-data 里取 username/password。注意它要求 `python-multipart`，没装会报错。
- **`select(User).where(...)` + `db.scalar`**：`scalar` 取第一行第一列，比 `execute` 再 `.scalar_one_or_none()` 更短。找不到返回 None，不会抛异常。
- **`await db.flush()` 后 `refresh`**：拿到自增 id 与数据库生成的 `created_at`，否则响应里 `id` 是 None。
- **注册时不做自动登录**：让客户端显式调一次登录接口，流程更清晰；如果想省一次请求，也可以在注册响应里直接返回 token。
- **`user: CurrentUser` 放在 `db` 前面**：参数顺序不影响依赖解析，但把认证放前面读起来更符合「先验身份再查数据」的直觉。

## 运行效果

```text
$ curl -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" -d '{"email":"tom@example.com","password":"secret123"}'
HTTP/1.1 201 Created
{"id":1,"email":"tom@example.com"}

$ curl -X POST http://127.0.0.1:8000/auth/login -d "username=tom@example.com&password=secret123"
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiYWRtaW4iOmZhbHNlLCJpYXQiOjE3MzE0MDgwMDAsImV4cCI6MTczMTQxMTYwMH0.7f3k...","token_type":"bearer"}

$ curl http://127.0.0.1:8000/items/mine
HTTP/1.1 401 Unauthorized
{"detail":"Not authenticated"}

$ curl http://127.0.0.1:8000/items/mine -H "Authorization: Bearer eyJhbGciOi..."
{"total":0,"items":[]}
```

注意第三次请求：连 `get_current_user` 都没进，`OAuth2PasswordBearer` 发现没有 Authorization 头就直接返回 401，文案是框架默认的 `Not authenticated`。想统一文案，可以在 `OAuth2PasswordBearer(auto_error=False)` 后自己处理。

## 常见坑

**passlib 与新版 bcrypt 冲突**：`AttributeError: module 'bcrypt' has no attribute '__about__'`。解决办法是 `pip install "bcrypt<4.1"`，或直接改用 `bcrypt` 库自己封装。这个报错不影响哈希结果，只影响日志输出，但会让人误以为登录坏了。

**token 里放 int 类型的 sub**：PyJWT 新版本解码时校验 `sub` 必须是字符串，传 int 会抛 `InvalidSubjectError`，表现为「刚登录就 401」。统一 `str(user.id)`。

**把 SECRET_KEY 写死在代码里并提交仓库**：等于把签名密钥公开。必须走环境变量，且不同环境用不同密钥；轮换密钥会导致所有已签发 token 失效，这是预期行为。

**登录接口用 JSON 传参**：`OAuth2PasswordRequestForm` 要求 `application/x-www-form-urlencoded`。前端用 JSON 提交会得到 422。要么改前端表单编码，要么自己定义一个 JSON 登录模型。

**以为 token 加密了**：JWT 只是签名，payload base64 解码就能看。任何敏感数据都不能放进去，调试时可以去 jwt.io 粘贴看看。

## 课后练习

1. 给 `Token` 增加 `expires_in` 字段（秒），登录时返回 1800，前端据此安排刷新时机。
2. 实现 `GET /auth/me`，返回当前登录用户的 `UserRead`，并验证不带 token 与带错误 token 两种情况的响应。
3. 把 access token 有效期改成 1 分钟，登录后等待 65 秒再请求，记录 401 的响应，并思考 refresh token 该如何设计。

## 下一课预告

现在任何登录用户都能删任何人的待办——下一课加上角色校验依赖与中间件，把「谁能做什么」和「请求经过了什么」都管起来。""",
    },
    {
        "title": "第 8 课：权限控制与中间件",
        "summary": "用依赖工厂做角色校验，配好 CORS、请求日志与全局异常中间件，把横切关注点从业务代码里彻底剥离。",
        "difficulty": 2,
        "tags": ["FastAPI", "权限控制", "中间件"],
        "duration_minutes": 32,
        "content": """## 🎯 本课目标

- 写一个「依赖工厂」，按角色动态生成权限校验依赖，避免为每个角色复制粘贴
- 理解资源级权限：管理员能删所有，普通用户只能删自己的
- 正确配置 CORSMiddleware，说清 `allow_origins=["*"]` 与 `allow_credentials` 的冲突
- 用 `@app.middleware("http")` 写请求日志中间件，记录方法、路径、状态码与耗时
- 用中间件做全局异常兜底，保证任何未捕获异常都返回统一 JSON

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| permissions.py | 角色依赖工厂与资源归属校验 |
| middleware.py | 请求日志、请求 ID、异常兜底中间件 |
| main.py | 注册 CORS 与中间件，管理接口加权限 |

## 承接上一课

第 7 课的 `get_current_user` 与 `CurrentUser` 别名继续使用；本课在它之上加一层「角色判断」，并给第 6 课已有的删除、更新接口补上归属校验。

## 📖 概念讲解

### 三层权限模型

| 层级 | 判断依据 | 实现方式 |
| --- | --- | --- |
| 认证 | 有没有有效 token | 第 7 课的 `get_current_user` |
| 角色 | 用户是不是 admin | 依赖工厂 `require_role` |
| 资源归属 | 这条数据是不是他的 | 查到对象后比较 `owner_id` |

三层缺一不可。只做角色不做归属，会出现「任何普通用户都能删别人的待办」；只做归属不做角色，管理员反而管不了别人的数据。

### 依赖工厂：用函数生成依赖

FastAPI 的依赖就是一个可调用对象，所以可以写一个**返回依赖函数的函数**：

```python
def require_role(role: str):
    async def checker(user: CurrentUser) -> User:
        ...
    return checker
```

调用 `Depends(require_role("admin"))` 时，`require_role("admin")` 先执行并返回 `checker`，FastAPI 再把它当依赖调用。这样十个角色也只需要一个函数，权限规则集中在一处。

### 中间件在请求链的哪个位置

请求进来后的顺序大致是：

```text
客户端 → CORS 中间件 → 自定义中间件 → 路由依赖 → 路由函数 → 响应原路返回
```

中间件适合做「与具体路由无关」的事：日志、计时、请求 ID、CORS 头、全局异常兜底。不适合做业务判断——中间件里拿不到路径参数，也拿不到 Pydantic 模型。

**注意**：`@app.middleware("http")` 基于 `BaseHTTPMiddleware`，它会缓冲响应体，对流式响应（SSE、大文件下载）有影响。第 15 课的生产清单里会提到，必要时改用纯 ASGI 中间件。

## 🛠 Step 1：permissions.py——角色与归属

```python
# permissions.py：权限判断集中在这里
from typing import Annotated

from fastapi import Depends, HTTPException, status

from deps import CurrentUser
from models import Item, User


def require_admin(user: CurrentUser) -> User:
    # 角色校验：只要不是管理员就 403，不再往下走
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user


AdminUser = Annotated[User, Depends(require_admin)]


def ensure_item_access(item: Item, user: User) -> None:
    # 资源归属校验：管理员放行，普通用户只能操作自己的数据
    if user.is_admin:
        return
    if item.owner_id != user.id:
        # 故意返回 404 而不是 403，避免泄露「这条数据存在」
        raise HTTPException(status_code=404, detail="Item not found")
```

逐段说明：

- **`require_admin` 直接依赖 `CurrentUser`**：形成「认证 → 角色」的依赖链，FastAPI 自动按顺序解析，token 无效时先返回 401，不会走到 403。
- **`AdminUser` 别名**：管理接口写 `admin: AdminUser` 即可，签名自解释。
- **`ensure_item_access` 是普通函数不是依赖**：它需要已经查出的 `item`，而 item 依赖路径参数与数据库，写成普通函数在路由里显式调用更清晰。
- **返回 404 而非 403**：这是安全实践。403 等于告诉攻击者「这个 id 存在，只是你没权限」，可以被用来枚举数据；404 则什么都不透露。

## 🛠 Step 2：middleware.py——日志与兜底

```python
# middleware.py：横切逻辑
import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.request")


def register_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_context(
        request: Request,
        call_next: Callable[[Request], Awaitable[object]],
    ):
        # 1. 每个请求一个 ID，方便串联日志
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        request.state.request_id = request_id

        # 2. 记录开始时间
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # 3. 兜底：未捕获异常统一转 500，绝不把堆栈返回给客户端
            logger.exception("unhandled error, request_id=%s", request_id)
            return JSONResponse(
                status_code=500,
                content={"code": "INTERNAL_ERROR", "message": "服务器内部错误"},
            )

        # 4. 记录耗时并回写请求 ID
        cost_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "%s %s -> %s %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            cost_ms,
        )
        return response
```

关键点：

- **`request.state`**：请求级别的命名空间，中间件写进去的值，路由和依赖都能读到。第 12 课会用它做请求 ID 追踪。
- **`time.perf_counter()`**：单调递增的高精度计时器，比 `time.time()` 适合测耗时（不受系统时间调整影响）。
- **`logger.exception`**：只在异常处理分支里用，它会自动带上堆栈。正常日志用 `logger.info`。
- **`JSONResponse` 直接返回**：中间件里不能再 `raise`，否则会被外层再次捕获，形成混乱的错误链。
- **`call_next` 的返回值是 Response**：可以修改 headers 后再返回，这是加 `X-Request-ID`、`X-Process-Time` 的标准位置。

## 🛠 Step 3：在 main.py 里装配

```python
# main.py：注册 CORS、中间件与权限
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware import register_middlewares
from permissions import AdminUser, ensure_item_access

app = FastAPI(title="FastAPI Todo API", version="0.8.0", lifespan=lifespan)

# CORS 必须加在最外层，否则错误响应会缺少跨域头，前端只能看到 Network Error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

register_middlewares(app)


@app.delete("/items/{item_id}", status_code=204)
async def remove_item(item_id: int, user: CurrentUser, db: DbDep) -> None:
    item = await get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    ensure_item_access(item, user)
    await delete_item(db, item)


@app.get("/admin/items", response_model=list[ItemRead])
async def admin_list_items(admin: AdminUser, db: DbDep) -> list[Item]:
    # 管理接口：只有 is_admin 为 True 的用户能进
    result = await db.execute(select(Item).order_by(Item.id))
    return list(result.scalars().all())
```

装配顺序有两个细节：

- **`add_middleware(CORSMiddleware, ...)` 要在自定义中间件之前**：Starlette 的中间件是「后加的先执行」外层。CORS 放最后加，实际就在最外层，能保证 500 错误响应也带上跨域头，前端才能读到错误信息。
- **`allow_origins` 不要写 `["*"]` 同时开 `allow_credentials=True`**：浏览器规范禁止通配符与凭证同时使用，配置了也不生效。开发期直接列出前端地址，生产期从配置读。
- **`expose_headers=["X-Request-ID"]`**：跨域时自定义响应头默认对 JS 不可见，必须显式暴露，否则前端拿不到请求 ID，报障时没法对日志。

## 运行效果

```text
$ curl -X DELETE http://127.0.0.1:8000/items/3 -H "Authorization: Bearer <普通用户 token>"
HTTP/1.1 404 Not Found
{"detail":"Item not found"}

$ curl http://127.0.0.1:8000/admin/items -H "Authorization: Bearer <普通用户 token>"
HTTP/1.1 403 Forbidden
{"detail":"需要管理员权限"}

$ curl http://127.0.0.1:8000/admin/items -H "Authorization: Bearer <管理员 token>"
[{"id":1,"name":"买牛奶",...}]

# 服务端日志
INFO:app.request:GET /items -> 200 12.4ms
INFO:app.request:DELETE /items/3 -> 404 3.1ms
ERROR:app.request:unhandled error, request_id=9f2c...
Traceback (most recent call last):
  ...
```

注意第一行：普通用户删别人的数据返回 404 而不是 403，这是刻意的设计；第二行才是真正的 403——他知道自己是普通用户，但接口本身就不允许这类角色访问。

## 常见坑

**`allow_origins=["*"]` 配 `allow_credentials=True`**：浏览器直接拒绝，控制台报 CORS 错误且不带具体原因。要么列白名单，要么关掉凭证（改用 Authorization 头就不需要 cookie 凭证）。

**在中间件里读请求体**：`await request.body()` 读过一次后流就被消费，路由再读会得到空。需要读 body 的场景要用纯 ASGI 中间件并缓存，别在 `BaseHTTPMiddleware` 里做。

**CORS 加在自定义中间件里面**：异常响应不经过 CORS 处理，前端只能看到 «Failed to fetch»，看不到真正的 500 信息。CORS 永远最外层。

**用 `if user.id != item.owner_id: raise 403` 做归属判断**：泄露数据是否存在。统一 404，除非业务上确实需要提示「无权限」。

**中间件里做数据库操作**：每个请求都多一次查询，包括静态文件和健康检查。中间件只做轻量的事，重活放依赖或路由。

## 课后练习

1. 给 `require_role` 写一个更通用的版本：接收角色名字符串列表，用户只要满足其中一个就放行；用它保护 `/admin/items` 与新增的 `/admin/users`。
2. 在日志中间件里增加「慢请求告警」：耗时超过 500ms 时用 `logger.warning` 打一条，并带上请求 ID。
3. 故意在某个接口里抛 `RuntimeError("boom")`，验证中间件返回的是统一 JSON 而不是堆栈，并确认服务端日志里有完整 traceback。

## 下一课预告

接口能收 JSON 了，但用户还想上传头像和附件——下一课处理 `UploadFile`、大小与类型校验、静态资源挂载与文件下载。""",
    },
    {
        "title": "第 9 课：文件上传与静态资源",
        "summary": "用 UploadFile 接收文件，做大小与类型双重校验，挂载 StaticFiles 提供访问，并实现安全的下载接口。",
        "difficulty": 2,
        "tags": ["FastAPI", "文件上传", "静态资源"],
        "duration_minutes": 30,
        "content": """## 🎯 本课目标

- 用 `UploadFile` + `File` 接收单个与多个文件，理解它与 `bytes` 参数的区别
- 做三重校验：内容类型白名单、文件大小上限、扩展名与存储名分离
- 用 `StaticFiles` 挂载上传目录，让图片可以直接通过 URL 访问
- 用 `FileResponse` 实现带原始文件名的下载，理解 `Content-Disposition`
- 知道为什么**绝不能直接用用户传的文件名做存储路径**

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| files.py | 上传、下载、删除三个接口 |
| uploads/ | 上传文件目录（加入 .gitignore） |
| main.py | 挂载 `/static` 并注册 files 路由 |

## 承接上一课

第 8 课的中间件会记录每个请求的耗时与状态码，上传接口同样受益；本课新增 `files.py`，把它当作一个独立的 `APIRouter` 挂到主应用上，为第 14 课的路由拆分提前铺路。

## 📖 概念讲解

### UploadFile 与 bytes 的区别

| 维度 | `file: bytes = File()` | `file: UploadFile = File()` |
| --- | --- | --- |
| 内存占用 | 整个文件读进内存 | 超过阈值自动落临时文件 |
| 大文件支持 | 几 MB 就危险 | 可以流式分块读 |
| 元信息 | 无 | 有 filename、content_type、size |
| 异步读取 | 不支持 | `await file.read(n)` |

结论很简单：**除了几十 KB 的小图标，一律用 UploadFile**。用 bytes 接一个 500MB 的视频，服务器会直接被 OOM 打挂。

### 上传接口的三道防线

| 防线 | 检查什么 | 不做的后果 |
| --- | --- | --- |
| 类型白名单 | `content_type` 是否在允许列表 | 上传 .php、.exe 后被当成脚本执行 |
| 大小上限 | 累计读取字节数 | 磁盘被打满、带宽被拖垮 |
| 存储名重写 | 用 uuid 生成文件名 | 路径穿越、覆盖他人文件、文件名乱码 |

**`content_type` 来自客户端，可以伪造**，所以它只是第一道粗筛。真正安全的做法是：只允许特定后缀 + 服务端重新生成文件名 + 上传目录禁止执行权限。如果需要更强校验，要读文件头做魔数检测（如 PNG 的前 8 字节）。

### 路径穿越：最经典的上传漏洞

如果直接用 `file.filename` 拼路径，攻击者可以传一个名为 `../../app/main.py` 的文件，把你的源码覆盖掉。防御方式只有一条：**永远不要相信用户提供的文件名**，只取它的后缀（还要过滤），文件名自己生成。

## 🛠 Step 1：files.py——上传与校验

```python
# files.py：文件上传、下载、删除
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE = 2 * 1024 * 1024          # 单文件 2MB
CHUNK_SIZE = 256 * 1024             # 每次读 256KB
ALLOWED_TYPES = {"image/png", "image/jpeg", "application/pdf"}
ALLOWED_SUFFIX = {".png", ".jpg", ".jpeg", ".pdf"}


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: Annotated[UploadFile, File(description="支持 png / jpg / pdf，最大 2MB")],
) -> dict[str, object]:
    # 1. 类型粗筛：content_type 由客户端提供，只能当第一道过滤
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="不支持的文件类型")

    # 2. 后缀单独校验，并统一转小写
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIX:
        raise HTTPException(status_code=415, detail="不支持的文件后缀")

    # 3. 存储名由服务端生成，彻底隔断路径穿越
    stored_name = uuid.uuid4().hex + suffix
    target = UPLOAD_DIR / stored_name

    # 4. 分块写入，边写边累计大小，超限立刻删除半成品
    size = 0
    try:
        with target.open("wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                if size > MAX_SIZE:
                    raise HTTPException(status_code=413, detail="文件超过 2MB")
                out.write(chunk)
    except HTTPException:
        target.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return {
        "filename": file.filename,
        "stored_name": stored_name,
        "size": size,
        "url": "/static/" + stored_name,
    }
```

逐段解释：

- **`APIRouter(prefix="/files", tags=["files"])`**：路由分组。`tags` 会让 `/docs` 把这些接口归到一个可折叠的分组里，接口一多就知道它的价值了。
- **`Path(file.filename or "")`**：filename 可能为 None，先兜底成空串再取后缀，避免 AttributeError。
- **`uuid.uuid4().hex`**：32 位十六进制随机串，碰撞概率可以忽略。原始文件名只存进数据库供展示，绝不参与路径拼接。
- **`while chunk := await file.read(CHUNK_SIZE)`**：海象运算符，读一块判一块。读到最后返回空 bytes，循环自然结束。这是流式处理的标准写法。
- **`size > MAX_SIZE` 时抛异常**：此时文件已经写了一部分，必须 `unlink` 删掉，否则磁盘上会堆满垃圾文件。
- **`finally: await file.close()`**：无论成功失败都释放临时文件句柄，这是 UploadFile 必须做的清理。
- **`target.open("wb")` 是同步写**：本地磁盘写入很快，这样写足够。如果上传到对象存储，应换成 `await client.put_object(...)`，避免阻塞事件循环。

## 🛠 Step 2：下载接口与静态挂载

```python
@router.get("/{stored_name}")
async def download_file(stored_name: str) -> FileResponse:
    # 1. 只允许取文件名，禁止任何路径分隔符，防穿越
    if "/" in stored_name or ".." in stored_name:
        raise HTTPException(status_code=400, detail="非法文件名")

    target = UPLOAD_DIR / stored_name
    if not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")

    # 2. FileResponse 会自动处理 Content-Length 与 Range 请求
    return FileResponse(
        path=target,
        filename=stored_name,
        media_type="application/octet-stream",
    )
```

```python
# main.py：挂载静态目录并注册路由
from fastapi.staticfiles import StaticFiles

from files import router as files_router

app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.include_router(files_router)
```

关键点：

- **`app.mount` 与 `include_router` 的区别**：`mount` 把一个完整的子应用（这里是静态文件服务）挂到某个路径前缀下，不参与 OpenAPI 文档；`include_router` 只是把路由合并进来，会出现在文档里。
- **`StaticFiles(directory="uploads")`**：目录必须存在，否则启动就报 `RuntimeError: Directory 'uploads' does not exist`。所以 `files.py` 里那句 `mkdir` 不是可选的。
- **`FileResponse(filename=...)`**：会生成 `Content-Disposition: attachment; filename=...`，浏览器直接触发下载。如果希望图片在浏览器里直接显示，就不要传 filename。
- **`media_type="application/octet-stream"`**：通用二进制流，强制下载。图片想内联展示可以改成 `image/png`，但要注意别把用户上传的 HTML 用 `text/html` 返回——那是存储型 XSS 的经典入口。
- **`"/" in stored_name` 检查**：虽然路由参数本身不会匹配到斜杠，但多一层防御没有成本，尤其是将来改成从 query 取文件名时。

## 🛠 Step 3：多文件上传（可选增强）

```python
@router.post("/batch", status_code=201)
async def upload_many(
    files: Annotated[list[UploadFile], File(description="一次最多 5 个文件")],
) -> dict[str, object]:
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="一次最多上传 5 个文件")

    saved = []
    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail=file.filename + " 类型不支持")
        suffix = Path(file.filename or "").suffix.lower()
        stored_name = uuid.uuid4().hex + suffix
        content = await file.read()
        (UPLOAD_DIR / stored_name).write_bytes(content)
        saved.append({"name": file.filename, "url": "/static/" + stored_name})
        await file.close()

    return {"count": len(saved), "files": saved}
```

多文件接口的注意点：**参数名必须是 `files` 且类型是 `list[UploadFile]`**，前端表单里的字段名要一一对应，否则 FastAPI 收不到文件。批量场景下单个文件大小不好控制，更稳妥的做法是逐个调用单文件接口，把限流交给第 15 课的网关。

## 运行效果

```text
$ curl -X POST http://127.0.0.1:8000/files -F "file=@avatar.png"
HTTP/1.1 201 Created
{"filename":"avatar.png","stored_name":"5f1c9a2e8b7d4c3fa1e0d6b2c9f84a71.png",
 "size":184320,"url":"/static/5f1c9a2e8b7d4c3fa1e0d6b2c9f84a71.png"}

$ curl -I http://127.0.0.1:8000/static/5f1c9a2e8b7d4c3fa1e0d6b2c9f84a71.png
HTTP/1.1 200 OK
content-type: image/png
content-length: 184320

$ curl -X POST http://127.0.0.1:8000/files -F "file=@movie.mp4"
HTTP/1.1 415 Unsupported Media Type
{"detail":"不支持的文件类型"}

$ curl http://127.0.0.1:8000/files/..%2Fmain.py -i
HTTP/1.1 400 Bad Request
{"detail":"非法文件名"}
```

`-F` 是 curl 的表单上传参数，等价于浏览器的 `<input type="file">`。注意最后一条：路径穿越被拦住了，这是本课最重要的安全边界。

## 常见坑

**直接用 `file.filename` 拼路径**：`../../main.py` 会覆盖源码，`/etc/passwd` 在权限足够时能读到系统文件。必须重命名。

**只校验 `content_type`**：客户端能随意伪造这个头。至少要加后缀白名单，重要场景再加文件头魔数校验。

**用 `len(await file.read())` 判断大小**：这会把整个文件读进内存，2GB 的文件直接 OOM。必须分块读、边读边累加。

**上传目录可以被执行**：把 uploads 放在 Web 根目录且服务器允许执行脚本，等于给攻击者一个 webshell。Nginx 里要对上传目录单独配置，禁止执行任何脚本。

**忘了 `python-multipart`**：启动时不报错，一调用上传接口就 500，提示 `Form data requires "python-multipart" to be installed`。装它只需一条命令，但很多人卡在这里。

## 课后练习

1. 给上传接口加上「按用户隔离目录」：在 `uploads/` 下按 `user.id` 建子目录，并修改下载接口做同样的权限校验。
2. 增加 `DELETE /files/{stored_name}`，删除前校验文件存在，返回 204；再测试删除不存在的文件时的响应。
3. 把 `MAX_SIZE` 改成从环境变量读取，默认 2MB，并说明为什么生产环境的上限应该由 Nginx 的 `client_max_body_size` 再兜一层。

## 下一课预告

上传接口里那个「写文件」动作其实可以放到响应之后做——下一课讲后台任务与异步外部请求，把耗时操作从请求链路里挪走。""",
    },
    {
        "title": "第 10 课：后台任务与外部请求",
        "summary": "用 BackgroundTasks 把耗时动作挪到响应之后，用 httpx 异步调用第三方 API，并正确处理超时、重试与阻塞陷阱。",
        "difficulty": 2,
        "tags": ["FastAPI", "BackgroundTasks", "httpx"],
        "duration_minutes": 30,
        "content": """## 🎯 本课目标

- 用 `BackgroundTasks` 在响应返回后执行通知、写日志等非关键动作
- 分清 `async def` 与 `def` 后台任务的区别，知道各自会不会阻塞事件循环
- 用 `httpx.AsyncClient` 调用第三方 API，设置连接与读取超时
- 实现带指数退避的简单重试，只对可重试错误重试
- 说清 BackgroundTasks 的能力边界：什么该用它，什么必须上消息队列

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| tasks.py | 后台任务函数：Webhook 通知、审计日志 |
| external.py | httpx 客户端封装与重试逻辑 |
| main.py | 待办完成接口触发后台通知 |

## 承接上一课

第 9 课的 `files.py` 用 `APIRouter` 组织，本课新增的 `tasks.py` 与 `external.py` 都是普通模块，由路由直接调用；第 14 课会把它们归入 `services` 层。

## 📖 概念讲解

### 为什么需要后台任务

一个「把待办标记为完成」的请求，理想耗时是几十毫秒。但完成之后可能要发邮件、推 Webhook、写审计日志——这些动作慢且不重要，让用户等它们做完是浪费。

| 方案 | 用户等待 | 可靠性 | 适用 |
| --- | --- | --- | --- |
| 同步执行 | 要等全部完成 | 高（失败即报错） | 必须成功的关键步骤 |
| BackgroundTasks | 只等主逻辑 | 低（进程重启会丢） | 通知、日志、缓存刷新 |
| 消息队列（Celery/ARQ） | 只等主逻辑 | 高（可重试、可持久化） | 支付回调、大批量任务 |

BackgroundTasks 的实现非常轻：任务挂在响应对象上，响应发送完毕后由同一个进程执行。**没有持久化、没有重试、没有独立的 worker**，所以在它里面做的事必须满足「失败也无所谓」。

### async 任务与 sync 任务的执行差异

- 任务函数是 `async def`：在事件循环里 `await` 执行，**能并发**，但函数里不能有阻塞调用；
- 任务函数是 `def`：FastAPI 会把它丢到线程池执行，**不阻塞事件循环**，适合调用同步库（如 `requests`、`PIL`）。

一个常见误解是「后台任务不影响响应速度」——它对**当前请求**没影响，但对**后续请求**有影响。如果在 `async def` 任务里写 `time.sleep(10)`，这 10 秒内所有请求都会卡住。

### httpx 的超时要分三段设

| 超时类型 | 含义 | 建议值 |
| --- | --- | --- |
| connect | 建立 TCP 连接 | 3 秒 |
| read | 等待响应数据 | 5 秒 |
| write | 发送请求体 | 5 秒 |

不设超时的 httpx 默认 5 秒，看起来安全，但连接池耗尽时仍会排队。生产环境建议显式写 `httpx.Timeout(5.0, connect=3.0)`，并且**永远不要在请求处理链路里发起没有超时的外部调用**。

## 🛠 Step 1：external.py——带重试的客户端

```python
# external.py：外部 HTTP 调用的统一封装
import asyncio
import logging

import httpx

logger = logging.getLogger("app.external")

WEBHOOK_URL = "https://httpbin.org/post"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


async def post_json(url: str, payload: dict[str, object], max_attempts: int = 3) -> bool:
    # 1. 显式设置三段超时，避免连接池被慢接口拖死
    timeout = httpx.Timeout(5.0, connect=3.0)

    # 2. 复用一个 AsyncClient，连接池与 HTTP/2 都能受益
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                response = await client.post(url, json=payload)
                # 3. 4xx 是客户端错误，重试没有意义，直接失败
                if response.status_code in RETRYABLE_STATUS:
                    raise httpx.HTTPStatusError(
                        "retryable status",
                        request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                return True
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                logger.warning(
                    "post failed attempt=%s url=%s error=%s",
                    attempt,
                    url,
                    type(exc).__name__,
                )
                if attempt == max_attempts:
                    logger.error("post gave up url=%s", url)
                    return False
                # 4. 指数退避：1s、2s、4s，避免把对方打得更惨
                await asyncio.sleep(2 ** (attempt - 1))
    return False
```

逐段解释：

- **`httpx.Timeout(5.0, connect=3.0)`**：总超时 5 秒，连接阶段单独 3 秒。外部服务挂掉时，连接阶段往往就是卡点，单独限制它能更快失败。
- **`async with httpx.AsyncClient(...)`**：一次调用创建一个客户端，用完即关。高频场景应该把客户端放进 lifespan 全局复用，第 15 课会这么做。
- **`RETRYABLE_STATUS`**：只有 429 与 5xx 值得重试；400、401、404 重试一百次也是同样的结果，只会放大故障。
- **`asyncio.sleep(2 ** (attempt - 1))`**：指数退避。真实项目还应加随机抖动（jitter），避免多个客户端同时重试形成「重试风暴」。
- **返回 bool 而不是抛异常**：后台任务失败不应该影响主流程，调用方只记录即可。如果是必须在链路里成功的调用，就应该 `raise` 让请求失败。
- **`logger.warning` 带 `type(exc).__name__`**：异常字符串里可能含 URL 与参数，打印类型足够定位，也避免日志泄露请求内容。

## 🛠 Step 2：tasks.py——后台任务函数

```python
# tasks.py：后台任务，全部设计成「失败也不影响主流程」
import logging

from external import post_json

logger = logging.getLogger("app.tasks")


async def notify_item_done(item_id: int, name: str, owner_email: str) -> None:
    # 异步任务：可以 await 外部请求，不阻塞事件循环
    logger.info("notify start item_id=%s", item_id)
    ok = await post_json(
        "https://httpbin.org/post",
        {"event": "item.done", "id": item_id, "name": name},
    )
    if not ok:
        logger.warning("notify failed item_id=%s owner=%s", item_id, owner_email)


def write_audit_log(action: str, user_id: int) -> None:
    # 同步任务：FastAPI 会放到线程池执行，适合文件写入等阻塞 IO
    with open("logs/audit.log", "a", encoding="utf-8") as f:
        f.write(str(user_id) + " " + action + chr(10))
```

要点：

- **`notify_item_done` 是 `async def`**：内部是网络 IO，用异步最合适；一旦写成同步版，就得在线程池里跑，还会多占一个线程。
- **`write_audit_log` 是 `def`**：文件写入是阻塞操作，写成同步函数后 FastAPI 自动丢线程池，反而更安全。**判断标准是「函数体里有没有阻塞调用」，不是「项目是不是异步项目」**。
- **`chr(10)` 代替换行符**：避免在源码里出现转义字符，效果与 `+ "换行"` 一致；真实项目直接用 `f.write(...)` 配 `print(..., file=f)` 更清晰。
- **任务函数自己吞掉异常**：后台任务抛异常只会打一条日志，不会传给客户端。既然如此，不如在函数内部就把失败处理干净，日志更可控。

## 🛠 Step 3：在路由里挂后台任务

```python
# main.py：完成待办并触发通知
from fastapi import BackgroundTasks

from tasks import notify_item_done, write_audit_log


@app.post("/items/{item_id}/done", response_model=ItemRead)
async def mark_done(
    item_id: int,
    background: BackgroundTasks,
    user: CurrentUser,
    db: DbDep,
) -> Item:
    item = await get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    ensure_item_access(item, user)
    item.status = "done"
    await db.flush()
    await db.refresh(item)

    # 主逻辑完成后才登记后台任务，响应发送后自动执行
    background.add_task(notify_item_done, item.id, item.name, user.email)
    background.add_task(write_audit_log, "item.done", user.id)

    return item
```

关键点：

- **`background: BackgroundTasks` 直接写在签名里**：不需要 `Depends`，FastAPI 会自动注入。
- **`add_task(函数, 位置参数...)`**：参数按位置传，不支持关键字。需要传字典就用位置参数传过去。
- **登记顺序即执行顺序**：多个任务按 `add_task` 的先后串行执行，不会并发。所以慢任务不要堆太多，否则响应后进程还在忙。
- **任务在响应发送后执行**：如果任务里抛异常，客户端已经收到 200，不会感知到。这正是它适合「非关键动作」的原因。
- **`item.status = "done"` 后 `flush`**：ORM 对象改属性即脏数据，flush 会把 UPDATE 发出去，提交仍由 `get_db` 负责。

## 运行效果

```text
$ curl -X POST http://127.0.0.1:8000/items/1/done -H "Authorization: Bearer <token>"
HTTP/1.1 200 OK
{"id":1,"name":"买牛奶","status":"done",...}

# 响应之后，服务端才打印
INFO:app.tasks:notify start item_id=1
INFO:httpx:HTTP Request: POST https://httpbin.org/post "HTTP/1.1 200 OK"
INFO:app.request:POST /items/1/done -> 200 45.2ms

$ # 断网后再次触发，观察重试
WARNING:app.external:post failed attempt=1 url=https://httpbin.org/post error=ConnectError
WARNING:app.external:post failed attempt=2 url=https://httpbin.org/post error=ConnectError
WARNING:app.external:post failed attempt=3 url=https://httpbin.org/post error=ConnectError
ERROR:app.external:post gave up url=https://httpbin.org/post
```

注意主请求依然是 200，45ms 就返回了；通知的成败完全不影响用户。这就是「把非关键路径移出请求链路」的价值。

## 常见坑

**在 async 路由里直接调同步 requests**：整个事件循环被阻塞，并发数瞬间降到 1。要么换 `httpx.AsyncClient`，要么用 `run_in_threadpool` 包一层。

**用 `asyncio.create_task` 代替 BackgroundTasks**：任务对象没有强引用，可能被 GC 提前回收；异常也不会被任何人看到。除非你明确管理了任务集合，否则用框架提供的机制。

**以为 BackgroundTasks 能保证送达**：进程重启、部署滚动更新时正在执行的任务会直接丢失。需要可靠性的场景必须上消息队列，把任务持久化。

**重试没有次数上限或没有退避**：对方已经 503，你还每秒打十次，等于帮它彻底躺平。重试必须有上限、有退避、有可重试状态码白名单。

**在后台任务里改数据库**：请求的会话可能已经关闭，直接用会报 `Session is closed`。后台任务要么自己开一个新会话，要么只做无状态的 IO。

## 课后练习

1. 给 `post_json` 增加随机抖动（`random.uniform(0, 0.5)` 秒），说明它能缓解什么问题。
2. 写一个后台任务，把完成的待办汇总成一行写入 `logs/done.log`，并与 `write_audit_log` 比较同步/异步写法的差异。
3. 把 `httpx.AsyncClient` 提到 lifespan 里全局复用，在关闭时 `await client.aclose()`，并说明这样做省掉了什么开销。

## 下一课预告

通知可以后台做了，但「实时看到别人改了待办」还需要服务端主动推——下一课用 WebSocket 做连接管理、广播与心跳。""",
    },
    {
        "title": "第 11 课：WebSocket 实时通信",
        "summary": "从握手到广播：用 ConnectionManager 管理连接，实现聊天室、心跳保活与断线清理，并说清多进程下的广播难题。",
        "difficulty": 2,
        "tags": ["FastAPI", "WebSocket", "实时通信"],
        "duration_minutes": 32,
        "content": """## 🎯 本课目标

- 说清 WebSocket 与 HTTP 轮询的差异，知道什么场景必须用长连接
- 写一个 `ConnectionManager`，管理连接、广播消息、清理断线
- 用查询参数传 token 完成握手认证，理解为什么 WebSocket 不方便用 Authorization 头
- 实现心跳机制，识别「假在线」的死连接
- 知道多 worker 部署时单机广播为什么会失效，以及正确的解决方向

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| ws.py | ConnectionManager + 聊天室 WebSocket 路由 |
| static/chat.html | 最小可用前端（原生 WebSocket + 心跳） |
| main.py | 注册 ws 路由 |

## 承接上一课

第 10 课完成待办后会推 Webhook；本课把「推」的方向反过来——由服务端主动推给浏览器。第 6 课的 `Item` 表和第 7 课的 token 校验都会复用。

## 📖 概念讲解

### HTTP 轮询与 WebSocket 的差别

| 维度 | 短轮询 | 长轮询 | WebSocket |
| --- | --- | --- | --- |
| 连接 | 每次请求新建 | 挂起到有数据 | 一次握手长期保持 |
| 实时性 | 取决于间隔 | 较好 | 毫秒级 |
| 服务端压力 | 大量空请求 | 连接占用高 | 连接常驻，消息开销极小 |
| 双向通信 | 客户端发起 | 客户端发起 | 双方随时可发 |
| 典型场景 | 配置刷新 | 通知 | 聊天、协同编辑、行情推送 |

一句话：**需要服务端主动、频繁、低延迟地推数据，就用 WebSocket**；只是偶尔查一次状态，普通接口足够。

### 握手阶段仍然是一次 HTTP 请求

WebSocket 建立连接分两步：客户端发一个带 `Upgrade: websocket` 的 HTTP 请求，服务端返回 101 Switching Protocols，之后这条 TCP 连接就变成了双向消息通道。

这带来两个实际影响：

1. 浏览器原生 `WebSocket` 构造函数**不能自定义请求头**，所以 token 只能放在 URL 查询参数或第一个消息里；
2. 中间的反向代理必须显式支持 Upgrade，否则连接会被降级或直接断开。第 15 课的 Nginx 配置里会有对应的两行。

### 连接必须自己管，也必须自己清

HTTP 是无状态的，请求结束就完事；WebSocket 是一条长期存活的连接，服务端要自己维护一份「当前有哪些连接」的清单。清单管理有三个动作：

| 动作 | 时机 | 不做会怎样 |
| --- | --- | --- |
| 加入清单 | `accept()` 之后 | 广播漏掉新用户 |
| 移除清单 | 断开或异常 | 清单越积越大，广播报错 |
| 心跳检测 | 定时 ping | 死连接永远留在清单里 |

「假在线」是 WebSocket 最典型的问题：用户拔网线、笔记本合盖，TCP 连接不会立刻感知，服务端可能几分钟后才发现。所以必须有应用层心跳。

## 🛠 Step 1：ws.py——连接管理器

```python
# ws.py：WebSocket 连接管理与聊天室
import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

logger = logging.getLogger("app.ws")

router = APIRouter()


class ConnectionManager:
    # 管理所有活跃连接，注意它是进程内状态
    def __init__(self) -> None:
        self.active: dict[str, set[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket) -> None:
        # 先 accept 握手，再登记，顺序不能反
        await websocket.accept()
        self.active.setdefault(room, set()).add(websocket)
        logger.info("ws connected room=%s total=%s", room, len(self.active[room]))

    def disconnect(self, room: str, websocket: WebSocket) -> None:
        # 用 discard 而不是 remove，重复清理不会抛 KeyError
        self.active.get(room, set()).discard(websocket)
        if not self.active.get(room):
            self.active.pop(room, None)

    async def broadcast(self, room: str, message: dict[str, object]) -> None:
        # 复制一份列表再遍历，避免遍历中被 disconnect 修改
        targets = list(self.active.get(room, set()))
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(message)
            except Exception:
                # 发送失败说明连接已断，收集起来统一清理
                dead.append(ws)
        for ws in dead:
            self.disconnect(room, ws)


manager = ConnectionManager()
```

逐段说明：

- **`dict[str, set[WebSocket]]`**：按房间分组。用 set 而不是 list，同一个连接重复加入不会产生重复消息。
- **先 `accept()` 再登记**：没 accept 就 `send_json` 会抛 `RuntimeError: WebSocket is not connected`。
- **`discard` 而非 `remove`**：断开可能被触发两次（客户端关闭 + 服务端异常），用 discard 天然幂等。
- **广播前复制列表**：`list(...)` 生成快照，遍历期间即使有连接被移除也不会抛「集合大小改变」。
- **发送失败即视为死亡**：`send_json` 抛异常说明底层已断，立刻从清单剔除，避免每次都白试一遍。
- **`manager` 是模块级单例**：进程内共享。这一点在第 5 个常见坑里会展开，它是本课最重要的限制。

## 🛠 Step 2：认证握手与消息循环

```python
@router.websocket("/ws/chat/{room}")
async def chat_room(websocket: WebSocket, room: str, token: str = "") -> None:
    # 1. 握手阶段校验 token：浏览器无法自定义请求头，只能走查询参数
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("missing sub")
    except Exception:
        # 校验失败必须关闭连接，不能在未认证状态下 accept
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. 登记连接
    await manager.connect(room, websocket)
    await manager.broadcast(room, {"type": "system", "text": "用户 " + str(user_id) + " 加入"})

    try:
        while True:
            # 3. 等待客户端消息；心跳用 ping/pong 文本协议
            text = await websocket.receive_text()
            if text == "ping":
                await websocket.send_json({"type": "pong"})
                continue
            if len(text) > 500:
                await websocket.send_json({"type": "error", "text": "消息过长"})
                continue
            await manager.broadcast(room, {"type": "chat", "user": user_id, "text": text})
    except WebSocketDisconnect:
        # 4. 客户端主动断开，走正常清理路径
        manager.disconnect(room, websocket)
        await manager.broadcast(room, {"type": "system", "text": "用户 " + str(user_id) + " 离开"})
    except Exception:
        # 5. 其他异常也要清理，否则连接会泄漏在清单里
        logger.exception("ws error room=%s", room)
        manager.disconnect(room, websocket)
```

关键点：

- **token 放查询参数**：`wss://host/ws/chat/1?token=xxx`。注意 URL 可能被日志、代理记录，生产环境应使用短时效的专用 ws token，而不是长期 access token。
- **未认证直接 `close`**：绝不能先 accept 再检查，否则客户端会以为自己连上了。`WS_1008` 表示策略违规，前端可以据此提示重新登录。
- **`while True` + `receive_text`**：这是 WebSocket 的标准读取循环，直到客户端断开抛 `WebSocketDisconnect` 才退出。
- **心跳用文本 `ping` / `pong`**：比协议层 ping 帧更简单，浏览器原生 API 无法发 ping 帧，只能靠文本消息模拟。
- **两层异常都要清理**：`WebSocketDisconnect` 是正常断开，其他异常是意外断开，两者都必须调 `disconnect`，否则清单里会留下死连接。

## 🛠 Step 3：最小前端与心跳

```html
<!-- static/chat.html：原生 WebSocket 客户端 -->
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <title>待办聊天室</title>
</head>
<body>
  <input id="token" placeholder="粘贴 access_token" size="60">
  <button onclick="connect()">连接</button>
  <ul id="log"></ul>

  <script>
    let ws = null;
    let timer = null;

    function connect() {
      const token = document.getElementById("token").value;
      ws = new WebSocket("ws://127.0.0.1:8000/ws/chat/1?token=" + token);

      ws.onopen = () => {
        // 每 25 秒发一次心跳，服务端回 pong
        timer = setInterval(() => ws.send("ping"), 25000);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "pong") return;
        const li = document.createElement("li");
        li.textContent = data.type + ": " + (data.text || "");
        document.getElementById("log").appendChild(li);
      };

      ws.onclose = () => {
        clearInterval(timer);
        console.log("连接已关闭，可以在这里做重连");
      };
    }
  </script>
</body>
</html>
```

前端的三个要点：

- **`onclose` 里清定时器**：不清会持续往已关闭的连接 send，控制台不断报错。
- **重连要加退避**：直接 `setInterval(connect, 1000)` 会在服务端故障时形成重连风暴，应改成指数退避。
- **消息统一用 JSON**：字符串协议一旦要加字段就得改解析逻辑，JSON 从第一天就用，扩展成本最低。

## 运行效果

```text
$ pip install websockets
$ uvicorn main:app --reload

# 用 wscat 模拟两个客户端
$ wscat -c "ws://127.0.0.1:8000/ws/chat/1?token=<有效token>"
Connected (press CTRL+C to quit)
< {"type":"system","text":"用户 1 加入"}
> 大家好
< {"type":"chat","user":"1","text":"大家好"}
> ping
< {"type":"pong"}

# 服务端日志
INFO:app.ws:ws connected room=1 total=1
INFO:app.ws:ws connected room=1 total=2

# token 错误时
$ wscat -c "ws://127.0.0.1:8000/ws/chat/1?token=bad"
Received close code 1008, reason: 
```

## 常见坑

**忘记 `await websocket.accept()`**：客户端一直停在 CONNECTING，服务端日志也看不出错。记住 accept 是握手的最后一步，必须先做。

**多 worker 下广播只到一部分人**：`manager` 是进程内变量，4 个 worker 就是 4 份清单，A 进程的消息推不到 B 进程的连接。解决办法是用 Redis Pub/Sub 做跨进程广播，把 worker 当成订阅者。

**用 `Depends(get_db)` 拿会话却跨消息复用**：WebSocket 连接可能存活几小时，而请求级会话在握手完成后就该关闭。长时间持有连接会让连接池耗尽，正确做法是每条消息单独开会话并尽快关闭。

**没有心跳就判断在线**：TCP 半开连接可以存活很久，清单里全是「假人」。心跳间隔建议 20~30 秒，连续两次没回应就主动关闭。

**在 WebSocket 里发送超大消息或无限缓冲**：单条消息应设上限（如 500 字符或 64KB），服务端还要限制每个房间的连接数，否则一个恶意客户端就能耗尽内存。

## 课后练习

1. 给 `ConnectionManager` 增加 `broadcast_all` 方法，向所有房间广播系统公告，并在管理接口里触发。
2. 把聊天消息落库：新建 `messages` 表，每条消息写入数据库，新用户进入时返回最近 20 条历史。
3. 用 Redis 的发布订阅改造广播逻辑（可以用 `redis.asyncio`），说明改造后 4 个 worker 为什么能收到同一条消息。

## 下一课预告

连接、任务、异常都有了，但线上出问题时你只能靠日志复盘——下一课把日志、请求 ID 与异常兜底做成一套真正可用的可观测体系。""",
    },
    {
        "title": "第 12 课：日志与错误处理实战",
        "summary": "用 dictConfig 配好分级日志，用 contextvars 串起请求 ID，做全局异常兜底并确保堆栈只进日志不进响应。",
        "difficulty": 3,
        "tags": ["FastAPI", "日志", "错误处理"],
        "duration_minutes": 32,
        "content": """## 🎯 本课目标

- 用 `logging.config.dictConfig` 统一配置控制台与文件日志，区分开发与生产格式
- 用 `contextvars` 给每条日志自动带上请求 ID，实现一次请求全链路追踪
- 写一个真正兜底的异常处理器：客户端只看到统一文案，服务端拿到完整堆栈
- 把常见数据库异常（唯一约束、外键失败）翻译成合适的 HTTP 状态码
- 建立「哪些能记、哪些绝不能记」的日志红线

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| logging_config.py | 日志配置与请求 ID 过滤器 |
| context.py | 请求上下文变量（request_id、user_id） |
| main.py | 注册全局异常处理器，启用日志配置 |

## 承接上一课

第 11 课的 WebSocket 日志已经在用 `logging.getLogger("app.ws")`，本课把 `app.*` 这组 logger 的输出格式、落盘与请求 ID 全部统一起来，之前所有 `logger.info` 立刻获得追踪能力。

## 📖 概念讲解

### print 与 logging 的差距

| 能力 | print | logging |
| --- | --- | --- |
| 级别过滤 | 无 | DEBUG/INFO/WARNING/ERROR |
| 输出目标 | 只能 stdout | 控制台、文件、Syslog、远端 |
| 格式统一 | 每次手写 | Formatter 集中配置 |
| 上下文 | 无 | 可注入请求 ID、用户 ID |
| 性能 | 同步阻塞 | 可按级别关闭，支持队列 |

线上排障靠的是「能不能在几万行日志里定位到那一次请求」。print 做不到，因为它没有级别、没有时间戳、没有上下文。

### 日志级别怎么用

| 级别 | 什么时候用 | 例子 |
| --- | --- | --- |
| DEBUG | 开发期细节 | SQL 参数、缓存命中情况 |
| INFO | 正常业务节点 | 用户登录、创建待办 |
| WARNING | 可恢复的异常 | 外部接口重试、慢请求 |
| ERROR | 需要人介入 | 未捕获异常、数据库连接失败 |
| CRITICAL | 服务不可用 | 配置缺失、密钥加载失败 |

一个实用原则：**INFO 级别应该能还原业务主线，但不应该刷屏**。每个请求打一条汇总日志足够，不要在循环里打 INFO。

### 请求 ID 是怎么串起来的

一次请求会经过中间件、依赖、路由、crud 好几层，每层都可能打日志。如果每条日志都手动传 request_id，代码会脏得没法看。

`contextvars` 解决的正是这个问题：它是「协程安全的全局变量」，同一个请求链路里的所有代码都能读到同一个值，不同请求之间互不干扰。配合 `logging.Filter`，每条日志自动附加该值。

## 🛠 Step 1：context.py 与 logging_config.py

```python
# context.py：请求级上下文
from contextvars import ContextVar

# 默认值 None，表示不在请求上下文中（如启动脚本、后台任务）
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")
```

```python
# logging_config.py：一次配置，全局生效
import logging
import logging.config

from context import request_id_var, user_id_var


class RequestContextFilter(logging.Filter):
    # 把 contextvars 里的值塞进 LogRecord，供 Formatter 使用
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        return True


LOG_FORMAT = "%(asctime)s %(levelname)s [%(request_id)s] [%(user_id)s] %(name)s: %(message)s"


def setup_logging(debug: bool = False) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,  # 不要关掉 uvicorn、sqlalchemy 的 logger
            "filters": {
                "request_context": {"()": RequestContextFilter},
            },
            "formatters": {
                "default": {"format": LOG_FORMAT},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["request_context"],
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/app.log",
                    "maxBytes": 10 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "formatter": "default",
                    "filters": ["request_context"],
                },
            },
            "root": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["console", "file"],
            },
            "loggers": {
                "uvicorn.access": {"level": "WARNING", "propagate": False},
                "sqlalchemy.engine": {"level": "WARNING"},
            },
        }
    )
```

逐段说明：

- **`ContextVar` 的 `default="-"`**：不在请求里时也能取到值，日志格式不会因为缺字段报错。
- **`disable_existing_loggers: False`**：默认是 True，会把已经创建的 logger 全部禁用，导致 uvicorn 的启动日志凭空消失。这是最常见的配置事故。
- **`filters` 挂在 handler 上**：过滤器作用于「这条日志要不要输出、输出时带什么字段」，挂在 handler 上比拼在 formatter 里简单可靠。
- **`RotatingFileHandler`**：按大小滚动，`maxBytes` 10MB、保留 5 份，避免磁盘被日志写满。容器部署通常不打文件，交给 stdout 收集。
- **`uvicorn.access` 降到 WARNING**：我们自己的中间件已经记录了请求日志，再留一份 access 日志会重复。
- **`sqlalchemy.engine` 降到 WARNING**：第 6 课开的 `echo=True` 在学习期有用，生产必须关掉。

## 🛠 Step 2：中间件写入上下文

```python
# middleware.py：改进后的请求日志中间件
import logging
import time
import uuid

from fastapi import FastAPI, Request

from context import request_id_var, user_id_var

logger = logging.getLogger("app.request")


def register_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        # set 之后返回的 token 用于恢复，防止上下文泄漏到其他请求
        id_token = request_id_var.set(request_id)
        user_token = user_id_var.set("-")
        start = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            logger.info(
                "%s %s -> %s %.1fms",
                request.method,
                request.url.path,
                response.status_code,
                (time.perf_counter() - start) * 1000,
            )
            return response
        finally:
            # 无论成功失败都复位，避免污染后续请求
            request_id_var.reset(id_token)
            user_id_var.reset(user_token)
```

关键点：

- **访问日志只能写在 `call_next` 之后**：状态码在响应对象上，`finally` 里拿不到 `response`，所以 `finally` 只负责复位上下文，不打日志。
- **`set()` 返回 token**：必须用 `reset(token)` 恢复，而不是再 `set("-")`。前者是栈式恢复，后者在嵌套调用时会丢掉外层的值。
- **`finally` 复位是硬要求**：中间件复用同一个事件循环，上下文如果不清理，可能串到下一个请求上——这种 bug 极难复现。
- **`user_id_var` 在依赖里设置**：`get_current_user` 里加一行 `user_id_var.set(str(user.id))`，之后的日志就自动带上用户 id，不用层层传参。

## 🛠 Step 3：全局异常兜底与数据库异常翻译

```python
# main.py：异常处理器
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger("app.error")


@app.exception_handler(SQLAlchemyError)
async def handle_db_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    # 1. 数据库异常分类处理：唯一约束冲突是可预期的业务错误
    if isinstance(exc, IntegrityError):
        logger.warning("integrity error path=%s", request.url.path)
        return JSONResponse(
            status_code=409,
            content={"code": "CONFLICT", "message": "数据冲突，请检查是否重复提交"},
        )

    # 2. 其余数据库错误记 ERROR，但不把 SQL 返回给客户端
    logger.exception("database error path=%s", request.url.path)
    return JSONResponse(
        status_code=503,
        content={"code": "DB_UNAVAILABLE", "message": "服务暂时不可用，请稍后重试"},
    )


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    # 3. 真正兜底：任何未捕获异常都在这里收口
    logger.exception(
        "unhandled error method=%s path=%s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "服务器内部错误"},
    )
```

要点：

- **`IntegrityError` 单独处理**：邮箱重复、外键失效都会走到这里，返回 409 比 500 更准确，前端也能给出「该邮箱已注册」的提示。
- **`logger.exception` 只在 except 或处理器内调用**：它依赖当前异常上下文，在别处调用只会打印 `NoneType: None`。
- **响应体只有 code 和 message**：绝不包含 `str(exc)`。SQLAlchemy 的异常字符串里有表名、列名、SQL 片段，有的还含参数值。
- **503 而不是 500**：数据库不可用是「暂时性」故障，503 能告诉网关和客户端「可以稍后重试」，语义更准。
- **`@app.exception_handler(Exception)` 不能完全替代中间件兜底**：它捕获路由链路内的异常，但中间件自身抛出的异常不经过它。两层都保留，覆盖率才够。

## 运行效果

```text
$ uvicorn main:app
2026-11-12 10:58:01,204 INFO [-] [-] app.request: GET /items -> 200 12.4ms
2026-11-12 10:58:09,881 INFO [7f2a9c] [-] app.db: query items skip=0 limit=10
2026-11-12 10:58:15,332 WARNING [7f2a9c] [3] app.error: integrity error path=/auth/register
2026-11-12 10:58:15,333 INFO [7f2a9c] [3] app.request: POST /auth/register -> 409 8.1ms

# 客户端看到的
$ curl -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" -d '{"email":"tom@example.com","password":"secret123"}'
{"code":"CONFLICT","message":"数据冲突，请检查是否重复提交"}

# 服务端日志里的完整堆栈
ERROR [7f2a9c] [3] app.error: unhandled error method=GET path=/items/boom
Traceback (most recent call last):
  File "main.py", line 88, in read_items
    ...
RuntimeError: boom
```

对比客户端响应与服务端日志：客户端只拿到一句话，服务端有请求 ID、用户 ID 和完整堆栈。用 `grep 7f2a9c logs/app.log` 就能还原这次请求的全过程。

## 常见坑

**`disable_existing_loggers` 用了默认 True**：uvicorn、sqlalchemy 的 logger 全被禁用，启动日志消失，排查问题时以为服务没起来。

**日志里用 f-string 或手动拼接**：`logger.info("user " + str(uid))` 会先做字符串拼接，即使这条日志最终被级别过滤掉，拼接待价也已经付出。正确写法是 `logger.info("user %s", uid)`，由 logging 延迟格式化。

**把密码、token、完整手机号写进日志**：日志往往比数据库更容易被导出、被第三方收集。登录日志只记用户 id 与结果，绝不记密码；必要时对邮箱做掩码。

**以为 `@app.exception_handler(Exception)` 能兜住所有错误**：语法错误、中间件异常、启动失败都不经过它。生产环境还要靠进程管理器重启与健康检查。

**在处理器里再查数据库**：异常往往就是数据库引发的，处理器里再查一次会二次失败，且掩盖原始错误。处理器只做序列化与记录。

## 课后练习

1. 在 `get_current_user` 里设置 `user_id_var`，验证登录后的日志自动带上用户 id；未登录接口仍显示 `-`。
2. 加一个慢请求告警：耗时超过 500ms 用 WARNING 级别记录，并把阈值做成环境变量。
3. 故意让一个接口抛 `ZeroDivisionError`，确认客户端只收到统一 JSON、服务端日志有堆栈，且 `X-Request-ID` 能在日志中检索到。

## 下一课预告

代码越来越复杂，靠手点接口验证已经不现实——下一课用 pytest 把注册、登录、增删改查全部自动化，让每次改动都有回归保护。""",
    },
    {
        "title": "第 13 课：用 pytest 测试接口",
        "summary": "用 pytest-asyncio 与 httpx 搭建异步测试：内存数据库、依赖覆盖、注册登录与 CRUD 全流程断言。",
        "difficulty": 3,
        "tags": ["FastAPI", "pytest", "接口测试"],
        "duration_minutes": 33,
        "content": """## 🎯 本课目标

- 搭好 pytest + pytest-asyncio + httpx 的异步测试环境，理解 `asyncio_mode = auto` 的作用
- 用 `StaticPool` 建一个测试专用的内存数据库，每个用例前后自动建表与清空
- 用 `dependency_overrides` 把生产数据库换成测试库，业务代码一行不改
- 写出注册、登录、创建、越权访问四类断言，覆盖正常路径与失败路径
- 养成「先写断言，再改代码」的回归习惯

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| pytest.ini | pytest 配置（异步模式、测试目录） |
| tests/conftest.py | 测试引擎、数据库覆盖、AsyncClient fixture |
| tests/test_auth.py | 注册与登录用例 |
| tests/test_items.py | 增删查与数据隔离用例 |

## 承接上一课

第 12 课把日志与异常都收口了，这让测试更好写——断言状态码和响应体即可，不用关心服务端打印了什么。测试直接复用 `main.py` 的 `app` 与 `get_db`。

## 📖 概念讲解

### 为什么用 httpx 而不是 TestClient

| 维度 | `TestClient` | `httpx.AsyncClient` + `ASGITransport` |
| --- | --- | --- |
| 执行方式 | 同步，内部起线程跑事件循环 | 原生异步 |
| 与 async 依赖配合 | 可用但绕 | 直接可用 |
| 复用性 | 仅测试 | 也能写脚本压测 |
| 生命周期事件 | 会触发 | 默认不触发，需手动管理 |

本课程的路由、依赖、数据库全是异步的，用 `AsyncClient` 最自然，也不会出现「测试里同步、生产里异步」两套心智模型。

### 测试数据库为什么必须用 StaticPool

SQLite 的 `:memory:` 数据库**属于单个连接**：连接断开，数据就没了。而 SQLAlchemy 默认用连接池，每个会话可能拿到不同连接，于是出现「建表成功但查不到表」的诡异现象。

`poolclass=StaticPool` 强制所有会话共用同一个连接，内存库才不会丢。这是异步 SQLite 测试最关键的配置，没有之一。

### 依赖覆盖的原理

`app.dependency_overrides[get_db] = override_get_db` 是一张替换表：FastAPI 解析依赖时先查这张表，命中就用替换函数。它有三个好处：

- 业务代码零改动，不需要 `if testing` 分支；
- 只替换数据库，认证、路由、中间件仍然走真实逻辑；
- 用完 `clear()` 就恢复，不会污染其他用例。

## 🛠 Step 1：安装依赖与 pytest 配置

```bash
# 在项目虚拟环境里安装测试依赖
pip install pytest pytest-asyncio httpx

# 更新依赖清单，第 15 课构建镜像时会一起装上
pip freeze > requirements.txt
```

```ini
# pytest.ini：放在项目根目录
[pytest]
asyncio_mode = auto
testpaths = tests
addopts = -q
filterwarnings =
    ignore::DeprecationWarning
```

配置说明：

- **`asyncio_mode = auto`**：所有 `async def test_*` 自动被当作异步用例，不用每个都写 `@pytest.mark.asyncio`。漏写装饰器是新手最常遇到的「测试被跳过」原因。
- **`testpaths = tests`**：限定只收集 `tests/` 目录，避免把脚本目录里的函数也当成用例。
- **`addopts = -q`**：默认精简输出；需要详细时命令行加 `-v` 覆盖。
- **`filterwarnings`**：第三方库的弃用警告不阻断测试，但不要全局屏蔽 `Warning`，否则会漏掉自己的问题。

## 🛠 Step 2：conftest.py——测试地基

```python
# tests/conftest.py：所有用例共享的 fixture
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import models  # noqa: F401  建表前必须让模型完成注册
from database import Base, get_db
from main import app

# 1. 内存数据库 + StaticPool：所有会话共用同一条连接
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSession = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database() -> AsyncGenerator[None, None]:
    # 2. 每个用例前建表、后删表，保证用例之间完全隔离
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    # 3. 与生产 get_db 行为一致：成功提交，失败回滚
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # 4. 用 ASGITransport 直接调用 app，不经过真实网络
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    # 5. 清理覆盖，避免影响下一个测试文件
    app.dependency_overrides.clear()
```

逐段说明：

- **`import models`**：和主应用一样，模型不导入就不会进 `Base.metadata`，`create_all` 会建出空库。
- **`autouse=True`**：不需要在每个用例里声明，自动生效。代价是每个用例都建删表，速度略慢，但隔离性最好。
- **`drop_all` 而不是删数据**：删表能彻底清掉自增 id 与索引状态，避免「第一个用例 id 是 1，第二个变成 2」这类顺序依赖。
- **`connect_args`**：`check_same_thread` 是 SQLite 的线程检查开关，测试环境关闭它避免多线程报错，生产 SQLite 同样建议关。
- **`base_url="http://test"`**：httpx 要求有 host，随便给一个即可，请求不会真的发出去。
- **`dependency_overrides.clear()`**：写在 `yield` 之后，即使用例失败也会执行。

**注意**：`ASGITransport` 默认不执行 lifespan，所以 `main.py` 里的 `create_all` 不会跑，也不会碰真实数据库文件。这正是我们想要的行为。

## 🛠 Step 3：写用例——认证与数据隔离

```python
# tests/test_auth.py
from httpx import AsyncClient


async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"email": "tom@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "tom@example.com"
    # 响应里绝不能出现密码相关字段
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_duplicate(client: AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": "secret123"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "secret123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "wrong-pass"},
    )
    assert response.status_code == 401
```

```python
# tests/test_items.py
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def headers(client: AsyncClient) -> dict[str, str]:
    # 注册并登录，返回可直接用于请求的认证头
    await client.post(
        "/auth/register",
        json={"email": "amy@example.com", "password": "secret123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "amy@example.com", "password": "secret123"},
    )
    return {"Authorization": "Bearer " + response.json()["access_token"]}


async def test_create_item_requires_login(client: AsyncClient) -> None:
    response = await client.post("/items", json={"name": "未登录创建"})
    assert response.status_code == 401


async def test_create_and_list(client: AsyncClient, headers: dict[str, str]) -> None:
    created = await client.post(
        "/items", json={"name": "买牛奶", "price": 12.5}, headers=headers
    )
    assert created.status_code == 201
    item_id = created.json()["id"]

    listed = await client.get("/items/mine", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [item_id]


async def test_cannot_delete_others_item(
    client: AsyncClient, headers: dict[str, str]
) -> None:
    created = await client.post("/items", json={"name": "私人物品"}, headers=headers)
    item_id = created.json()["id"]

    # 换一个用户登录，尝试删除别人的数据
    await client.post(
        "/auth/register",
        json={"email": "eve@example.com", "password": "secret123"},
    )
    login = await client.post(
        "/auth/login",
        data={"username": "eve@example.com", "password": "secret123"},
    )
    other = {"Authorization": "Bearer " + login.json()["access_token"]}

    response = await client.delete("/items/" + str(item_id), headers=other)
    # 第 8 课的设计：越权访问返回 404，不暴露数据是否存在
    assert response.status_code == 404
```

用例设计的三个原则：

- **每条断言只验证一件事**：状态码、字段、数量分开写，失败时一眼看出哪里不对。
- **失败路径和成功路径一样重要**：401、404、409 才是线上真正会出问题的地方。
- **不要依赖执行顺序**：每个用例自己造数据，`autouse` 的建删表保证互不影响。

## 运行效果

```text
$ pytest -v
tests/test_auth.py::test_register_success PASSED          [ 14%]
tests/test_auth.py::test_register_duplicate PASSED        [ 28%]
tests/test_auth.py::test_login_wrong_password PASSED      [ 42%]
tests/test_items.py::test_create_item_requires_login PASSED [ 57%]
tests/test_items.py::test_create_and_list PASSED          [ 71%]
tests/test_items.py::test_cannot_delete_others_item PASSED [ 85%]

==================== 6 passed in 2.31s ====================

$ pytest tests/test_items.py::test_create_and_list -v
tests/test_items.py::test_create_and_list PASSED          [100%]
```

2 秒跑完 6 个用例，覆盖了注册、登录、鉴权、创建、查询与越权。以后每次改代码，跑一遍就知道有没有破坏既有行为。

## 常见坑

**内存库不加 StaticPool**：建表在连接 A，查询走连接 B，报 `no such table: items`。看到这个错先检查连接池配置。

**异步 fixture 用了 `@pytest.fixture`**：返回的是协程对象，用例拿到后所有操作都失效。异步 fixture 必须用 `@pytest_asyncio.fixture`。

**`dependency_overrides` 没清理**：一个文件覆盖了数据库，另一个文件以为在用生产库，实际还在测试库上，测试之间互相污染。用 `try/finally` 或 fixture 的清理段解决。

**测试直接连开发数据库**：跑一次测试把开发数据删了。测试环境必须是独立的内存库或独立文件库，绝不共用。

**只测成功路径**：6 个用例全绿，上线后 401 和 409 全错。失败路径才是接口契约的真正边界。

## 课后练习

1. 补一个用例：创建两个同名待办，验证业务层是否允许重名；如果允许，说明为什么不该在数据库层加唯一约束。
2. 用 `app.dependency_overrides[get_now]` 固定时间，测试「创建时间」字段是否落在预期区间。
3. 给 `tests/` 加一个 `pytest.mark.slow` 的慢用例（比如上传 2MB 文件），并在 `pytest.ini` 里配置默认跳过它。

## 下一课预告

测试有了，但项目还是一堆平铺的文件——下一课做工程化重构：APIRouter 拆分、pydantic-settings 管理配置、Alembic 接管数据库迁移。""",
    },
    {
        "title": "第 14 课：项目分层与工程化",
        "summary": "把平铺文件重构成标准包结构：APIRouter 聚合路由、pydantic-settings 管理配置、Alembic 接管表结构迁移。",
        "difficulty": 3,
        "tags": ["FastAPI", "工程化", "Alembic"],
        "duration_minutes": 35,
        "content": """## 🎯 本课目标

- 把 13 课积累的十几个文件重构成 `app/` 包，按 core / db / models / schemas / api / services 分层
- 用 `APIRouter` 把接口按业务拆分，再由一个总路由聚合，`main.py` 只负责装配
- 用 `pydantic-settings` 管理配置，环境变量优先、`.env` 兜底、类型自动转换
- 用 Alembic 的 async 模板接管建表与改表，理解 `revision --autogenerate` 的边界
- 说清分层的收益与代价，避免为了分层而分层

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| app/ 包 | 标准分层目录（见下方结构图） |
| app/core/config.py | Settings 与 get_settings |
| app/api/router.py | 总路由聚合 |
| alembic/env.py | 异步迁移环境 |
| alembic.ini | 迁移配置 |

## 承接上一课

第 13 课的测试依赖 `main.app` 与 `database.get_db`；重构后它们的导入路径变成 `app.main:app` 与 `app.db.session.get_db`，测试只需改 import 与 `base_url`，断言逻辑完全不变。

## 📖 概念讲解

### 为什么要在第 14 课才重构

前 13 课把所有文件平铺在根目录，是为了让每一课的代码都能「复制即运行」，不被包路径干扰。当文件涨到十几个、接口涨到二十几个时，平铺的代价开始显现：

| 问题 | 平铺 | 分层 |
| --- | --- | --- |
| 找代码 | 全靠文件名记忆 | 按职责定位 |
| 循环导入 | 到处都是 | 依赖方向单一 |
| 多人协作 | 抢同一个 main.py | 各改各的 router |
| 复用 | 复制粘贴 | service 层共享 |

**分层不是目的，降低修改成本才是。** 如果项目只有 5 个接口，平铺反而更快；一旦接口上两位数、开始多人协作，就该拆。

### 依赖方向必须单向

```
api（路由） → services（业务） → db / models（数据）
      ↓                ↓
   schemas          core（配置、安全、日志）
```

规则只有一条：**下层不能 import 上层**。models 不认识 FastAPI，services 不认识 Request，这样业务逻辑才能脱离 Web 框架单独测试。第 4 课把业务异常和 HTTPException 分开，就是为了守住这条线。

### 配置为什么要用 pydantic-settings

| 做法 | 问题 |
| --- | --- |
| 模块级常量 | 改配置要改代码，无法区分环境 |
| `os.environ.get` 散落各处 | 类型全是 str，布尔值 `"false"` 是真值 |
| pydantic-settings | 集中声明、自动转类型、缺关键配置启动即失败 |

`BaseSettings` 的读取优先级是：**环境变量 > `.env` 文件 > 类默认值**。这让同一份镜像可以在开发、测试、生产用不同配置运行，正是第 15 课容器化的前提。

## 🛠 Step 1：目标目录结构与配置

```text
fastapi_todo/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 只做装配：中间件、路由、生命周期
│   ├── core/
│   │   ├── config.py           # Settings
│   │   ├── security.py         # 密码与 JWT
│   │   └── logging_config.py   # 日志配置
│   ├── db/
│   │   ├── base.py             # Base
│   │   └── session.py          # engine / SessionLocal / get_db
│   ├── models/
│   │   ├── __init__.py         # 导入所有模型，供 Alembic 发现
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── item.py
│   ├── api/
│   │   ├── deps.py             # DbDep / CurrentUser
│   │   ├── router.py           # 总路由
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── items.py
│   │       ├── files.py
│   │       └── ws.py
│   └── services/
│       ├── external.py
│       └── tasks.py
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

```python
# app/core/config.py：全项目唯一的配置来源
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FastAPI Todo API"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./todo.db"
    secret_key: str = "dev-only-change-me"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:5173"]
    max_upload_size: int = 2 * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    # 只实例化一次，全项目共享；测试里可以 clear 缓存后替换
    return Settings()
```

关键点：

- **字段名自动映射环境变量**：`database_url` 对应 `DATABASE_URL`，大小写不敏感。容器里直接用 `-e DATABASE_URL=...` 注入。
- **类型自动转换**：`debug: bool` 收到字符串 `"false"` 会转成 `False`，不会出现「写了 false 却是真值」的坑。
- **`list[str]` 要从环境变量传 JSON**：`CORS_ORIGINS='["https://a.com","https://b.com"]'`。pydantic-settings 会按 JSON 解析，逗号分隔的写法在 v2 里不再支持。
- **`secret_key` 有默认值只是为了让本地能跑**：生产环境必须注入真实值，且不能有默认值兜底。可以改成 `secret_key: str`，缺失时启动直接报错——让配置错误在启动阶段暴露，比运行到登录接口才炸好得多。
- **`@lru_cache`**：避免每次依赖都重新解析 .env。测试里想换配置，先 `get_settings.cache_clear()`。

## 🛠 Step 2：路由拆分与总装

```python
# app/api/routers/items.py：只关心 items 的 HTTP 语义
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, DbDep
from app.schemas.item import ItemCreate, ItemRead
from app.services import item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/mine", response_model=list[ItemRead])
async def list_my_items(user: CurrentUser, db: DbDep):
    return await item_service.list_by_owner(db, user.id)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ItemRead)
async def create_item(payload: ItemCreate, user: CurrentUser, db: DbDep):
    return await item_service.create(db, payload, owner_id=user.id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, user: CurrentUser, db: DbDep) -> None:
    item = await item_service.get(db, item_id)
    if item is None or (item.owner_id != user.id and not user.is_admin):
        raise HTTPException(status_code=404, detail="Item not found")
    await item_service.remove(db, item)
```

```python
# app/api/router.py：总路由，只做 include
from fastapi import APIRouter

from app.api.routers import auth, files, items, ws

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(items.router)
api_router.include_router(files.router)
api_router.include_router(ws.router)
```

```python
# app/main.py：装配层，读完就知道这个应用由什么组成
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.db.base import Base
from app.db.session import engine
from app.middleware import register_middlewares
from app.services.tasks import close_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # 仅本地开发用
    yield
    await close_http_client()
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.debug)
    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_middlewares(application)
    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()
```

关键点：

- **每个 router 自带 `prefix` 和 `tags`**：items 的 prefix 是 `/items`，总路由再统一加上 `/api/v1`，最终路径是 `/api/v1/items`。版本前缀集中在一处，将来升 v2 只改一行。
- **`create_app()` 工厂函数**：测试里可以创建多个独立实例；某些部署工具（如 Gunicorn 的 app factory 模式）也依赖它。
- **`main.py` 不再出现任何业务逻辑**：它只回答「加载什么配置、挂什么中间件、包含哪些路由」。
- **`ws.router` 没有 prefix**：因为第 11 课的路径已经写成 `/ws/chat/{room}`，prefix 留空避免变成 `/ws/ws/chat`。拆路由时一定要核对最终路径。
- **`include_router` 的顺序**：路由按注册顺序匹配，固定路径（`/items/mine`）必须写在参数路径（`/items/{item_id}`）之前，第 2 课的规则在拆分后依然生效。

## 🛠 Step 3：Alembic 接管表结构

```bash
# 1. 安装并用 async 模板初始化（会生成 alembic/ 与 alembic.ini）
pip install alembic
alembic init -t async alembic

# 2. 修改 alembic.ini 里的脚本位置（可选，默认即可）
# 3. 编辑 alembic/env.py（见下方代码）
# 4. 生成第一个迁移，检查无误后应用
alembic revision --autogenerate -m "init tables"
alembic upgrade head
```

```python
# alembic/env.py：只保留关键部分
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.models  # noqa: F401  必须导入，autogenerate 才能看到表
from app.core.config import get_settings
from app.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 用运行时配置覆盖 ini 里的 URL，保证环境变量生效
config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # 字段类型变化也能检测到
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


run_migrations_online()
```

关键点：

- **`import app.models`**：`autogenerate` 靠 `Base.metadata` 对比数据库，模型没导入就生成一个空迁移。这个坑每年都有人踩。
- **`set_main_option` 覆盖 URL**：`alembic.ini` 里的 URL 是静态的，用代码覆盖才能读到环境变量，避免生产迁移连错库。
- **`compare_type=True`**：默认不检测类型变更，`String(50)` 改 `String(100)` 会被漏掉。打开它更安全。
- **`poolclass=NullPool`**：迁移是一次性任务，不需要连接池，用完即断。
- **`create_all` 与 Alembic 不能并存**：一旦用了迁移，`lifespan` 里的 `create_all` 就该删掉，否则新库会被「先建表、再迁移」搞出冲突。

## 运行效果

```text
$ alembic revision --autogenerate -m "init tables"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'items'
Generating /Users/me/fastapi_todo/alembic/versions/8f2c1d4a9b77_init_tables.py ... done

$ alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade  -> 8f2c1d4a9b77, init tables

$ uvicorn app.main:app --reload
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.

$ curl http://127.0.0.1:8000/api/v1/items/mine
{"detail":"Not authenticated"}
```

注意启动命令变成了 `app.main:app`——包路径重构后，模块名是点分形式，这是最容易忘的一处改动。

## 常见坑

**循环导入**：`db/session.py` 导入 `core/config.py`，`models` 导入 `db/base.py`，`api` 又导入 `models`，一旦某个文件反向导入就死锁。原则：严格单向，公共类型放 `schemas` 或 `core`。

**`__init__.py` 缺失**：Python 3.11 有隐式命名空间包，某些情况下能跑，但 `alembic`、`pytest` 的导入会莫名其妙失败。每个包目录都放一个空 `__init__.py`，省心。

**配置缓存导致测试串环境**：`@lru_cache` 让 `get_settings()` 只读一次，测试里改环境变量无效。记得在 fixture 里 `get_settings.cache_clear()`。

**`alembic.ini` 里还写着同步 URL**：`sqlite:///` 配 async 引擎会报驱动错误。要么用代码覆盖，要么改成 `sqlite+aiosqlite:///`。

**为了分层而分层**：三个接口拆出 service、repository、manager 四层，改一个字段要动六个文件。分层的粒度应该跟着复杂度走，而不是跟着教程走。

## 课后练习

1. 把第 11 课的 `ws.py` 移进 `app/api/routers/`，修正所有 import，并验证 `/ws/chat/1` 仍然可连。
2. 给 `Settings` 增加 `log_level: str = "INFO"`，用它控制第 12 课的日志级别，并用环境变量验证生效。
3. 改一个字段长度（如 `name` 从 50 改到 80），用 `revision --autogenerate` 生成迁移，打开生成的文件检查 SQLite 下的实际写法，再 `upgrade head`。

## 下一课预告

结构、配置、迁移都就位了，最后一课把它装进 Docker、挂上 Nginx、配好健康检查与限流，并完成整个待办事项 API 的验收。""",
    },
    {
        "title": "第 15 课：部署上线与毕业项目",
        "summary": "用 Docker 打包、Nginx 反代、多 worker 启动，配齐健康检查、限流与环境变量，并验收完整的待办事项 API。",
        "difficulty": 3,
        "tags": ["FastAPI", "Docker", "部署上线"],
        "duration_minutes": 35,
        "content": """## 🎯 本课目标

- 写出多阶段构建的 Dockerfile，镜像里不带编译工具与测试依赖
- 用 docker compose 串起 api 与 nginx，理解数据卷为什么必须挂
- 配好 Nginx 反向代理，包括 WebSocket 的 Upgrade 头与上传大小限制
- 说清生产启动参数：worker 数量、`--proxy-headers`、健康检查、限流
- 用前 14 课的所有知识完成「待办事项 API」的最终验收

## 📦 本课产出

| 文件 | 作用 |
| --- | --- |
| Dockerfile | 多阶段构建的生产镜像 |
| .dockerignore | 排除 .venv、tests、*.db |
| docker-compose.yml | api + nginx 编排 |
| nginx.conf | 反向代理、WebSocket、限流 |
| README.md（可选） | 启动方式与接口清单 |

## 承接上一课

第 14 课已经得到 `app.main:app` 这个标准入口，配置全部走环境变量；本课不再改业务代码，只补齐运行环境与上线检查项。

## 📖 概念讲解

### 开发启动与生产启动的差别

| 项 | 开发 | 生产 |
| --- | --- | --- |
| 命令 | `uvicorn app.main:app --reload` | `uvicorn app.main:app --workers 4` |
| 热重载 | 开 | 必须关 |
| 进程数 | 1 | `2 × CPU + 1` 左右 |
| 日志 | 控制台彩色 | stdout，由平台收集 |
| 代理头 | 不需要 | `--proxy-headers --forwarded-allow-ips=*` |
| 数据库 | SQLite 文件 | 独立数据库服务 + 迁移先行 |

**worker 不是越多越好**：每个 worker 是独立进程，各自持有连接池与内存。4 个 worker 意味着 4 份连接池、4 份 WebSocket 连接清单（第 11 课的广播问题就在这里暴露）。先按 CPU 核数配，再压测调整。

### 多阶段构建省掉了什么

| 阶段 | 内容 | 最终镜像是否保留 |
| --- | --- | --- |
| builder | 编译器、pip 缓存、wheel | 否 |
| runtime | 只装好的依赖 + 代码 | 是 |

好处是镜像体积能小一半以上，攻击面也更小——生产镜像里没有 gcc，就算被打进容器也少一堆工具可用。

### 上线清单

| 类别 | 检查项 |
| --- | --- |
| 配置 | 所有密钥走环境变量；`DEBUG=false`；CORS 白名单 |
| 数据 | 迁移在启动前跑完；数据目录挂卷；有备份 |
| 可用性 | `/health` 健康检查；worker 数合理；重启策略 |
| 安全 | 非 root 用户运行；上传大小限制；登录接口限流；HTTPS |
| 可观测 | 日志到 stdout；请求 ID；错误率与延迟监控 |

这张表建议直接抄进项目的 README，每次上线逐条打勾。

## 🛠 Step 1：Dockerfile 与 .dockerignore

```dockerfile
# 阶段一：安装依赖
FROM python:3.11-slim AS builder

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
# 装到独立前缀，方便整目录复制
RUN pip install --prefix=/install -r requirements.txt


# 阶段二：运行时
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local
COPY ./app ./app

# 非 root 用户运行，数据目录给它写权限
RUN useradd -m appuser
RUN mkdir -p /data && chown -R appuser:appuser /data
USER appuser

EXPOSE 8000

# 健康检查直接用 Python 标准库，镜像里不必装 curl
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*"]
```

```text
# .dockerignore：把不该进镜像的东西挡在门外
.venv/
__pycache__/
*.pyc
*.db
.env
.git/
tests/
logs/
uploads/
```

逐段说明：

- **两阶段**：builder 里装依赖，runtime 只复制 `/install`，pip 缓存与编译器都不进最终镜像。
- **`PYTHONUNBUFFERED=1`**：Python 默认缓冲 stdout，容器里会导致日志延迟甚至丢失。这一行必须加。
- **`--prefix=/install`**：把包装到一个独立目录，复制时不会带上 builder 里的其他文件。
- **`useradd` + `USER appuser`**：容器内不以 root 运行。很多安全基线（如 Kubernetes 的 restricted 策略）强制要求这一点。
- **`HEALTHCHECK`**：每 30 秒请求一次 `/health`，连续 3 次失败标记为 unhealthy，编排系统据此重启或摘流量。
- **`--proxy-headers`**：让 FastAPI 信任 `X-Forwarded-For` / `X-Forwarded-Proto`，否则日志里的客户端 IP 全是 Nginx 的地址，生成的跳转链接也会变成 http。
- **JSON 数组形式的 CMD**：直接 exec 启动，uvicorn 是 PID 1，能正确收到 SIGTERM 做优雅关闭。shell 形式会多一层 sh，信号传不进去。

## 🛠 Step 2：compose 与 Nginx

```yaml
# docker-compose.yml
services:
  api:
    build: .
    environment:
      DATABASE_URL: sqlite+aiosqlite:////data/todo.db
      SECRET_KEY: ${SECRET_KEY:?请在 .env 中设置 SECRET_KEY}
      DEBUG: "false"
      CORS_ORIGINS: '["https://todo.example.com"]'
    volumes:
      # 具名卷挂到 /data，容器重建数据不丢
      - todo-data:/data
    expose:
      - "8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3

  nginx:
    image: nginx:1.27-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  todo-data:
```

```nginx
# nginx.conf
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

server {
    listen 80;
    client_max_body_size 5m;

    # 基础安全响应头，避免浏览器做 MIME 嗅探与页面嵌套
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;

    # JSON 响应体通常能压缩掉一半以上，省带宽也省时间
    gzip on;
    gzip_types application/json;

    location /api/v1/auth/login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
    }

    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location = /health {
        proxy_pass http://api:8000/health;
        access_log off;
    }
}
```

关键点：

- **`DATABASE_URL` 有四个斜杠**：`sqlite+aiosqlite:////data/todo.db` 表示绝对路径 `/data/todo.db`；三个斜杠是相对路径，在容器里会写到工作目录，容器一重建就没了。
- **具名卷 `todo-data`**：SQLite 的数据文件必须放在卷上。生产环境更推荐独立数据库服务，SQLite 适合单机小流量。
- **`${SECRET_KEY:?...}`**：变量缺失时 compose 直接报错退出，避免用默认密钥上线。这比在代码里兜底安全得多。
- **`client_max_body_size 5m`**：比应用层 2MB 限制略大，让应用返回结构化的 413，而不是 Nginx 直接返回 HTML 错误页。
- **WebSocket 的两行配置**：`Upgrade` 与 `Connection` 头必须转发，否则握手失败，前端只会看到连接被关闭；`proxy_read_timeout 3600s` 防止空闲连接被 Nginx 60 秒掐断。
- **登录限流 `5r/m`**：Nginx 层挡住暴力破解，应用层还可以用 `slowapi` 做更细的策略。限流要放在最外层，别让请求打到数据库才拒绝。
- **`add_header` 与 `gzip`**：安全头是低成本高收益的一项；`gzip_types` 只列 JSON，避免对图片、压缩包重复压缩反而更慢。

## 🛠 Step 3：启动、验收与毕业项目

```bash
# 1. 准备环境变量
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env

# 2. 构建并启动
docker compose up -d --build

# 3. 查看状态与日志
docker compose ps
docker compose logs -f api

# 4. 验证
curl http://127.0.0.1/health
curl -X POST http://127.0.0.1/api/v1/auth/register -H "Content-Type: application/json" -d '{"email":"tom@example.com","password":"secret123"}'
curl -X POST http://127.0.0.1/api/v1/auth/login -d "username=tom@example.com&password=secret123"

# 5. 关闭
docker compose down
```

毕业项目的完整目录（15 课的全部产物）：

```text
fastapi_todo/
├── app/
│   ├── main.py                 # 装配：配置、中间件、路由、生命周期
│   ├── core/                   # config / security / logging
│   ├── db/                     # base / session（async engine + get_db）
│   ├── models/                 # user / item
│   ├── schemas/                # auth / item（Pydantic v2）
│   ├── api/                    # deps / router / routers（auth, items, files, ws）
│   └── services/               # item_service / external / tasks
├── alembic/                    # 迁移脚本
├── tests/                      # pytest 用例
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
└── .env                        # 不入库
```

验收清单（全部满足才算毕业）：

1. 未登录访问 `/api/v1/items/mine` 返回 401，登录后返回自己的数据；
2. 用户 A 无法删除用户 B 的待办（返回 404），管理员可以；
3. 创建待办时 `name` 为空返回 422，且错误结构统一；
4. 上传 3MB 文件返回 413，上传 mp4 返回 415；
5. 完成待办后服务端日志出现后台通知记录，主请求耗时不受影响；
6. 打开两个浏览器窗口连同一个房间，消息实时互相可见，关掉一个后另一个收到离开提示；
7. `pytest` 全绿，`alembic upgrade head` 在空库上可重复执行；
8. `docker compose up` 后 `/health` 返回 200，容器以非 root 用户运行。

## 运行效果

```text
$ docker compose up -d --build
[+] Building 18.4s (12/12) FINISHED
 => [builder 3/4] RUN pip install --prefix=/install -r requirements.txt      12.1s
 => [stage-1 2/5] COPY --from=builder /install /usr/local                      0.6s
 => exporting to image                                                         0.4s
[+] Running 3/3
 ✔ Network fastapi_todo_default      Created
 ✔ Container fastapi_todo-api-1      Started
 ✔ Container fastapi_todo-nginx-1    Started

$ docker compose ps
NAME                    STATUS                    PORTS
fastapi_todo-api-1      Up 12 seconds (healthy)   8000/tcp
fastapi_todo-nginx-1    Up 12 seconds             0.0.0.0:80->80/tcp

$ curl -i http://127.0.0.1/health
HTTP/1.1 200 OK
content-type: application/json
{"status":"ok"}

$ curl -i -X POST http://127.0.0.1/api/v1/auth/login -d "username=tom@example.com&password=wrong"
HTTP/1.1 401 Unauthorized
{"detail":"邮箱或密码错误"}

# 第 6 次快速重试会被 Nginx 拦下
HTTP/1.1 503 Service Temporarily Unavailable
<html><head><title>503 Service Temporarily Unavailable</title></head></html>
```

状态列出现 `(healthy)` 说明 HEALTHCHECK 通过；登录限流生效说明 Nginx 配置已加载。至此，一个从零写起、带鉴权、数据库、上传、实时通信、测试与部署的后端项目真正跑起来了。

## 常见坑

**镜像里留着 `--reload`**：热重载进程常驻，CPU 和内存翻倍，文件监听在某些文件系统上还会失效。生产 CMD 必须去掉它。

**只开 1 个 worker**：单进程只能用一个 CPU 核，并发上不去。4 核机器建议 4~9 个 worker，再根据压测结果调整。

**不带 `.dockerignore`**：`.venv`、`.git`、`*.db` 全被塞进构建上下文，镜像几百 MB，还可能把本地数据库和密钥打进镜像层。

**SQLite 文件写在容器内**：容器一重建数据全没。必须挂卷，或者换成独立数据库服务。这也是为什么生产环境更推荐 MySQL / PostgreSQL。

**Nginx 没转发 WebSocket 头**：握手返回 400 或连接立刻断开，前端控制台只显示「连接已关闭」，没有任何有用信息。`Upgrade` 与 `Connection` 两行一个都不能少。

**密钥写进 Dockerfile 或 compose 文件**：镜像层和 Git 历史都会永久保留。用 `.env`（加入 .gitignore）或平台的 secret 管理，构建时不要 COPY 密钥文件。

## 课后练习

1. 把 `--workers 4` 改成 `--workers 1`，用 `hey -n 200 -c 20 http://127.0.0.1/health` 各压一次，比较 QPS 与延迟，解释差异来源。
2. 给 Nginx 加一个全局限流（如 `20r/s`），验证正常业务不受影响、突发流量被平滑处理。
3. 把数据库从 SQLite 换成 MySQL：改 `DATABASE_URL`、在 compose 里加 mysql 服务、装 aiomysql、跑 `alembic upgrade head`，记录遇到的问题与解决办法。

## 下一课预告

这是本模块的最后一课。接下来可以沿着三条路继续深入：把项目部署到云服务器并配 HTTPS、接入 Redis 做缓存与跨进程广播，或者补一个前端把整套接口真正用起来。""",
    },
]
