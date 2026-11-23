"""嵌入式开发模块种子数据（C 语言、STM32、通信协议、FreeRTOS、调试）。"""

MODULE = {
    "code": "embedded",
    "name": "嵌入式开发",
    "description": "从 C 语言进阶到 STM32 外设、FreeRTOS 实时系统与调试技巧，15 篇硬核文章带你打通嵌入式全链路。",
    "icon": "🔧",
    "color": "#34d399",
    "sort_order": 2,
}

ARTICLES = [
    {
        "title": "C 语言指针进阶：指针数组、数组指针与函数指针",
        "summary": "int (*p)[4] 和 int *p[4] 到底谁是谁？一篇理清嵌入式 C 里最容易绕晕的指针组合。",
        "difficulty": 2,
        "tags": ["C语言", "指针", "基础进阶"],
        "duration_minutes": 15,
        "content": """## 指针数组 vs 数组指针

```c
int *p[4];    // 指针数组：4 个元素的数组，每个元素是 int*
int (*q)[4];  // 数组指针：1 个指针，指向含 4 个 int 的数组
```

判读口诀：**看变量名先和谁结合**。`[]` 优先级高于 `*`，所以 `p` 先是数组；`q` 被括号强制先与 `*` 结合，所以是指针。

## 典型应用场景

### 指针数组：字符串表

```c
const char *menu[] = {"LED Control", "UART Echo", "Sensor Read"};
for (int i = 0; i < 3; i++) {
    uart_print(menu[i]);
}
```
嵌入式里做命令解析、菜单显示，全靠它，比二维数组省 RAM（只存地址不存内容）。

### 数组指针：二维数组传参

```c
void print_map(int (*m)[4], int rows) {
    for (int r = 0; r < rows; r++)
        for (int c = 0; c < 4; c++)
            printf("%d ", m[r][c]);
}
```

## 函数指针：回调的灵魂

```c
typedef void (*irq_handler_t)(void);

void uart_isr(void) { /* 处理接收 */ }

irq_handler_t handlers[2] = {uart_isr};
handlers[0]();  // 通过指针调用
```

STM32 HAL 库里的 `HAL_UART_RxCpltCallback`、FreeRTOS 的定时器回调，本质都是函数指针。理解它，才能理解整个中断回调机制。

## 常见错误

1. **野指针**：局部变量地址被返回，栈帧销毁后访问 → HardFault。
2. **解引用空指针**：malloc 失败返回 NULL 未检查。
3. **类型不匹配**：`float*` 强转 `uint32_t*` 再解引用，多数平台可行但违反严格别名规则。

## 一道经典面试题

`*(*(a + 2) + 3)` 中 a 是二维数组，等价于 `a[2][3]`。理解这点，指针就算入门了。""",
    },
    {
        "title": "volatile 关键字：嵌入式 C 的第一道坎",
        "summary": "为什么调试时正常、优化后失灵？90% 是 volatile 没加。从编译器优化机制讲透它。",
        "difficulty": 2,
        "tags": ["C语言", "volatile", "编译器"],
        "duration_minutes": 10,
        "content": """## 一个诡异的现象

```c
uint32_t *status_reg = (uint32_t *)0x40021000;
while (*status_reg & FLAG_READY) {
    ;  // 等待硬件就绪
}
```

**开 -O2 优化后死循环。** 因为编译器看到循环体内没人改 `*status_reg`，直接把读取优化成读一次寄存器，值不再刷新。

## volatile 的作用

`volatile` 告诉编译器：**这个变量随时可能被外部改变，每次都必须老老实实从内存读**。

```c
volatile uint32_t *status_reg = (uint32_t *)0x40021000;
```

三个必须加 volatile 的场景：

| 场景 | 原因 |
| --- | --- |
| 硬件寄存器映射 | 值由外设硬件改变 |
| 中断服务程序与主程序共享的变量 | 值由 ISR 改变 |
| 多线程/多任务共享的标志 | 值由其他任务改变 |

## 典型错误案例

```c
volatile bool rx_done = false;          // ✅ 正确
void USART1_IRQHandler(void) { rx_done = true; }

int main(void) {
    while (!rx_done) { }                // volatile 版本能退出
}
```

如果去掉 volatile，主循环可能被优化成 `while(1)`，程序永远"卡死"——但用调试器单步执行时又一切正常（单步会强制刷新内存），这是嵌入式调试最经典的灵异现象。

## volatile ≠ 原子性

注意：volatile **只保证可见性，不保证原子性**。对 32 位变量在 32 位 MCU 上的读写天然原子，但 `count++` 这种"读-改-写"三步操作，中断里和主循环同时做仍会丢数据，需要关中断保护：

```c
__disable_irq();
count++;
__enable_irq();
```

## 记忆口诀

**寄存器必加、中断共享必加、任务共享必加**；纯软件局部变量、加了互斥锁的变量不加（加了反而影响优化）。""",
    },
    {
        "title": "STM32 GPIO 从寄存器到 HAL：点亮 LED 的两种姿势",
        "summary": "操作寄存器 ODR/BSRR 与调 HAL_GPIO_WritePin 有什么区别？从时钟树讲到推挽开漏。",
        "difficulty": 1,
        "tags": ["STM32", "GPIO", "HAL库"],
        "duration_minutes": 12,
        "content": """## 点亮 LED 的最小流程

1. **使能 GPIO 时钟**：STM32 外设默认断电省电，先开时钟
2. **配置引脚模式**：输出、推挽、速度
3. **写电平**

### HAL 库版（推荐入门）

```c
__HAL_RCC_GPIOA_CLK_ENABLE();

GPIO_InitTypeDef gpio = {0};
gpio.Pin   = GPIO_PIN_5;
gpio.Mode  = GPIO_MODE_OUTPUT_PP;   // 推挽输出
gpio.Speed = GPIO_SPEED_FREQ_LOW;
HAL_GPIO_Init(GPIOA, &gpio);

HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);    // 亮
HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);                  // 翻转
```

### 寄存器直操版（理解底层）

```c
RCC->AHB1ENR  |= RCC_AHB1ENR_GPIOAEN;      // 开时钟
GPIOA->MODER  |= (1 << 10);                 // PA5 设为输出
GPIOA->BSRR   = GPIO_PIN_5;                 // 置 1（原子操作）
GPIOA->BSRR   = GPIO_PIN_5 << 16;           // 置 0
```

## BSRR 的精妙之处

写 ODR 是"读-改-写"，中断插入时可能互相覆盖。**BSRR 写 1 置位、高 16 位写 1 复位，一条指令完成且原子**——这就是为什么中断里翻转引脚推荐 BSRR。

## 推挽 vs 开漏

| 模式 | 特点 | 场景 |
| --- | --- | --- |
| 推挽 PP | 主动输出高低电平，驱动强 | 普通输出、LED |
| 开漏 OD | 只能拉低，高电平靠外部上拉 | I2C 总线、电平转换、线与 |

判断口诀：**需要"多个设备共用一根线"就用开漏 + 上拉**。

## 踩坑记录

- 引脚怎么都不输出：八成忘了开时钟。
- LED 反逻辑（写 0 亮）：很多板子 LED 接 VCC，低电平导通，看原理图别猜。
- 复用引脚冲突：PA5 同时被 SPI 配置占用，先检查 AF 复用映射表。""",
    },
    {
        "title": "中断系统详解：NVIC 优先级与抢占那些事",
        "summary": "抢占优先级和子优先级的区别、中断嵌套规则、为什么 ISR 里不能 delay。",
        "difficulty": 2,
        "tags": ["STM32", "中断", "NVIC"],
        "duration_minutes": 14,
        "content": """## 中断的到达路径

外设事件 → EXTI/外设中断标志 → NVIC 仲裁 → CPU 跳到中断向量表对应入口 → 执行 ISR → 清标志返回。

## NVIC 优先级机制

STM32 用 4 位表达优先级，可拆分为**抢占优先级**与**子优先级**：

- **抢占优先级**：数值越小越优先，**高的可以打断低的**（中断嵌套）
- **子优先级**：同时挂起时谁先响应，**不能互相打断**

```c
HAL_NVIC_SetPriority(USART1_IRQn, 1, 0);   // 抢占 1，子 0
HAL_NVIC_EnableIRQ(USART1_IRQn);
```

### 嵌套规则示例

| 中断 | 抢占优先级 | 能否被彼此打断 |
| --- | --- | --- |
| A | 0 | A 运行时 B/C 都不能打断 |
| B | 1 | B 运行时可被 A 打断 |
| C | 1 | C 与 B 之间不能互相打断 |

## ISR 编写铁律

1. **短小快**：只做取数据、置标志，复杂处理放主循环或任务
2. **禁止 delay、禁止 printf**：阻塞会让低优先级中断全部饿死
3. **记得清中断标志**：不清则退出后立即重入，死循环
4. **共享变量加 volatile**，必要时关中断保护

```c
volatile uint8_t rx_byte;

void USART1_IRQHandler(void) {
    if (USART1->SR & USART_SR_RXNE) {
        rx_byte = USART1->DR;   // 读 DR 自动清 RXNE
        rx_flag = 1;
    }
}
```

## 经典问题：SysTick 与 HAL_Delay 死锁

在优先级 ≥ SysTick 的 ISR 里调用 `HAL_Delay`，SysTick 永远无法抢占 → Delay 永远不返回。**记住：ISR 里绝不调用阻塞函数**，用时间戳标记代替。

## 调试技巧

HardFault 后在 Keil/IAR 查看 LR 寄存器判断是线程模式还是handler 模式崩溃，再把 PC/LR 地址对照 .map 文件定位到函数——这招能救 90% 的玄学崩溃。""",
    },
    {
        "title": "定时器原理与实战：从 1ms 心跳到 PWM 呼吸灯",
        "summary": "定时器溢出公式怎么算？PWM 占空比与呼吸灯的关系，一篇讲透 STM32 定时器。",
        "difficulty": 2,
        "tags": ["STM32", "定时器", "PWM"],
        "duration_minutes": 13,
        "content": """## 定时时间公式

定时器本质是**计数器**：输入时钟 CK_CNT 经预分频 PSC 分频，计数到 ARR 自动重装。

```
定时时间 = (ARR + 1) × (PSC + 1) / CK_PSC
```

例：84MHz 时钟，想要 1ms 中断：
- PSC = 83（84MHz / 84 = 1MHz，计一个数 1µs）
- ARR = 999（计 1000 个数 = 1ms）

**先定分频让计数粒度够细，再定重装值凑时长。**

## 两种最常用模式

### 1. 定时中断（系统心跳）

```c
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {
        g_system_tick++;          // 1ms 心跳，非阻塞延时基石
    }
}
```

有了它就能写出非阻塞式状态机，替代 HAL_Delay：

```c
if (now - last_ts > 500) {   // 每 500ms 执行
    HAL_GPIO_TogglePin(...);
    last_ts = now;
}
```

### 2. PWM 输出（呼吸灯/电机）

PWM 频率由 ARR 决定，占空比由 CCR 决定：

```c
HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
__HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, duty);  // duty ∈ [0, ARR]
```

**呼吸灯技巧**：亮度感知是非线性的，用平方曲线 `duty = (i*i)/period` 比线性递增顺眼得多。

## 输入捕获：测频率神器

上升沿捕获计数值 t1，下一个上升沿捕获 t2，`频率 = 1/(t2-t1)×CK_CNT`。测超声波 HC-SR04 回波脉宽、红外解码全靠它。

## 常见翻车点

- PSC 忘了减 1：定时时间全错
- 中断标志未清：回调只进来一次
- PWM 死区：驱动电机半桥时必须配置死区时间，否则上下管直通炸管""",
    },
    {
        "title": "UART 串口通信：波特率、帧格式与 printf 重定向",
        "summary": "调试利器串口怎么配？从起始位讲到 DMA 收发不定长数据，附 IDLE 中断方案。",
        "difficulty": 1,
        "tags": ["UART", "串口", "通信"],
        "duration_minutes": 12,
        "content": """## UART 帧格式

```
空闲(高) | 起始位(低) | D0 D1 D2 D3 D4 D5 D6 D7 | 校验位(可选) | 停止位(高)
```

**波特率必须双方一致**，115200 表示每秒 115200 个码元。差 2% 以上就会出现乱码——串口助手看到 `å½ ä¸²` 这种天书，先查波特率。

## 最小收发代码

```c
huart1.Instance = USART1;
huart1.Init.BaudRate = 115200;
huart1.Init.WordLength = UART_WORDLENGTH_8B;
huart1.Init.StopBits = UART_STOPBITS_1;
huart1.Init.Parity = UART_PARITY_NONE;
huart1.Init.Mode = UART_MODE_TX_RX;
HAL_UART_Init(&huart1);

HAL_UART_Transmit(&huart1, (uint8_t *)"Hello\\n", 6, 100);
```

## printf 重定向（调试基本功）

```c
#include <stdio.h>
int fputc(int ch, FILE *f) {
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, 10);
    return ch;
}
```
Keil 勾选 Use MicroLIB，之后 `printf("temp=%d\\n", t)` 直接上屏。

## 不定长数据接收：IDLE + DMA 方案

传统定长接收很死板，工业协议多为不定长。套路：

1. 开 DMA 循环接收
2. 使能 **IDLE 空闲中断**（总线空闲一帧结束触发）
3. 中断里计算收到的字节数，拷贝数据，置标志

```c
void USART1_IRQHandler(void) {
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_IDLE)) {
        __HAL_UART_CLEAR_IDLEFLAG(&huart1);
        uint16_t len = BUF_SIZE - __HAL_DMA_GET_COUNTER(huart1.hdmarx);
        memcpy(rx_msg, rx_buf, len);
        rx_ready = 1;
    }
}
```

## 常见问题排查表

| 现象 | 先查什么 |
| --- | --- |
| 全是乱码 | 波特率、晶振频率配置 |
| 能发不能收 | RX 引脚模式、是否开 RXNE 中断 |
| 偶尔丢字节 | 改用 DMA，或提高中断优先级 |
| USB 转串口无数据 | TX/RX 是否交叉连接 |""",
    },
    {
        "title": "I2C 总线深入：时序、地址与上拉电阻的坑",
        "summary": "两根线怎么挂多个设备？为什么 SCL 要 4.7k 上拉？ACK/NACK 机制一次讲清。",
        "difficulty": 2,
        "tags": ["I2C", "总线", "传感器"],
        "duration_minutes": 13,
        "content": """## I2C 基本面

两根线：**SCL** 时钟 + **SDA** 数据。开漏输出 + 上拉电阻（标准 4.7kΩ），支持多主多从，通过**7 位地址**寻址。

## 一次完整通信

```
START → [地址+读写位] → ACK → [寄存器地址] → ACK → [数据]... → STOP
```

- **START**：SDA 在 SCL 高电平时由高变低
- **读写位**：0 写 1 读，所以 0x68 的 MPU6050 写地址是 0xD0（0x68 << 1）
- **ACK**：第 9 个时钟由接收方拉低 SDA 表示收到；NACK 表示拒绝或数据结束

## HAL 读写传感器示例

```c
uint8_t who_am_i;
HAL_I2C_Mem_Read(&hi2c1, 0xD0, 0x75, I2C_MEMADD_SIZE_8BIT,
                 &who_am_i, 1, 100);
// WHO_AM_I 应返回 0x68
```

## 上拉电阻怎么选

I2C 是开漏，没人拉高总线就永远低电平。上拉阻值权衡：

| 阻值 | 上升沿 | 适用 |
| --- | --- | --- |
| 1k~2k | 陡峭 | 高速 400kHz+、长线 |
| 4.7k | 标准 | 100kHz 常规 |
| 10k | 缓慢 | 低速短距离、超低功耗 |

**总线越长电容越大，上升沿越缓，需减小阻值**；但太小（<1k）灌电流过大可能烧管。

## 玄学问题排查清单

1. **总线卡死**：从机拉死 SDA 不放 → 主机发 9 个 SCL 时钟强制释放
2. **读回全 0xFF**：没上拉，或地址错了
3. **读回全 0x00**：SDA/SCL 接反，或设备没供电
4. **时好时坏**：杜邦线太长，降速到 100kHz 或缩短线材

## 实用技巧

用逻辑分析仪抓一次完整波形（几十块的 Saleae 克隆版足够），对着时序图看一遍，比读十遍手册都管用。""",
    },
    {
        "title": "SPI 全双工实战：与 I2C 如何选择",
        "summary": "CPOL/CPHA 四种模式怎么配？屏幕、Flash、SD 卡为什么都爱 SPI？速度上限差在哪。",
        "difficulty": 2,
        "tags": ["SPI", "通信", "外设驱动"],
        "duration_minutes": 11,
        "content": """## SPI 四线制

- **SCK**：时钟（主机产生）
- **MOSI**：主出从入
- **MISO**：主入从出
- **CS/NSS**：片选（每个从机一根，低有效）

全双工，速率轻松跑 10MHz+，比 I2C（标准 100k）快两个数量级。

## 模式配置：CPOL 与 CPHA

| 模式 | CPOL | CPHA | 采样时机 |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 第一个边沿采样（常用） |
| 1 | 0 | 1 | 第二个边沿采样 |
| 2 | 1 | 0 | 第一个边沿采样 |
| 3 | 1 | 1 | 第二个边沿采样（多数屏幕/Flash 用这个） |

**配置错了读到的数据是移位的乱码**。查芯片手册时序图：空闲时 SCK 电平 = CPOL，第一个还是第二个边沿采样 = CPHA。

## HAL 读写 Flash（W25Q64）示例

```c
uint8_t cmd = 0x9F;                 // Read JEDEC ID
uint8_t id[3] = {0};

HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET);   // 片选拉低
HAL_SPI_Transmit(&hspi1, &cmd, 1, 100);
HAL_SPI_Receive(&hspi1, id, 3, 100);
HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET);     // 释放
// id 应为 EF 40 17
```

## SPI vs I2C 选型表

| 维度 | SPI | I2C |
| --- | --- | --- |
| 线数 | 4 + 每从机 1 根 CS | 2 根 |
| 速度 | 10~50MHz+ | 100k/400k/1M |
| 寻址 | 硬件片选 | 软件地址 |
| 设备数多时 | CS 线爆炸 | 地址冲突风险 |
| 典型设备 | 屏幕、Flash、SD、ADC | 传感器、EEPROM、OLED 小屏 |

**经验法则：大数据量高速用 SPI，低速多传感器挂总线用 I2C。**

## 踩坑提示

- 屏幕 SPI 刷屏慢：开 DMA 传输，速度提升 3 倍以上
- MISO 悬空读全 FF：从机未选中，查 CS 极性
- 多从机互扰：切换 CS 前确保前一设备已释放总线""",
    },
    {
        "title": "FreeRTOS 任务管理：优先级、栈大小与调度机制",
        "summary": "任务为什么神秘跑飞？栈分配多大合适？从调度器原理到 uxTaskGetStackHighWaterMark 实测。",
        "difficulty": 3,
        "tags": ["FreeRTOS", "RTOS", "任务调度"],
        "duration_minutes": 16,
        "content": """## 任务三要素

```c
void sensor_task(void *arg) {
    for (;;) {                          // 任务绝不 return！
        read_sensor();
        vTaskDelay(pdMS_TO_TICKS(100)); // 阻塞让出 CPU
    }
}

xTaskCreate(sensor_task, "sensor", 256, NULL, 3, NULL);
//                            栈:256字=1KB   优先级:3
```

## 调度规则

FreeRTOS 默认**抢占式 + 时间片轮转**：

- **高优先级就绪 → 立即抢占低优先级**
- 同优先级任务时间片轮流跑
- **空闲任务（优先级 0）兜底**，永远存在

⚠️ 高优先级任务里若有 `for(;;){}` 且不阻塞，低优先级任务全部饿死，看门狗复位——这是新手第一大坑。

## 栈大小怎么定

任务栈单位是**字**（STM32 上 1 字 = 4 字节）。估算方法：

1. 先给个保守值：无 printf/浮点 256 字起步，有 printf 512 字起步
2. 运行时实测：

```c
UBaseType_t wm = uxTaskGetStackHighWaterMark(NULL);
printf("stack min free: %u words\\n", wm);
```

HighWaterMark 是历史最小剩余量。**剩余小于总量的 20% 就该扩栈**，接近 0 就是定时炸弹。

## 任务状态机

```
Running ⇄ Ready ⇄ Blocked
                ↓
             Suspended (vTaskSuspend 挂起)
```

只有 Blocked/Suspended 的任务不参与调度。vTaskDelay 是 Blocked，while 忙等是 Ready——**后者会持续吃 CPU**。

## 优先级分配经验

| 优先级 | 放什么 |
| --- | --- |
| 最高 | 硬实时、周期短：电机控制、安全保护 |
| 中 | 数据采集、通信协议解析 |
| 低 | 日志、UI 刷新、 статист上报 |
| 0 | 别用，留给空闲任务 |

## 常见死因清单

1. 栈溢出 → 改小栈后复现，配置 `configCHECK_FOR_STACK_OVERFLOW=2` 钩子抓现行
2. 任务函数 return → FreeRTOS 会直接挂掉（新版本断言报错）
3. 在中断里调用 `vTaskDelay` → 换 `vTaskDelayUntil` 的任务版或直接禁止
4. 共享资源没保护 → 见下一篇信号量与互斥量""",
    },
    {
        "title": "FreeRTOS 队列、信号量与互斥量：选对工具才不翻车",
        "summary": "ISR 里用哪个 API？二值信号量和互斥量的区别？生产者-消费者模型完整示例。",
        "difficulty": 3,
        "tags": ["FreeRTOS", "IPC", "并发"],
        "duration_minutes": 15,
        "content": """## 三种工具的定位

| 工具 | 传递什么 | 典型场景 |
| --- | --- | --- |
| 队列 Queue | 数据本身（拷贝） | ISR → 任务传传感器数据 |
| 二值/计数信号量 | 事件发生与否 | 中断通知任务处理 |
| 互斥量 Mutex | 资源所有权 | 保护 UART/SPI/共享缓冲 |

**记住一句话：传数据用队列，传事件用信号量，锁资源用互斥量。**

## 生产者-消费者完整示例

```c
QueueHandle_t adc_queue;

void adc_isr(void) {                        // 生产者：中断
    uint16_t v = ADC1->DR;
    xQueueSendFromISR(adc_queue, &v, NULL); // FromISR 版本！
}

void process_task(void *arg) {              // 消费者：任务
    uint16_t v;
    for (;;) {
        if (xQueueReceive(adc_queue, &v, portMAX_DELAY) == pdTRUE) {
            process(v);
        }
    }
}
```

队列内部自带阻塞唤醒机制：队列空时消费者休眠，ISR 写入后自动唤醒——**零轮询，CPU 占用极低**。

## ISR 黄金法则

中断里**只能用 `FromISR` 后缀的 API**：

- `xQueueSendFromISR`
- `xSemaphoreGiveFromISR`
- `xTaskNotifyFromISR`

普通版本在中断上下文调用会直接触发 configASSERT 断言失败。

## 互斥量 vs 二值信号量

看起来都"给一下、拿一下"，本质区别：

- **互斥量有优先级继承**：低优先级任务持锁时，自动提升到等待者中最高优先级，**防止优先级反转**
- 二值信号量没有，用它当锁可能出现优先级反转事故（火星探路者号的真实 Bug）

**规则：当锁用 mutex，当事件用 semaphore，不要混。**

## 优先级反转再现场

```
低优先级 L 持有锁 → 高优先级 H 等锁 → 中优先级 M 抢占 L 跑个没完
→ H 被 M 间接阻塞 = 反转
```

互斥量的优先级继承把 L 临时抬到 H 级，M 插不进来，链条断掉。

## 死锁预防

两个任务互相等对方的锁就死锁。预防法：**统一全系统加锁顺序**，或一次 `xSemaphoreTakeRecursive` 持有全部资源再操作。""",
    },
    {
        "title": "低功耗设计实战：Stop 模式与唤醒策略",
        "summary": "电池设备如何做到待机电流 2µA？Stop/Standby 模式对比、RTC 唤醒与外设状态恢复。",
        "difficulty": 3,
        "tags": ["低功耗", "STM32", "电源管理"],
        "duration_minutes": 14,
        "content": """## STM32 低功耗模式速查

| 模式 | 典型电流 | RAM/寄存器 | 唤醒后 |
| --- | --- | --- | --- |
| Sleep | mA 级 | 保持 | 继续运行，唤醒最快 |
| Stop | ~µA 级 | 保持 | 从唤醒点继续，时钟需重新配置 |
| Standby | <2µA | **丢失** | 相当于复位，从复位向量启动 |

**选型口诀：要秒级响应用 Stop，要月级续航用 Standby（配合 RTC 闹钟）。**

## Stop 模式 + RTC 唤醒模板

```c
void enter_stop(uint32_t seconds) {
    // 1. 关闭不用的外设，配置 GPIO 为模拟输入防漏电
    HAL_ADC_DeInit(&hadc);
    GPIO_InitTypeDef g = {0};
    g.Mode = GPIO_MODE_ANALOG;
    g.Pin = GPIO_PIN_All;
    HAL_GPIO_Init(GPIOA, &g);

    // 2. 设置 RTC 闹钟
    set_rtc_alarm(seconds);

    // 3. 进入 Stop
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);

    // 4. 唤醒后：系统时钟变回 HSI 8MHz，必须重配！
    SystemClock_Config();
}
```

## 唤醒后的头号大坑

**Stop 唤醒后 SYSCLK 自动切到 HSI 8MHz**，如果你的主程序跑 72MHz PLL，唤醒后所有波特率、定时周期全乱。**唤醒第一件事：重新调用 SystemClock_Config()**。

## 功耗优化清单

1. **不用的 GPIO 设为模拟输入**（默认浮空输入会漏电）
2. 关调试口后再测电流（DBGMCU 会阻止低功耗）
3. LED、上拉电阻、传感器供电用 MOS 管控制，睡眠时彻底断电
4. 降主频比关外设省得多：72MHz 降至 8MHz 功耗约降 70%
5. 测量用万用表 µA 档串联供电回路，别信开发板 LDO 输出端读数

## 真实案例：水表电池方案

每天唤醒 48 次读表 + LoRa 上报，每次活跃 200mA×50ms：
- 平均电流 = 48×0.05×200/86400 ≈ **5.6µA**
- 2400mAh 锂亚电池 → 理论寿命 **48 年**，实际按自放电算 10~15 年

低功耗设计的本质：**把活跃时间压到极致，其余时间装死**。""",
    },
    {
        "title": "Bootloader 与 IAP：远程升级固件的原理解析",
        "summary": "固件怎么通过 OTA 写进 Flash？中断向量表偏移、双 Bank 方案与 CRC 校验全流程。",
        "difficulty": 3,
        "tags": ["Bootloader", "IAP", "OTA"],
        "duration_minutes": 16,
        "content": """## Flash 布局设计

```
0x08000000 ┌────────────────┐
           │ Bootloader 16KB │  上电最先跑，负责升级与跳转
0x08004000 ├────────────────┤
           │ App  ~256KB     │  业务固件
0x08040000 └────────────────┘
```

## 升级流程

1. App 收到新固件（UART/BLE/WiFi），分包写入下载区
2. 全部接收后 **CRC 校验**
3. 设置标志写入 Flash（如 `OTA_FLAG = 0xA5`），触发系统复位
4. **Bootloader 先启动**，读到标志 → 搬运/擦写新固件 → 清标志 → 跳转新 App
5. 校验失败 → 保留旧固件继续跑（回滚保障）

## Bootloader 跳转 App 的标准动作

```c
#define APP_ADDR 0x08004000

typedef void (*pFunction)(void);

void jump_to_app(void) {
    uint32_t sp = *(volatile uint32_t *)APP_ADDR;          // 1. 取栈顶
    uint32_t pc = *(volatile uint32_t *)(APP_ADDR + 4);    // 2. 取复位向量

    HAL_RCC_DeInit();
    HAL_DeInit();
    SysTick->CTRL = 0;                                     // 3. 关中断源

    __set_MSP(sp);                                         // 4. 设栈指针
    ((pFunction)pc)();                                     // 5. 跳转
}
```

## App 侧必改的两处

1. **中断向量表偏移**：`SCB->VTOR = 0x08004000;`（不改则所有中断飞掉，程序一进中断就 HardFault——IAP 最经典翻车点）
2. **链接地址**：Keil IROM 起始改为 0x08004000，或修改 .ld 文件

## 可靠性三件套

| 机制 | 作用 |
| --- | --- |
| CRC32 校验 | 防止传输/写入损坏的固件被运行 |
| 升级标志 + 两次确认 | 新固件跑通后回写"运行正常"，超时未确认则回滚 |
| 固件版本号 | Bootloader 校验兼容性，防降级冲突 |

## 写入 Flash 注意

STM32 写 Flash 最小单位是**半字/双字**（按系列），擦除以**页/扇区**为单位且擦除期间 CPU 停摆——写入过程必须关中断或放入 Bootloader 中执行。""",
    },
    {
        "title": "调试方法论：HardFault 定位与逻辑分析仪实战",
        "summary": "程序莫名跑飞别再裸奔重试：Cortex-M 故障寄存器分析 + 观测工具箱，系统性排错流程。",
        "difficulty": 3,
        "tags": ["调试", "HardFault", "工具"],
        "duration_minutes": 15,
        "content": """## HardFault 三大来源

1. **野指针访问**：访问未映射地址（最常见）
2. **栈溢出**：局部大数组、递归、中断嵌套深
3. **未对齐/非法指令**：函数指针飞了

## 定位套路：看 SCB 故障寄存器

HardFault_Handler 里断点停下，看这几个寄存器：

| 寄存器 | 含义 |
| --- | --- |
| SCB->CFSR | 具体故障类型（位域展开） |
| SCB->HFSR | FORCED 位=1 表示升级成了 HardFault |
| 栈里的 PC | 崩溃时刻执行的指令地址 |

**把栈里的 PC 值拿去 .map 文件查**，直接定位到函数甚至行号。Keil 的 Fault Analyzer 和 VSCode Cortex-Debug 插件都能自动做这一步。

```c
void HardFault_Handler(void) {
    __asm volatile (
        "tst lr, #4          \\n"
        "ite eq              \\n"
        "mrseq r0, msp       \\n"
        "mrsne r0, psp       \\n"
        "b hardfault_c       \\n"
    );
}
// hardfault_c 里解析栈帧的 PC/LR，经串口打印出来
```

## 观测工具箱

| 工具 | 用途 |
| --- | --- |
| 逻辑分析仪 | 抓 I2C/SPI/UART 波形，看协议层时序 |
| 示波器 | 看模拟量、电源毛刺、PWM 实际输出 |
| SWD 调试器 | 断点、单步、看寄存器 |
| ITM/SWO printf | 不占用 UART 的轻量日志 |
| SEGGER RTT | 高速双向日志，强烈推荐 |

## 系统性排错流程

1. **复现**：找到稳定触发条件（概率性问题先查中断竞态、时序依赖）
2. **二分**：注释代码段定位到最小复现集
3. **观测**：加日志/抓波形，获取证据而不是猜
4. **假设验证**：一次只改一个变量
5. **回归**：修复后跑完整流程确认无副作用

## 经验之谈

- 玄学复位先查**看门狗**和**栈溢出**
- 加了 printf 就正常 = 时序问题（printf 拖了时间），别高兴太早
- 断点下正常全速跑就崩 = 竞态或 volatile 缺失
- 静电/插拔就死 = 硬件防护问题，加 TVS、改善接地""",
    },
    {
        "title": "嵌入式代码架构：分层设计与模块解耦",
        "summary": "从面条代码到可移植固件：HAL 抽象层、事件驱动框架与模块化目录结构实战。",
        "difficulty": 3,
        "tags": ["架构", "代码规范", "模块化"],
        "duration_minutes": 14,
        "content": """## 为什么要分层

业务代码直接操作寄存器 = 换颗芯片全部重写。分层的核心目标：**换硬件不动业务，改业务不碰硬件**。

## 推荐四层结构

```
┌──────────────────────────┐
│ Application  业务逻辑      │  app_sensor.c: 状态机、协议
├──────────────────────────┤
│ Service      服务层        │  service_log.c: 日志格式化
├──────────────────────────┤
│ Driver       驱动抽象层    │  drv_temp.c: 统一 read() 接口
├──────────────────────────┤
│ HAL/BSP      芯片相关      │  stm32_i2c.c: 寄存器/HAL 调用
└──────────────────────────┘
```

## 驱动抽象示例

```c
// drv_temp.h —— 上层只认识这个接口
typedef struct {
    int (*read)(float *temp);
    int (*init)(void);
} temp_driver_t;

extern const temp_driver_t drv_sht30;   // I2C 版
extern const temp_driver_t drv_ds18b20; // 单总线版

// app_sensor.c
const temp_driver_t *g_temp = &drv_sht30;  // 换传感器只改这一行
```

**面向接口编程在 MCU 上同样成立**，函数指针就是 C 语言的虚函数表。

## 事件驱动替代轮询

```c
// 事件队列：所有模块通过事件通信，彼此不 include
typedef enum { EVT_KEY, EVT_ADC_READY, EVT_TIMER } evt_type_t;

void main_loop(void) {
    event_t e;
    if (event_pop(&e)) {
        switch (e.type) {
        case EVT_ADC_READY: sensor_on_data(&e); break;
        case EVT_KEY:       ui_on_key(&e);      break;
        }
    }
    low_power_check();   // 队列空可休眠
}
```

**模块间只传事件不互相调用**，单测、替换、加功能都只动一处。

## 目录与规范

```
project/
  app/       业务逻辑
  service/   通用服务（日志/参数存储）
  drivers/   设备驱动
  bsp/       芯片板级支持
  third_party/  FreeRTOS、FatFs
```

规则：**上层可以 include 下层头文件，反向禁止**；每个 .c 配同名 .h；公共宏集中在 config.h。坚持三个月，你会感谢自己的。""",
    },
    {
        "title": "看门狗与系统可靠性：让设备 365 天不宕机",
        "summary": "无人值守设备靠什么自愈？独立看门狗与窗口看门狗的区别、喂狗策略与故障自记录设计。",
        "difficulty": 2,
        "tags": ["可靠性", "看门狗", "故障诊断"],
        "duration_minutes": 10,
        "content": """## 为什么必须有看门狗

无人值守设备（电表、水泵、路灯控制器）一年运行 8760 小时，任何一次死机都是事故。看门狗（Watchdog）的本质：**一个不断倒计时的定时器，程序必须周期性喂狗；一旦程序跑飞没喂狗，超时复位——系统自愈。**

## 两种看门狗

| | 独立看门狗 IWDG | 窗口看门狗 WWDG |
| --- | --- | --- |
| 时钟 | LSI 独立时钟（主时钟挂了也工作） | PCLK 派生 |
| 超时行为 | 喂狗太晚 → 复位 | 喂太早或太晚都复位 |
| 适用 | 防程序跑飞兜底 | 检测程序时序异常 |

**窗口看门狗的精髓**：规定"必须在 30ms~50ms 窗口内喂"，喂早了（主循环卡在其他地方）也算异常——比"只要别太晚"的独立看门狗严格得多。

## 喂狗的正确姿势

### 错误做法：在中断里喂狗

```c
void TIM2_IRQHandler(void) {   // ❌ 反例
    IWDG->KR = 0xAAAA;         // 中断活着 ≠ 主程序活着
}
```

主程序死循环但中断还在跑，看门狗永远被喂，**完全失去保护意义**。

### 正确做法：主循环多点喂狗 + 关键任务确认

```c
// 各模块完成一轮工作后置位
task_flags |= TASK_ADC_OK | TASK_UART_OK | TASK_UI_OK;

void feed_watchdog_if_ok(void) {
    if ((task_flags & TASK_ALL) == TASK_ALL) {
        IWDG->KR = 0xAAAA;              // 全部任务正常才喂
        task_flags = 0;
    }
}
```

**只有所有关键任务都跑完才喂狗**——任何一个模块卡死，系统复位重来。

## 复位后的自诊断

看门狗复位不是"假装没事重新开始"，应该**留下案发现场记录**：

```c
if (RCC->CSR & RCC_CSR_IWDGRSTF) {
    fault_log.count++;                 // 复位原因写入 Flash/EEPROM
    fault_log.last_pc = saved_pc;      // 复位前保存的 PC
    fault_log.last_task = current_task_id;
    RCC->CSR |= RCC_CSR_RMVF;          // 清除复位标志
}
```

**PC 值 + .map 文件 → 定位跑飞地址**；任务 ID → 定位是哪个模块卡死。远程设备还能把故障日志随下一次通信上报，形成完整的现场回溯。

## 可靠性设计的组合拳

1. **看门狗兜底**（必须有，超时时间 = 主循环最长周期的 3~5 倍）
2. **关键参数双区存储 + CRC**：Flash 写入时校验，坏区自动切换
3. **开机自检**：RAM/Flash/传感器通信检查，异常进入安全模式而非带病工作
4. **上电防抖**：电源毛刺引起的复位用电压监控（BOR）拦截
5. **老化测试**：出厂前 48 小时连续运行 + 人为注入故障（阻塞一个任务），验证看门狗真的会咬人

**可靠性不是测出来的，是设计出来的**：假设任何一行代码都可能跑飞，再假设复位之后一切还能继续——带着这两个假设写出来的固件，才配得上"365 天不宕机"。""",
    },
]
