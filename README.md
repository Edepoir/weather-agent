# Weather Agent - AI 天气助手

> 软件产品综合开发实践 - 实验二：Bring Your Own Agent (BYOA)

一个基于大语言模型的智能天气助手 Agent，支持查询实时天气和当前时间。

## 功能特性

- **查询当前时间**：获取本地系统时间
- **查询实时天气**：支持国内外 70+ 城市，自动地理编码查询任意城市
- **意图识别**：手动关键词匹配，准确识别用户查询意图
- **工具调用**：集成 Open-Meteo 免费天气 API

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.8+ |
| LLM API | 硅基流动 (SiliconFlow) - Qwen2.5-7B-Instruct |
| 天气 API | Open-Meteo (免费，无需 API Key) |
| 地理编码 | Open-Meteo Geocoding API |
| HTTP 客户端 | httpx |
| 环境变量 | python-dotenv |

## 项目结构

```
weather-agent/
├── agent.py          # Agent 主程序（意图识别 + 工具调用 + 格式化输出）
├── .env              # 环境变量（API Key，不提交到 Git）
├── .gitignore        # Git 忽略文件
└── README.md         # 项目说明
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Edepoir/weather-agent.git
cd weather-agent
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install openai python-dotenv httpx
```

### 4. 配置 API Key

创建 `.env` 文件，填入你的硅基流动 API Key：

```bash
SILICONFLOW_API_KEY=sk-your-api-key-here
```

> 获取 API Key：[硅基流动](https://cloud.siliconflow.cn)

### 5. 运行 Agent

```bash
python agent.py
```

## 使用示例

```
==================================================
[天气] 天气助手 Agent 已启动！
==================================================
支持功能：
  - 查询天气："北京天气怎么样？"
  - 查询时间："现在几点了？"
  - 支持国内外任意城市（自动地理编码）
  - 输入 quit / exit / q 退出
==================================================

[用户] 现在几点了？
[Agent] 思考中...
[工具] get_current_time()
[结果] 当前时间：2026年06月20日 22:18:35
[Agent]
[时间] 当前时间
[日期] 2026年06月20日
[时钟] 22时18分35秒

[用户] 北京天气怎么样
[Agent] 思考中...
[工具] get_weather(city=北京)
[结果] 北京: 22.9°C, [晴]晴朗
[Agent]
[天气] 北京
[晴]晴朗
[温度] 22.9°C
[湿度] 39%
[风速] 9.6 km/h

[用户] 驻马店天气
[Agent] 思考中...
[工具] get_weather(city=驻马店)
[结果] 驻马店: 23.7°C, [云]阴天
[Agent]
[天气] 驻马店
[云]阴天
[温度] 23.7°C
[湿度] 82%
[风速] 5.8 km/h
```

## 架构设计

```
用户输入
  ↓
意图识别（手动关键词匹配）
  ↓
工具选择
  ├─ 时间查询 → get_current_time() → 本地系统时间
  └─ 天气查询 → get_weather(city) → Open-Meteo API
  ↓
程序格式化输出（100% 准确，不经过 LLM 复述）
  ↓
自然语言回复
```

## 核心设计决策

**为什么不用 LLM 复述工具结果？**

在实验过程中发现，小模型（Qwen2.5-7B）在复述准确数据时频繁产生幻觉：
- 工具返回 `2026年06月20日 21:20:21`，LLM 回复变成 `2226年06月22日`
- 工具返回温度 `22.9°C`，LLM 回复变成 `6.5°C`

**解决方案**：将 LLM 的角色从"决策者+复述者"改为仅做"意图识别"，工具调用和数据格式化全部由程序完成。这样既保证了数据 100% 准确，又满足了 Agent 的核心架构要求。

## 实验反思

### 遇到的技术问题

1. **模型不可用**：硅基流动的 `DeepSeek-V2.5` 模型被禁用，切换为 `Qwen/Qwen2.5-7B-Instruct`
2. **Function Calling 兼容性问题**：Qwen2.5-7B 对 OpenAI function calling 格式支持不佳，模型输出格式混乱
3. **LLM 幻觉问题**：模型在复述工具返回的准确数据时频繁篡改数字
4. **编码问题**：Windows CMD 默认 GBK 编码不支持 emoji，需设置 UTF-8

### 解决方法

- 放弃 function calling，改用**手动意图识别 + 程序直接调用工具**
- 工具结果由**程序格式化输出**，不经过 LLM 复述，确保数据准确性
- 在代码开头添加 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` 解决编码问题

## 评分项对应

| 评分项 | 实现 |
|--------|------|
| **工具使用 / Skills** (≥2个) | `get_current_time` (本地时间) + `get_weather` (Open-Meteo API) |
| **上下文集成** | System Prompt 定义角色规则 + 工具结果注入 |
| **Vibe Coding** | 使用 AI 辅助生成代码框架，人工调整架构和提示词 |

## License

MIT

---

> 软件产品综合开发实践 - 实验二
