"""Python 爬虫模块种子数据（HTTP 基础、解析、反爬、框架、存储与合规）。"""

MODULE = {
    "code": "python_crawler",
    "name": "Python 爬虫",
    "description": "从 HTTP 原理到 Scrapy 实战：requests、解析、反爬应对、数据存储与爬虫合规，15 篇带你写出专业爬虫。",
    "icon": "🕷️",
    "color": "#38bdf8",
    "sort_order": 7,
    "parent_code": "python",
}

ARTICLES = [
    {
        "title": "爬虫是什么：HTTP 请求-响应原理与浏览器开发者工具",
        "summary": "网页是怎么来到你屏幕上的？搞懂请求-响应模型和 F12 开发者工具，爬虫就成功了一半。",
        "difficulty": 1,
        "tags": ["HTTP", "开发者工具", "入门"],
        "duration_minutes": 12,
        "content": """## 爬虫到底在做什么

爬虫的本质一句话：**模拟浏览器向服务器发请求，把返回的数据留下来**。浏览器展示页面 = 发 HTTP 请求 → 拿到响应 → 渲染；爬虫只是把"浏览器"换成 Python 脚本，跳过渲染，直接取数据。

## HTTP 请求-响应的一生

```http
GET /search?q=python HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
```

响应由状态码、响应头、响应体组成。爬虫最关心状态码：**200 成功、301/302 重定向、403 被拦截、404 不存在、429 请求太频繁、5xx 服务器出错**；响应体（HTML 或 JSON）才是要解析的内容。

## 浏览器开发者工具：第一件武器

按 F12，三个面板最常用：

| 面板 | 用途 |
| --- | --- |
| Network | 看浏览器发出的每个请求，找数据在哪个接口 |
| Elements | 查看渲染后的 HTML 结构，写解析规则 |
| Preview | 预览接口返回的 JSON，判断好不好拿 |

**要点**：写任何爬虫前，先在 Network 面板找到"数据到底在哪个请求里"，再动手写代码，能少走 80% 的弯路。

## 注意：源码 ≠ Elements

右键"查看网页源代码"是服务器返回的原始 HTML；Elements 是 JS 执行后的最终结构。源码里没有的数据，多半是 JS 动态加载的，那是后面的课题。""",
    },
    {
        "title": "requests 入门：GET/POST、headers、超时与重试",
        "summary": "人生苦短，我用 requests。10 分钟学会发请求、带参数、设超时，写出第一个能跑的爬虫。",
        "difficulty": 1,
        "tags": ["requests", "GET/POST", "入门"],
        "duration_minutes": 12,
        "content": """## 第一个请求

```python
import requests

resp = requests.get("https://httpbin.org/get")
print(resp.status_code)  # 200
```

`resp.json()` 解析 JSON；`resp.content` 拿二进制。

## GET 与 POST

```python
requests.get("https://httpbin.org/get", params={"q": "python", "page": 1})
requests.post("https://httpbin.org/post", data={"user": "tom", "pwd": "123"})
```

口诀：**GET 用 params 传参；POST 表单用 data，JSON 用 json**。

## headers 伪装

默认 User-Agent 是 `python-requests/xxx`，一眼被识破。**第一课：带上浏览器请求头**。

```python
headers = {"User-Agent": "Mozilla/5.0"}
requests.get(url, headers=headers, timeout=5)
```

## 超时与重试：保命符

不设 timeout 会卡死；不重试就丢数据。

```python
from requests.adapters import HTTPAdapter, Retry

s = requests.Session()
s.mount("http://", HTTPAdapter(max_retries=Retry(
    total=3, backoff_factor=1, status_forcelist=[500, 502])))
resp = s.get(url, timeout=(3, 10))
```

**注意**：`timeout=(3, 10)` 是连接 3 秒、读 10 秒；永远不要不设超时。""",
    },
    {
        "title": "HTML 结构速成：标签、层级与 DOM 树",
        "summary": "不会前端也能学爬虫：20 分钟看懂标签、属性与父子层级，为网页解析打好坚实地基。",
        "difficulty": 1,
        "tags": ["HTML", "DOM", "基础"],
        "duration_minutes": 10,
        "content": """## HTML 是一棵树

浏览器把 HTML 解析成 **DOM 树**：`html` 是根，往下逐层分叉。爬虫解析页面，本质就是"在这棵树上找节点"。

```html
<div class="list">
  <a href="/1">第一篇</a>
  <a href="/2">第二篇</a>
</div>
```

这里 `div` 是两个 `a` 的**父节点**，两个 `a` 互为**兄弟节点**。

## 标签、属性、文本三要素

| 要素 | 例子 | 爬虫用途 |
| --- | --- | --- |
| 标签名 | `a`、`div` | 缩小查找范围 |
| 属性 | `class="title"`、`href` | 精确定位、提取链接 |
| 文本 | `第一篇` | 往往就是目标数据 |

**要点**：`id` 全页唯一，`class` 可重复。写解析规则优先用 `id`，其次用语义化的 `class`。

## 常见标签速查

- `a`：链接，`href` 就是地址；
- `img`：图片，`src` 是地址，**注意相对路径要补全**；
- `table / tr / td`：表格数据爬取的主战场；
- `ul / li`：新闻列表、商品列表的常用容器；
- `div / span`：无语义容器，靠 class 区分用途。

## 结构改版的影响

页面改版（如 `class="title"` 改名）解析就会失效。**规则要写得稳**：优先选语义化、不易变的属性，别依赖过深的层级路径。

**注意**：Elements 面板是 JS 渲染后的结果，写规则前先确认源代码里真有这些节点。""",
    },
    {
        "title": "BeautifulSoup 解析：find/find_all 与对象模型",
        "summary": "把 HTML 变成可查询的 Python 对象。find 与 find_all 用熟了，静态页面解析就通了。",
        "difficulty": 1,
        "tags": ["BeautifulSoup", "解析", "入门"],
        "duration_minutes": 12,
        "content": """## 基本用法

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
soup.a["href"]   # 取属性
soup.a.text      # 取文本
```

解析后是四类对象：`soup`（文档）、`Tag`（标签）、`NavigableString`（文本）、`Comment`（注释）。日常 90% 的操作都在 `Tag` 上。

## find 与 find_all：核心中的核心

```python
soup.find_all("a")                    # 所有匹配，返回列表
soup.find_all("div", class_="item")   # class 是保留字，写 class_
soup.find("a", href="/1")             # 只取第一个，找不到返回 None
```

**要点**：`find_all` 返回 `list`，哪怕只匹配到一个；`find` 返回单个对象。忘记这点，遍历时必踩坑。

## 节点导航

```python
soup.div.parent             # 父节点
soup.a.find_next("a")       # 下一个匹配的 a
soup.a.find_parent("div")   # 往上找最近的 div
```

## 完整小例子

```python
for item in soup.find_all("div", class_="item"):
    a = item.find("a")
    if a:
        print(a.text.strip(), a["href"])
```

先缩进查找，再取文本和属性，这是最常见的解析模板。

**注意**：`find` 可能为 `None`，链式取值前必须判空，否则一条脏数据就让整个爬虫崩溃。""",
    },
    {
        "title": "CSS 选择器与 XPath：精准定位元素",
        "summary": "find 不够用时，选择器才是利器。一篇打通 CSS 选择器与 XPath 两大定位体系。",
        "difficulty": 1,
        "tags": ["CSS选择器", "XPath", "解析"],
        "duration_minutes": 14,
        "content": """## CSS 选择器：select 方法

```python
soup.select("div.item > a.title")     # class 组合 + 直接子级
soup.select("#main li:nth-child(2)")  # id + 第 2 个 li
soup.select_one("a[href^='https']")   # 取单个
```

| 符号 | 含义 |
| --- | --- |
| `.xxx` / `#xxx` | class / id |
| 空格 / `>` | 任意层级后代 / 直接子级 |
| `[]` | 属性匹配 |

**要点**：`select` 永远返回列表，取单个用 `select_one`。

## XPath：另一种定位语言

用路径思维描述位置，功能更强（能按文本内容匹配），推荐用 lxml 执行：

```python
from lxml import etree

tree = etree.HTML(html)
tree.xpath('//div[@class="item"]/a/text()')    # 取文本
tree.xpath('//a/@href')                        # 取属性
tree.xpath('//a[contains(text(), "python")]')  # 按文本模糊匹配
```

语法：`//` 任意层级、`/` 下一级、`@class` 选属性、`[@class="item"]` 是谓词过滤。

## 两套体系怎么选

简单页面、class 明确时用 CSS 选择器，直观好写；要按文本内容定位、或用 Scrapy 框架时选 XPath——CSS 做不到按内容匹配，而 Scrapy 原生支持 XPath。

**注意**：F12 复制的路径常带大量 `nth-child`，又长又脆，页面一改就断。**学会手写简短选择器**，比复制粘贴重要得多。""",
    },
    {
        "title": "lxml 与解析性能：为什么大项目都用它",
        "summary": "同样解析 10 万个页面，为什么别人只要 30 秒？聊聊解析器性能差距与容错能力。",
        "difficulty": 1,
        "tags": ["lxml", "性能", "解析"],
        "duration_minutes": 10,
        "content": """## 解析器性能对比

BeautifulSoup 只是"壳"，真正干活的是底层解析器：

| 解析器 | 写法 | 速度 |
| --- | --- | --- |
| html.parser | 内置免安装 | 慢 |
| lxml | `BeautifulSoup(html, "lxml")` | 快一个数量级 |
| html5lib | 兼容浏览器行为 | 最慢 |

```bash
pip install lxml
```

实测 1MB 页面：html.parser 约 200ms，lxml 约 20ms。**百万级页面面前，这就是天与地的差距。**

## 直接用 etree

大项目常跳过 BeautifulSoup，直接用 lxml，API 同样简洁：

```python
from lxml import etree

tree = etree.HTML(html)
tree.xpath('//h2[@class="title"]/text()')
tree.xpath('//a/@href')
```

`etree.HTML()` 自带容错：标签没闭合、缺 head，都会尽力补全后解析。

## 三个加分理由

1. **内存占用低**：C 层实现，同样数据明显更省；
2. **XPath 全支持**：`contains`、`position()` 随便用；
3. **生态兼容**：Scrapy 底层就是 lxml，学它为框架铺路。

## 何时不用纠结

**要点**：只爬几百个页面、跑一次就丢，任何解析器都够，别提前优化；长期采集任务从第一天就用 lxml，成本几乎为零。

**注意**：严重不规范的 HTML，lxml 结果可能与浏览器不一致，此时用 html5lib 兜底核对。""",
    },
    {
        "title": "反爬第一课：User-Agent、Cookie、Referer 与请求头伪装",
        "summary": "403 了怎么办？看懂服务器如何识别爬虫，学会用请求头把自己伪装成正常浏览器用户。",
        "difficulty": 2,
        "tags": ["反爬", "请求头", "User-Agent"],
        "duration_minutes": 14,
        "content": """## 服务器怎么认出你是爬虫

最基础的反爬先看请求头，四个"验人"依据：

| 请求头 | 作用 | 缺失/异常的后果 |
| --- | --- | --- |
| User-Agent | 客户端身份 | 默认 python-requests 直接被拦 |
| Referer | 来源页面 | 图片防盗链返回 403 |
| Cookie | 会话凭证 | 可能拿不到数据 |

## 完整伪装一个浏览器请求

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh) "
                  "AppleWebKit/537.36 Chrome/120.0",
    "Referer": "https://example.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
requests.get(url, headers=headers, timeout=10)
```

**要点**：先在 Network 面板照抄真实请求的头，比凭感觉编靠谱。

## User-Agent 池：随机轮换

总用一个 UA 也容易被统计，准备列表随机取用：

```python
import random

UA_POOL = ["Mozilla/5.0 (Windows NT 10.0) Chrome/120.0",
           "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)"]
headers["User-Agent"] = random.choice(UA_POOL)
```

也可以用 `fake-useragent` 库自动生成。

## 防盗链与提醒

爬图片莫名 403，多半 Referer 校验，带上所在页面地址。

**注意**：请求头伪装只解决"身份识别"一层；遇到 Cookie 加密、JS 签名要靠抓包分析或浏览器自动化，别死磕。收到 429 说明频率过高，**先降速**。""",
    },
    {
        "title": "动态渲染页面：Selenium 与浏览器自动化",
        "summary": "源码里找不到数据？页面是 JS 画的。用 Selenium 驱动真实浏览器，让数据自己渲染出来。",
        "difficulty": 2,
        "tags": ["Selenium", "动态页面", "自动化"],
        "duration_minutes": 15,
        "content": """## 为什么源码里没数据

有些页面由 JS 画进 DOM：源代码里空空如也，Elements 里啥都有。requests 拿不到，要用真浏览器执行 JS。

## 最小示例

```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://example.com/list")
driver.implicitly_wait(5)  # 等 JS 渲染
html = driver.page_source  # 渲染后 HTML
```

`page_source` 可交给 BeautifulSoup，解析知识全复用。

## 常用元素操作

```python
from selenium.webdriver.common.by import By

driver.find_element(By.ID, "kw").send_keys("python")
driver.find_element(By.ID, "su").click()
items = driver.find_elements(By.CLASS_NAME, "item")
```

## 显式等待：比 sleep 靠谱

**要点**：别 sleep 硬等，条件满足就继续：

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "item")))
```

瀑布流用 `execute_script` 滚动加载；用完 `quit()` 清理进程。

**注意**：Selenium 慢且重，能直接请求接口就别跑浏览器。""",
    },
    {
        "title": "Playwright：新一代爬虫自动化利器",
        "summary": "比 Selenium 更快更稳的自动化方案：自动等待、多浏览器、无头模式一步到位。",
        "difficulty": 2,
        "tags": ["Playwright", "自动化", "异步"],
        "duration_minutes": 14,
        "content": """## Playwright 是什么

微软开源的浏览器自动化库，可视为"Selenium 现代替代品"：多浏览器内核、自带自动等待、可拦截请求。

```bash
pip install playwright
playwright install chromium
```

## 同步用法：五行起步

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # 无头模式
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
```

**要点**：操作自带自动等待，`click()` 等元素可点才执行，多数场景不用手写等待，这是比 Selenium 省心的核心。

## 常用操作速查

```python
page.fill("#kw", "python")                  # 输入
page.click("text=搜索")                      # 按文本点击
page.goto(url, wait_until="networkidle")    # 等网络空闲
```

## 拦截请求：降维打击

能监听页面发出的网络请求，数据不用解析 DOM，拦接口即可：

```python
def on_response(resp):
    if "/api/list" in resp.url:
        print(resp.json())

page.on("response", on_response)
```

**注意**：存量项目 Selenium 够用；要拦接口或跑异步的新项目，优先 Playwright。""",
    },
    {
        "title": "抓包分析 Ajax 接口：直接请求 JSON 数据的高效姿势",
        "summary": "与其解析 HTML，不如直捣接口。学会在 Network 里挖出 Ajax 接口，效率提升十倍。",
        "difficulty": 2,
        "tags": ["Ajax", "抓包", "JSON"],
        "duration_minutes": 15,
        "content": """## 为什么要找接口

页面展示的数据多来自返回 JSON 的 Ajax 请求。直接请求接口，**跳过 HTML 解析、跳过浏览器渲染**，速度和稳定性双升级。

## 三步定位数据接口

1. F12 → Network → 切到 **Fetch/XHR** 过滤器；
2. 刷新页面或点"加载更多"，观察新出现的请求；
3. 逐个看 Preview，找到含目标数据的那一条。

**要点**：接口名常含 `list`、`query`、`api`；分页时对比两页请求的差异，翻页参数一目了然。请求要素重点看：URL 参数（page、size）、请求方法（POST 的参数在请求体）、关键请求头（Cookie、token）、签名字段（sign、timestamp 多由 JS 计算，右键 Copy as cURL 可完整还原）。

## 用 requests 复现

```python
data = requests.get(
    "https://example.com/api/list",
    params={"page": 1, "size": 20},
    headers={"User-Agent": "Mozilla/5.0",
             "Referer": "https://example.com/"},
    timeout=10,
).json()

for item in data["data"]["list"]:
    print(item["title"], item["url"])
```

先在浏览器确认 JSON 的层级结构，再写取值路径，别靠猜。

## 签名参数与健壮性

参数带 `sign`、去掉就 403，说明是前端 JS 算的：入门阶段先观察变化规律（有的只是时间戳），或用浏览器自动化拦截响应。

**注意**：接口会随版本变动，取值用 `data.get("data")` 判空，接口一变不至于整个崩掉。""",
    },
    {
        "title": "requests.Session：登录态保持与 Cookie 管理",
        "summary": "登录后才能看的数据怎么爬？Session 自动管 Cookie，一次登录全程可用。",
        "difficulty": 2,
        "tags": ["Session", "Cookie", "登录态"],
        "duration_minutes": 12,
        "content": """## 为什么需要 Session

普通 `requests.get` 每次都是"新面孔"，服务器不记得你。`requests.Session` **自动保存并携带服务器下发的 Cookie**，像浏览器一样保持登录态；还复用底层连接，批量请求更快。

```python
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0"})

s.post("https://example.com/login",
       data={"user": "tom", "pwd": "123"})
s.get("https://example.com/profile")   # 自动带上 Cookie
```

## 三种登录姿势

| 姿势 | 适用场景 | 做法 |
| --- | --- | --- |
| 表单 POST | 老式登录，无加密 | 直接 POST 账号密码 |
| 带验证码 | 简单图形码 | 下载图片人工识别或 OCR |
| 导出 Cookie | 扫码、短信等复杂登录 | 复制浏览器 Cookie 注入 |

**要点**：工程里第三种最常用——登录环节交给人工或浏览器自动化，爬虫只负责带着现成 Cookie 采集。

## 手动注入 Cookie

```python
for kv in "token=abc123; uid=42".split(";"):
    name, _, value = kv.strip().partition("=")
    s.cookies.set(name, value)
```

请求头、代理也在 Session 上配置一次，全部请求生效，比每次传参干净。

## 失效检测与安全

Cookie 有有效期：检测到响应被重定向到登录页，就重新登录再继续。

**注意**：账号密码、Cookie 绝不硬编码进代码或提交仓库，用环境变量或配置文件管理。""",
    },
    {
        "title": "并发提速：线程池、协程 aiohttp 与限速设计",
        "summary": "单线程爬一晚上？用线程池和协程把采集速度提上去，再用限速设计守住礼貌与安全底线。",
        "difficulty": 2,
        "tags": ["并发", "aiohttp", "限速"],
        "duration_minutes": 16,
        "content": """## 爬虫的时间都花在哪

一次请求 90% 时间在**等网络响应**，CPU 闲置。与其排队等 100 个页面，不如同时发 10 个请求。

## 线程池：最简单的提速

```python
from concurrent.futures import ThreadPoolExecutor

def fetch(url):
    return requests.get(url, timeout=10).status_code

with ThreadPoolExecutor(max_workers=8) as pool:
    pool.map(fetch, urls)
```

`max_workers` 建议 5~20，**不是越大越快**，过高会触发限流甚至封 IP。

## 协程：高并发的正解

协程单线程切换，轻松撑起海量并发；用信号量限并发：

```python
import asyncio, aiohttp

sem = asyncio.Semaphore(10)   # 最多同时 10 个请求

async def fetch(session, url):
    async with sem:
        async with session.get(url) as r:
            return await r.text()

async def main():
    async with aiohttp.ClientSession() as s:
        await asyncio.gather(*(fetch(s, u) for u in urls))

asyncio.run(main())
```

## 限速：并发之外的第二道闸

并发管"同时在跑的数量"，限速管"每秒发几个"：

```python
time.sleep(random.uniform(0.5, 1.5))
```

**要点**：适度并发 + 随机延迟 + 失败退避。**注意**：提速以对方承受为前提，打挂小站等来的就是封禁与追责。""",
    },
    {
        "title": "Scrapy 框架：架构、Spider 与 Pipeline 实战",
        "summary": "告别手搓爬虫：用 Scrapy 的调度、去重、管道体系，把采集工程化地组织起来。",
        "difficulty": 3,
        "tags": ["Scrapy", "框架", "Pipeline"],
        "duration_minutes": 18,
        "content": """## 架构一图流

Scrapy 把请求调度、并发、去重、解析、存储全安排好了。

| 组件 | 职责 |
| --- | --- |
| Scheduler | 请求队列与去重 |
| Downloader | 真正发请求 |
| Spider / Pipeline | 解析规则 / 清洗落库 |

90% 的代码只写在 **Spider 和 Pipeline** 里。

## Spider 实战

建项目后 `scrapy genspider books example.com` 生成骨架：

```python
class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://example.com/list"]

    def parse(self, response):
        for item in response.css("div.item"):
            yield {"title": item.css("a::text").get()}
        if nxt := response.css("a.next::attr(href)").get():
            yield response.follow(nxt, callback=self.parse)
```

**要点**：yield dict 进 Pipeline，yield Request 进调度器，借此翻页。

## Pipeline 与常用配置

settings.py 里开启 `ITEM_PIPELINES`，配 `DOWNLOAD_DELAY = 1` 控速。

**注意**：用 `scrapy shell "URL"` 调试选择器，比反复跑快得多。""",
    },
    {
        "title": "数据落地：CSV、SQLite、MySQL 存储方案对比",
        "summary": "爬下来的数据放哪？CSV、SQLite、MySQL 三种方案各有主场，一篇讲清怎么选怎么写。",
        "difficulty": 3,
        "tags": ["数据存储", "SQLite", "MySQL"],
        "duration_minutes": 14,
        "content": """## 三种方案怎么选

| 方案 | 适合场景 | 优点 | 缺点 |
| --- | --- | --- | --- |
| CSV | 小数据、给 Excel | 零依赖 | 无类型、难更新 |
| SQLite | 单机中小项目 | 单文件、SQL | 并发写入弱 |
| MySQL | 大数据量、共用 | 并发强 | 要装服务、建表 |

**经验**：几千条 CSV；几十万条 SQLite；再大或给后端用 MySQL。

## CSV：标准库开箱即用

```python
import csv

with open("data.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["title", "url"])
    w.writeheader(); w.writerows(items)
```

`utf-8-sig` 防乱码；`newline=""` 防 Windows 空行。

## SQLite：Python 自带的数据库

```python
conn = sqlite3.connect("spider.db")
conn.execute("CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY, title TEXT, url TEXT UNIQUE)")
conn.executemany("INSERT OR IGNORE INTO articles(title,url) VALUES(?,?)", rows)
conn.commit()
```

UNIQUE + INSERT OR IGNORE **天然按链接去重**，断点重爬不怕。

## MySQL 注意事项

pymysql 批量插入用 `executemany`，逐条慢百倍；字符集 `utf8mb4` 防 emoji 失败；密码放配置。

**注意**：落库前先清洗、去重，事后清理成本高得多。""",
    },
    {
        "title": "爬虫的边界：robots.txt、限速礼仪与法律合规",
        "summary": "技术不是免罪金牌。搞懂 robots 协议、限速礼仪与法律红线，做一名守规矩的爬虫工程师。",
        "difficulty": 3,
        "tags": ["合规", "robots.txt", "法律风险"],
        "duration_minutes": 12,
        "content": """## robots.txt：访客须知

域名后加 `/robots.txt` 能看到站长声明的爬取规则：

```text
User-agent: *
Disallow: /private/
Crawl-delay: 5
```

含义：所有爬虫禁止访问 `/private/`，两次请求至少间隔 5 秒。Python 里这样读：

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser("https://example.com/robots.txt")
rp.read()
rp.can_fetch("*", "https://example.com/page/1")
```

**要点**：robots 是行业自律协议而非强制手段，遵守它是职业底线；Scrapy 默认 `ROBOTSTXT_OBEY = True`，不要随手关。

## 限速礼仪

1. **控频率**：单站点每秒 1~2 个请求，大批量安排在凌晨低峰；
2. **表明身份**：User-Agent 里留联系方式，站长遇到问题找你而不是直接封禁；
3. **支持退避**：收到 429/503 主动放慢——服务器在求你减速。

## 法律红线：三个"不要"

| 红线 | 说明 |
| --- | --- |
| 不碰个人隐私 | 身份证、手机号、行踪轨迹受法律严格保护 |
| 不破解技术保护 | 绕过鉴权、破解加密接口可能构成"非法获取" |
| 不转售公开数据 | 数据商用、倒卖，风险陡增 |

国内重点关注《网络安全法》《数据安全法》《个人信息保护法》。

**注意**：尺度口诀——**公开的、非敏感的、低频的、不作恶的**是安全灰度区；一旦涉及登录后数据、个人信息或商业倒卖，先做合规评估。技术会过时，对边界的敬畏不会。""",
    },
]
