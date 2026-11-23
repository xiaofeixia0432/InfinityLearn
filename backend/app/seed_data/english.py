"""英语日常口语模块种子数据（中英混合，场景对话 + 高频句型 + 地道表达）。"""

MODULE = {
    "code": "english",
    "name": "英语日常口语",
    "description": "从点餐问路到职场面试，覆盖 15 个高频生活场景的地道英语口语表达，每课含对话、句型与练习。",
    "icon": "💬",
    "color": "#4f8ef7",
    "sort_order": 1,
}

ARTICLES = [
    {
        "title": "点餐场景：从「我想吃…」到「买单」完整对话",
        "summary": "走进餐厅到结账走人，一条龙掌握点餐高频句型：I'd like / Could I have / Are you ready to order。",
        "difficulty": 1,
        "tags": ["场景对话", "点餐", "高频句型"],
        "duration_minutes": 8,
        "content": """## 场景对话

**Waiter:** Good evening. Are you ready to order?（晚上好，可以点餐了吗？）
**Amy:** Not yet. Could we have a couple more minutes?（还没，能再给我们几分钟吗？）
**Waiter:** Of course.
**Amy:** OK, I'd like the grilled salmon and a garden salad, please.（我要烤三文鱼和一份蔬菜沙拉。）
**Waiter:** How would you like your salmon?（三文鱼要几分熟？）
**Amy:** Medium, please. And could I have the dressing on the side?（五分熟。酱料能放旁边吗？）

## 高频句型

| 中文 | 地道表达 |
| --- | --- |
| 我想要… | I'd like... / I'll have... |
| 能给我…吗 | Could I have..., please? |
| 这个不吃辣 | I can't handle spicy food. / Not spicy, please. |
| 打包 | Could I get this to go? |
| 买单 | Could we get the check, please? |

## 容易踩的坑

- 中国学生常直译 *I want to eat beef*，语法没错但生硬，用 **I'll go with the beef** 更自然。
- "服务员"不要喊 *waiter!*，抬手说 **Excuse me** 就够了。
- AA 制可以说 **Let's split the bill** 或口语化的 *go Dutch*。

## 小练习

把下面三句翻成英文再说出口：1）帮我打包；2）先不点，等一下；3）买单，分开付。明天点餐前默念一遍，直接上场用。""",
    },
    {
        "title": "问路与交通：Excuse me 之后的正确打开方式",
        "summary": "迷路不慌：掌握 how do I get to / Is it far / Which line 三个骨架句，走遍全球都不怕。",
        "difficulty": 1,
        "tags": ["场景对话", "问路", "出行"],
        "duration_minutes": 7,
        "content": """## 场景对话

**You:** Excuse me, how do I get to the National Museum?（请问国家博物馆怎么走？）
**Local:** Take Line 2 and get off at Central Station. It's a five-minute walk from there.（坐 2 号线到中央站，步行五分钟。）
**You:** Is it far from here?（远吗？）
**Local:** Not really. About two stops.
**You:** Thanks! And where's the nearest subway entrance?（谢谢！最近的地铁口在哪？）
**Local:** Go straight and turn left at the lights.（直走过红绿灯左转。）

## 方位词速查

- 直走 **go straight (ahead)**
- 左转/右转 **turn left / right**
- 在拐角 **around the corner**
- 过马路 **cross the street**
- 就在旁边 **It's right next to...**
- 在你右手边 **It's on your right-hand side**

## 常用交通句型

- 去机场要多长时间？**How long does it take to get to the airport?**
- 这趟车到市中心吗？**Does this bus go downtown?**
- 我该在哪站下？**Which stop should I get off at?**
- 票价多少？**What's the fare?**

## 实用提示

问路先说 **Excuse me** 再抛问题，是最基本的礼貌缓冲。听不懂时别硬点头，直接说 **Sorry, could you say that again more slowly?**（能说慢一点吗？），当地人都会放慢速度帮你。""",
    },
    {
        "title": "购物英语：试穿、砍价与退税一步到位",
        "summary": "Do you have this in a larger size? 学会尺码、价格与售后三大购物核心表达。",
        "difficulty": 1,
        "tags": ["场景对话", "购物", "高频句型"],
        "duration_minutes": 9,
        "content": """## 场景对话

**Clerk:** Can I help you find anything?（要找什么吗？）
**You:** I'm looking for a leather jacket. Do you have this in a larger size?（我想买皮夹克，这件有大一号的吗？）
**Clerk:** Sure, here's an L. The fitting room is over there.（有，这是 L 码，试衣间在那边。）
**You:** How does it look?（看起来怎么样？）
**Clerk:** It fits you really well.（非常合身。）
**You:** How much is it? Any discount?（多少钱？有折扣吗？）
**Clerk:** It's $120, and it's already 20% off.（120 美元，已经打了八折。）

## 购物三件套

### 1. 尺码与试穿
- 有别的颜色吗？**Do you have this in other colors?**
- 可以试穿吗？**Can I try this on?**
- 有点紧/松 **It's a bit tight / loose.**

### 2. 价格
- 太贵了 **That's a bit over my budget.**
- 能便宜点吗？**Could you give me a better price?**
- 有活动吗？**Are there any deals going on?**

### 3. 售后
- 能退货吗？**Can I return this if it doesn't fit?**
- 保修多久？**How long is the warranty?**

## 退税小贴士

离开欧盟等购物地时，在机场说 **I'd like to claim the tax refund**（我想办退税），准备好小票 **receipts** 和护照。记住：**duty-free** 是免关税，**tax refund** 是退税，两者不完全一样。""",
    },
    {
        "title": "机场英语全流程：值机、安检到登机口",
        "summary": "过境必备：aisle or window、checked baggage、boarding pass，一次把机场关键对话全部拿下。",
        "difficulty": 2,
        "tags": ["场景对话", "机场", "出行"],
        "duration_minutes": 10,
        "content": """## 值机柜台对话

**Agent:** May I see your passport, please?（请出示护照。）
**You:** Here you go. I'd like a window seat if possible.（给你，可以的话我要靠窗。）
**Agent:** Any bags to check?（有托运行李吗？）
**You:** Just this one suitcase.（就这一个行李箱。）
**Agent:** It's 24 kilos, slightly over the limit. You'll need to pay for extra baggage.（24 公斤，超了一点，需要付超重费。）

## 关键词表

| 场景 | 关键表达 |
| --- | --- |
| 靠窗/靠过道 | window seat / aisle seat |
| 随身行李 | carry-on / hand luggage |
| 托运行李 | checked baggage |
| 登机牌 | boarding pass |
| 登机口 | boarding gate |
| 转机 | transfer / layover |
| 航班延误 | The flight is delayed. |

## 安检与登机

安检员常说 **Take off your belt and put your belongings in the tray.**（腰带解下来，随身物品放进托盘。）听到 **Random check**（随机检查）不用紧张，配合即可。

登机前广播：**Flight CA987 is now boarding at Gate 12.**（CA987 开始在 12 号口登机。）听到自己的航班号就去排队吧。

## 应急表达

- 我找不到我的行李 **I can't find my checked bag.**
- 我误机了，能改签吗？**I missed my flight. Can I rebook?**
- 我转机时间够吗？**Will I make my connection?**""",
    },
    {
        "title": "酒店入住与退房：check-in 到 late checkout",
        "summary": "前台对话模板 + 房间问题投诉句型 + 退房结账细节，住得舒心先说对话。",
        "difficulty": 1,
        "tags": ["场景对话", "酒店", "出行"],
        "duration_minutes": 8,
        "content": """## 入住对话

**Receptionist:** Good afternoon. Do you have a reservation?（下午好，有预订吗？）
**You:** Yes, under the name Wang, W-A-N-G.（有，姓王预订的。）
**Receptionist:** A double room for three nights. Could I have a credit card for the deposit?（双人房三晚，需要信用卡做预授权。）
**You:** Sure. Is breakfast included?（好的，含早餐吗？）
**Receptionist:** Yes, from 7 to 10 on the second floor.（含，二楼 7 点到 10 点。）

## 房间问题投诉

- 空调不制热 **The air conditioning isn't heating.**
- 热水没了 **There's no hot water.**
- 隔音太差 **The room is too noisy. Could I switch to a quieter one?**（能换个安静的房间吗？）
- 这不是我要的房型 **This isn't the room type I booked.**

礼貌投诉公式：**I'm sorry to bother you, but + 问题 + Could you please + 请求？** 先致歉再提诉求，服务人员态度会好很多。

## 退房必备句

- 退房 **I'd like to check out. Room 508.**
- 能延迟退房吗？**Could I have a late checkout?**（很多酒店可延迟到 13:00 或 14:00）
- 能帮我叫出租车吗？**Could you call a taxi for me?**
- 能寄存行李吗？**Could I leave my luggage here for a few hours?**""",
    },
    {
        "title": "面试自我介绍：Tell me about yourself 高分公式",
        "summary": "现在-过去-未来三段式自我介绍，加 8 个加分句型，让面试官记住你。",
        "difficulty": 2,
        "tags": ["面试", "职场", "句型"],
        "duration_minutes": 12,
        "content": """## 自我介绍三段式

### 1. 现在（我是谁）
> I'm a front-end developer with three years of experience in e-commerce projects.（我是有三年电商项目经验的前端工程师。）

### 2. 过去（我做成过什么）
> At my current company, I led the redesign of our checkout flow, which improved conversion by 15%.（我主导过结账流程改版，转化率提升了 15%。）

### 3. 未来（我为什么来）
> I'm excited about this role because it combines my two strengths: coding and user research.（这个岗位正好结合我的两个强项：编程和用户研究。）

总长度控制在 90 秒以内，超过会显得背稿。

## 加分句型

| 表达 | 用途 |
| --- | --- |
| My biggest strength is... | 谈优势 |
| I'm a quick learner. | 强调学习能力 |
| I take ownership of my work. | 强调责任心 |
| I'd love to take on more responsibility. | 表达上进心 |
| Could you tell me more about the team? | 反问环节 |
| What does success look like in this role? | 高级反问 |

## 避雷指南

- 不要背诵简历全文，挑 2~3 个亮点即可。
- 缺点被问到时，用真实但不致命的例子 + 改进行动：*I used to be detail-obsessed, so now I set time boxes for polish work.*
- 结尾别问薪资假期，留给 HR 环节。

## 课后任务

用三段式写出自己的 90 秒自我介绍，对着手机录音，听两遍再改。""",
    },
    {
        "title": "咖啡店点单：size、shot 与定制化表达",
        "summary": "grande 还是 tall？oat milk 加不加？把星巴克式点单黑话一次说明白。",
        "difficulty": 1,
        "tags": ["场景对话", "点餐", "咖啡"],
        "duration_minutes": 6,
        "content": """## 场景对话

**Barista:** What can I get for you today?（今天喝点什么？）
**You:** I'll have a medium iced latte with oat milk, please.（中杯冰拿铁，燕麦奶。）
**Barista:** Any extra shot?（要加浓缩吗？）
**You:** Yes, one extra shot, and less ice, please.（加一份浓缩，冰少点。）
**Barista:** For here or to go?（堂食还是带走？）
**You:** To go. What's your name for the order?（带走。订单写什么名字？）
**You:** Wei, W-E-I.

## 点单黑话速成

- 杯型：**small / medium / large** 通用；连锁店常用 **tall / grande / venti**
- 奶类：**whole milk**（全脂）、**skim milk**（脱脂）、**oat milk**（燕麦奶）、**soy milk**（豆奶）
- 浓度：**extra shot**（加浓缩）、**decaf**（低因）
- 温度：**iced**（冰）、**hot**（热）、**no ice**（去冰）
- 糖度：**half-sweet**（半糖）、**no sugar**（无糖）

## 实用三句

1. **Can I get that decaf?** 能做低因的吗？
2. **What do you recommend?** 有什么推荐？
3. **Is there a size upgrade for free?** 有免费升杯吗？

小贴士：店员问名字是为了写杯贴，直接说名字就行，这不是查户口。""",
    },
    {
        "title": "地道表达辨析：这 10 组词 90% 的人用错",
        "summary": "interesting≠好玩、boring≠无聊透顶…逐一辨析中国人最容易混用的口语词对。",
        "difficulty": 2,
        "tags": ["词汇辨析", "地道表达", "易错词"],
        "duration_minutes": 11,
        "content": """## 1. interesting / fun

**interesting** = 引发兴趣、值得琢磨；**fun** = 好玩、开心。
- 博物馆导览很有料 → *The tour was really interesting.*
- 聚会嗨翻了 → *The party was so much fun.*
说 *You are interesting* 意思是"你这个人挺有意思"，不是夸你好玩，别用错场合。

## 2. boring / bored

**-ing 修饰事物，-ed 描述人的感受。**
- *The lecture was boring.*（讲座无聊）
- *I was bored.*（我感到无聊）
说反了会变成 *I am boring*（我这个人很无趣）——面试自我介绍时的大事故。

## 3. lend / borrow

**lend 借出，borrow 借入。**
- *Could you lend me your charger?*（你能把充电器借我吗？）
- *Can I borrow your charger?*（我能借用你的充电器吗？）

## 4. advice / suggest

**advice** 是名词（不可数）：*Thank you for your advice.* 不说 *an advice*。
**suggest** 是动词：*I suggest taking a break.* 注意后接动名词。

## 5. actually / currently

**actually** = 其实（纠正或强调），**currently** = 目前。问工作状态用 *Where are you working currently?*，用 actually 会很怪。

## 6. hardly / hard

**hardly** = 几乎不；**hard** = 努力地。*I hardly work out* 是"我几乎不锻炼"，*I work out hard* 才是"我疯狂撸铁"，一字之差天壤之别。

## 7~10 快速表

| 词对 | 正确用法 |
| --- | --- |
| recently / lately | 都表"最近"，lately 多与完成时连用 |
| hear / listen to | hear 无意听到，listen to 主动听 |
| trip / travel | trip 可数名词（一次旅行），travel 多作动词 |
| clothes / cloth | clothes 衣服（复数），cloth 布料 |

## 练习方法

每组词对造一句自己的真实生活例句，说出口而不是默写，一周后自然内化。""",
    },
    {
        "title": "电话与预约英语：听不清？先说这三句",
        "summary": "电话英语没有肢体语言辅助，学会请求重复、确认信息和礼貌预约的标准流程。",
        "difficulty": 2,
        "tags": ["场景对话", "电话", "预约"],
        "duration_minutes": 9,
        "content": """## 听不清的三张安全牌

1. **Sorry, could you say that again?**（能再说一遍吗？）
2. **Sorry, the line is breaking up.**（信号不好，听不清。）
3. **Could you spell that for me?**（能拼一下吗？）

电话里听不清是常态，别慌着挂断，先甩这三句。

## 预约场景对话

**Receptionist:** Dental clinic, how can I help you?（牙科诊所，有什么可以帮您？）
**You:** I'd like to make an appointment for a cleaning.（我想预约洗牙。）
**Receptionist:** How about this Friday at 3 pm?（这周五下午三点怎么样？）
**You:** I'm afraid I'm working then. Is Saturday morning available?（那天上班，周六上午有空吗？）
**Receptionist:** Yes, 10 am on Saturday. Can I have your name and number?（可以，周六 10 点。请留姓名电话。）
**You:** Sure, it's Wang, 138-xxxx-xxxx.

## 电话礼仪句型

| 场景 | 表达 |
| --- | --- |
| 自报家门 | Hi, this is Wei calling from ABC Corp. |
| 找人 | Could I speak to Mr. Smith, please? |
| 请对方稍等 | Hold on a second, please. / One moment. |
| 帮人转接 | I'll put you through. |
| 对方不在 | He's not available right now. Can I take a message? |
| 留言 | Could you ask him to call me back? |

## 数字确认技巧

电话里数字最易错，听到后复述确认：**So that's 2-0-2-5, is that right?**（是 2025 对吧？）把单号、日期逐位复述一遍，能避免 90% 的沟通事故。""",
    },
    {
        "title": "看医生英语：症状描述模板句",
        "summary": "身体不舒服 abroad 不会说？掌握症状、病史、买药三条线的关键句型。",
        "difficulty": 2,
        "tags": ["场景对话", "医疗", "症状描述"],
        "duration_minutes": 10,
        "content": """## 描述症状的万能句式

**I've been + 症状 + for + 时长.**
- *I've had a sore throat for three days.*（嗓子疼三天了。）
- *I've been coughing a lot since last night.*（从昨晚开始咳嗽很厉害。）
- *I have a fever and my whole body aches.*（发烧，全身酸痛。）

## 常见症状词汇表

| 中文 | 英文 |
| --- | --- |
| 头疼 | headache |
| 流鼻涕 | runny nose |
| 恶心 | nausea / feel sick to my stomach |
| 头晕 | dizzy |
| 拉肚子 | diarrhea |
| 便秘 | constipation |
| 过敏 | allergy / allergic to... |

## 医生常问的话

- **What brings you in today?**（今天哪里不舒服？）
- **How long have you had these symptoms?**（症状持续多久了？）
- **Are you allergic to any medication?**（对药物过敏吗？）
- **Are you currently taking any medication?**（目前在服药吗？）

## 药房场景

买非处方药可以说：**Could you recommend something for a headache?**（头疼有什么推荐的药吗？）
关键询问：**How often should I take it?**（多久吃一次？）、**Does it make you drowsy?**（会犯困吗？）

小贴士：紧急情况直接拨 911（北美）或 999（英国），去急诊说 **I need to see a doctor right away.**""",
    },
    {
        "title": "Small Talk 艺术：和外国人寒暄不冷场",
        "summary": "天气、周末、球赛三大安全话题 + 结束对话的礼貌方式，让闲聊自然收尾。",
        "difficulty": 1,
        "tags": ["闲聊", "社交", "文化"],
        "duration_minutes": 8,
        "content": """## 三大万能话题

### 1. 天气（最安全）
- *Beautiful day, isn't it?*（天气真好，是吧？）
- *It's been raining all week. So sick of it.*（下了一整周雨，烦死了。）

### 2. 周末计划
- *Any plans for the weekend?*（周末有什么安排？）
- *How was your weekend?*（周末过得怎么样？）——周一万能开场。

### 3. 轻松话题：球赛、剧、美食
- *Did you catch the game last night?*（昨晚球赛看了吗？）
- *Been watching anything good lately?*（最近有什么好看的剧吗？）

## 寒暄的黄金结构

**问句 + 简短回答 + 反问**。只回答不反问，对话三秒死亡：
> *How's it going?* — **Not bad, pretty busy lately. You?** ✅
> *How's it going?* — **Fine.** ❌（对方不知道怎么接）

## 千万别问

- 年龄、收入、体重
- *Why are you still single?*（为什么还单身？）
- 政治与宗教（除非熟到不行）

## 优雅结束对话

- **Anyway, I should get going. Great talking to you!**（我该走了，跟你聊得很开心！）
- **Let's catch up soon.**（回头再聊）
- **I won't take up more of your time.**（不多占用你时间了）

说 Anyway 是社交暗号：对话要收尾了。拖太久反而不礼貌。""",
    },
    {
        "title": "表达观点：agree to disagree 的进阶讨论句型",
        "summary": "从 I think 升级到 12 种观点表达：委婉反对、部分同意、请求澄清一网打尽。",
        "difficulty": 3,
        "tags": ["观点表达", "讨论", "高级句型"],
        "duration_minutes": 12,
        "content": """## 摆出观点的 4 个层次

### 1. 直接表达
- *In my view, remote work is here to stay.*（在我看来，远程办公会一直存在。）
- *The way I see it, ...*（我个人的看法是…）

### 2. 部分同意（开会超实用）
- *I see your point, but...*（我理解你的意思，但是…）
- *That's true to some extent. However, ...*（某种程度上没错，然而…）
- *Fair enough, but have you considered...?*（有道理，但你考虑过…吗？）

### 3. 委婉反对
- *I'm not sure I agree with that.*（我不太确定是否同意。）
- *I'm afraid I see it differently.*（恐怕我的看法不同。）
- 直接说 *You're wrong* 在英语职场里几乎等于宣战，慎用。

### 4. 强硬但有礼貌的坚持
- *Let me put it another way.*（换个说法。）
- *With respect, the data says otherwise.*（恕我直言，数据不是这么说的。）

## 请求澄清三连

1. **Sorry, I'm not following. Could you elaborate?**（没跟上，能展开讲讲吗？）
2. **What exactly do you mean by that?**（具体指什么？）
3. **So if I understand correctly, you're saying...?**（我理解对的话，你是说…？）

最后一句是会议神器：先复述对方观点再回应，既显尊重又争取思考时间。

## agree to disagree

聊到僵局，来一句 *Let's agree to disagree.*（求同存异吧），既保留立场又不伤和气，是英语讨论文化里的体面终点。""",
    },
    {
        "title": "投诉与退货：礼貌但坚定的维护权益表达",
        "summary": "产品坏了、上错菜了怎么办？学会升级投诉的三段话术，不吵不闹把问题解决。",
        "difficulty": 3,
        "tags": ["投诉", "维权", "场景对话"],
        "duration_minutes": 10,
        "content": """## 投诉三段公式

**说明问题 → 表明期望 → 给出时限。**

> *I'm afraid there's a problem with my order. The screen arrived cracked. I'd like a full refund, and I hope this can be resolved by Friday.*（订单有问题，屏幕到货就碎了，我要求全额退款，希望周五前解决。）

## 场景对话：餐厅上错菜

**You:** Excuse me, I ordered the pasta, but this is the steak.（我点的是意面，这是牛排。）
**Waiter:** Oh, I'm terribly sorry. I'll fix that right away.（非常抱歉，马上处理。）
**You:** Thank you. No rush, but the sauce is also cold.（不急，但酱也是凉的。）

关键点：**一次只提一个核心问题**，情绪稳定地逐步升级，比一次性倾倒所有不满有效得多。

## 退货话术

- **I'd like to return this. Here's the receipt.**（退货，这是小票。）
- **It stopped working after two days.**（用了两天就坏了。）
- **I'd prefer a refund rather than store credit.**（我想要退款而不是购物卡。）

## 升级投诉的阶梯

1. 平静陈述问题：*This isn't what I expected.*
2. 明确诉求：*I'd like this replaced / refunded.*
3. 请管理者出面：*Could I speak to the manager, please?*
4. 最后通牒：*If it can't be sorted out, I'll have to contact my bank for a chargeback.*（解决不了我只能找银行拒付了。）

## 语言温度管理

多用 **I'm afraid... / Unfortunately...** 开头，配合 **but I do need this fixed** 的坚定尾句。礼貌是形式，诉求是实质，两者不冲突。""",
    },
    {
        "title": "时态在口语里的实战：说对时间感才像母语者",
        "summary": "have been doing 和 have done 到底差在哪？用 6 个生活场景把口语时态讲透。",
        "difficulty": 3,
        "tags": ["语法", "时态", "口语"],
        "duration_minutes": 13,
        "content": """## 场景 1：朋友问你最近在干嘛

- *I've been working on a side project.*（最近一直在做个副业项目，**强调持续过程**）
- *I've finished my side project.*（项目做完了，**强调结果**）

**have been doing** 看过程，**have done** 看结果。

## 场景 2：约人吃饭

- *I'm having dinner with Sarah tonight.*（今晚和人约了晚饭——**现在进行时表已定安排**）
- *I'll have dinner with Sarah.*（相对少用，显得临时决定）

和熟人约事，进行时比 will 更自然。

## 场景 3：讲过去的故事

说经历用过去时讲故事，插叙背景用过去进行时：
> *I was walking home when I ran into my old boss.*（走着走着撞见老领导。）

## 场景 4：聊体验

- *Have you ever been to Japan?*（去过日本吗？——**经历用 have been**）
- *I went there in 2019.*（具体时间点用过去时）

**have gone to** 是"去了还没回来"，说自己经历千万别说 *I have gone to Japan*。

## 场景 5：虚拟语气表达愿望

- *If I had more time, I would learn the guitar.*（要是时间够我就学吉他了——与现实相反）
- *I wish I could speak French.*（真希望我会法语）

## 场景 6：被放鸽子

- *I've been waiting for an hour!*（我已经等了一个小时了！——**等待的怨气用完成进行时**）

## 自测

把下面三句翻成英文：1）我学英语学了五年了；2）我上周刚把《绝命毒师》看完；3）要是我早点认识你就好了。答案会陆续出现在你的口语里。""",
    },
    {
        "title": "发音进阶：连读、弱读与缩略的地道感",
        "summary": "wanna、gotta 不是懒音而是规则。掌握连读弱读，口语瞬间从教科书升级到街头感。",
        "difficulty": 2,
        "tags": ["发音", "连读", "听力"],
        "duration_minutes": 14,
        "content": """## 为什么你听不懂母语者

不是词汇量不够，而是他们说的不是你背的形状：**What do you want to do?** 实际发音接近 *Whaddaya wanna do?*。听力卡壳，八成败在连读弱读。

## 连读三规律

### 1. 辅音 + 元音 → 拼起来
- *not at all* → no-ta-tall
- *check it out* → che-cki-tout

### 2. 相同辅音 → 只读一次并拉长
- *bad day* → ba(g)day
- *some money* → so(m)money

### 3. t 在两个元音间 → 闪音（近似 d）
- *water* → **wader**（美音）
- *better* → **bedder**

## 弱读：虚词悄悄消失

实词（名词、动词）重读，虚词（a、of、to、for、and）弱读成含糊的 /ə/：
> *a cup of tea* → /ə kup əv tiː/
> *fish and chips* → fish **n** chips

## 缩略语不是错误，是习惯

| 缩略 | 完整形式 | 场景 |
| --- | --- | --- |
| wanna | want to | 口语 |
| gotta | have got to | 口语 |
| gonna | going to | 口语 |
| kinda | kind of | 有点儿 |

注意：这些**只用于口语和非正式文字**，商务邮件请老老实实写 want to。

## 训练方法：影子跟读

1. 挑一段 30 秒的美剧台词（语速自然的）
2. 第一遍盲听抓大意
3. 第二遍看文本标出连读弱读位置
4. 第三遍影子跟读：落后原声 0.5 秒同步说
5. 录音对比原声，差距就是你的进步空间

每天 10 分钟，两周后你会发现美剧突然"变清楚了"——其实是你耳朵升级了。""",
    },
    {
        "title": "数字与时间表达：报价、日期、倍数的精确说法",
        "summary": " billion 和 million 别再数错零：价格、百分比、日期与倍数的职场精确表达。",
        "difficulty": 2,
        "tags": ["数字表达", "职场", "听力"],
        "duration_minutes": 9,
        "content": """## 大数字的英语读法

| 数字 | 英文 | 易错点 |
| --- | --- | --- |
| 1,000 | one thousand | — |
| 10,000 | ten thousand | 中文"万"，英语没有万！ |
| 100,000 | one hundred thousand | 十万 = 百千 |
| 1,000,000 | one million | 百万 |
| 1,000,000,000 | one billion | 十亿 |

**核心口诀：以千和百万为台阶，三位一分节。** 45,000 读作 *forty-five thousand*，不是 *forty-five wan*。

## 价格与百分比

- 报价：*It's $59.99.* → **fifty-nine ninety-nine**（口语常省略 dollars and cents）
- 折扣：*20% off* = 打八折（注意：off 是减掉的部分！**80% off** 是一折不是八折）
- 增长：*Sales grew by 15%.*（增长了 15%）vs *Sales grew to 15 million.*（增长到 1500 万）——by 和 to 一字之差。

## 日期读法

- 2026-10-10（美式）：*October tenth, twenty twenty-six*
- 年份读法：**twenty twenty-six**，不读 *two thousand and twenty-six*（过时且啰嗦）
- 1990s：*the nineties*（九十年代）

## 时间的精确表达

- 9:15 → *nine fifteen* / *a quarter past nine*
- 9:45 → *nine forty-five* / *a quarter to ten*
- 上午 9 点开会：*The meeting is at 9 am.* 用 **at**；**in the morning** 泛指早上

## 倍数表达

- *The new office is three times as big.*（大三倍 = 是原来的三倍大）
- *Twice as expensive as...*（贵一倍）
- *Sales doubled.*（翻倍了）triple 翻三倍，quadruple 翻四倍

## 听力自测

让朋友随机报 5 个大数字和 3 个日期，你写下来对答案。错 2 个以上，本周每天练 5 分钟。""",
    },
    {
        "title": "租房英语：看房、签合同与押金全流程",
        "summary": "从 I'm looking for a two-bedroom 到 security deposit，海外租房每个环节的表达清单。",
        "difficulty": 2,
        "tags": ["场景对话", "租房", "生活"],
        "duration_minutes": 11,
        "content": """## 看房对话

**Agent:** What kind of place are you looking for?（想找什么样的房子？）
**You:** I'm looking for a two-bedroom apartment near downtown, under $1,500 a month.（想找市中心附近的两居室，月租 1500 美元以内。）
**Agent:** Are utilities included?（含水电吗？）
**You:** Is the internet included in the rent?（网费含在房租里吗？）
**Agent:** Water is, but electricity and internet are on you.（含水，电和网自理。）

## 关键词汇表

| 中文 | 英文 |
| --- | --- |
| 押金 | security deposit |
| 月租 | monthly rent |
| 水电网费 | utilities |
| 家具齐全 | fully furnished |
| 合租 | share a flat / roommate |
| 中介费 | agency fee |
| 提前退租 | break the lease |

## 必问的 6 个问题

1. **How long is the lease?**（租期多长？）
2. **What's the deposit, and is it refundable?**（押金多少，可退吗？）
3. **Are there any extra fees?**（有额外费用吗？）
4. **Who handles repairs?**（维修谁负责？）
5. **Can I sublet it if I move out early?**（提前搬走能转租吗？）
6. **What's notice period for moving out?**（退租要提前多久通知？）

## 签约与验房

签合同前逐条看 **terms and conditions**（条款），特别注意 **early termination clause**（提前解约条款）。

入住当天拍照留存 **for the record**（留档），退租时说：*The apartment is in the same condition as when I moved in. I'd like my deposit back, please.*（房子和我入住时一样，请退还押金。）

押金纠纷是海外租房最高发问题，照片就是你最好的证据。""",
    },
]
