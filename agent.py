# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import os
import asyncio
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv
import httpx

# 加载环境变量
load_dotenv()

# 初始化客户端（硅基流动）
client = AsyncOpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

# ========== 工具函数 ==========

def get_current_time():
    """获取当前系统时间"""
    now = datetime.now()
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "full": now.strftime("%Y年%m月%d日 %H:%M:%S")
    }

def get_weather(city: str):
    """获取指定城市天气（自动查询坐标）"""

    # 先尝试本地映射（常用城市，减少 API 调用）
    city_coords = {
        "北京": (39.9042, 116.4074),
        "上海": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "深圳": (22.5431, 114.0579),
        "成都": (30.5728, 104.0668),
        "杭州": (30.2741, 120.1551),
        "武汉": (30.5928, 114.3055),
        "西安": (34.3416, 108.9398),
        "驻马店": (32.9802, 114.0253),
        "郑州": (34.7466, 113.6253),
        "南京": (32.0603, 118.7969),
        "重庆": (29.5630, 106.5516),
        "天津": (39.0842, 117.2010),
        "苏州": (31.2989, 120.5853),
        "长沙": (28.2282, 112.9388),
        "青岛": (36.0671, 120.3826),
        "厦门": (24.4798, 118.0894),
        "昆明": (25.0389, 102.7183),
        "大连": (38.9140, 121.6147),
        "宁波": (29.8683, 121.5440),
        "沈阳": (41.8057, 123.4315),
        "哈尔滨": (45.8038, 126.5350),
        "济南": (36.6512, 117.1201),
        "福州": (26.0745, 119.2965),
        "合肥": (31.8206, 117.2272),
        "南昌": (28.6820, 115.8579),
        "石家庄": (38.0428, 114.5149),
        "太原": (37.8706, 112.5489),
        "长春": (43.8171, 125.3235),
        "南宁": (22.8170, 108.3665),
        "贵阳": (26.6470, 106.6302),
        "兰州": (36.0611, 103.8343),
        "海口": (20.0440, 110.1999),
        "乌鲁木齐": (43.8256, 87.6168),
        "拉萨": (29.6500, 91.1000),
        "银川": (38.4872, 106.2309),
        "西宁": (36.6171, 101.7782),
        "呼和浩特": (40.8414, 111.7519),
        "香港": (22.3193, 114.1694),
        "澳门": (22.1987, 113.5439),
        "台北": (25.0330, 121.5654),
        "东京": (35.6762, 139.6503),
        "纽约": (40.7128, -74.0060),
        "伦敦": (51.5074, -0.1278),
        "巴黎": (48.8566, 2.3522),
        "悉尼": (-33.8688, 151.2093),
        "莫斯科": (55.7558, 37.6173),
        "新加坡": (1.3521, 103.8198),
        "曼谷": (13.7563, 100.5018),
        "首尔": (37.5665, 126.9780),
        "迪拜": (25.2048, 55.2708),
        "孟买": (19.0760, 72.8777),
        "开罗": (30.0444, 31.2357),
        "伊斯坦布尔": (41.0082, 28.9784),
        "多伦多": (43.6532, -79.3832),
        "温哥华": (49.2827, -123.1207),
        "洛杉矶": (34.0522, -118.2437),
        "旧金山": (37.7749, -122.4194),
        "芝加哥": (41.8781, -87.6298),
        "墨尔本": (-37.8136, 144.9631),
        "柏林": (52.5200, 13.4050),
        "罗马": (41.9028, 12.4964),
        "马德里": (40.4168, -3.7038),
        "阿姆斯特丹": (52.3676, 4.9041),
        "维也纳": (48.2082, 16.3738),
        "苏黎世": (47.3769, 8.5417),
    }

    city_key = city.lower().strip()
    coords = None
    display_city = city

    # 先查本地映射
    for key, value in city_coords.items():
        if city_key in key.lower() or key.lower() in city_key:
            coords = value
            display_city = key
            break

    # 本地找不到，调用地理编码 API 查询
    if not coords:
        try:
            geo_resp = httpx.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "zh"},
                timeout=10.0
            )
            geo_data = geo_resp.json()

            if "results" in geo_data and geo_data["results"]:
                result = geo_data["results"][0]
                coords = (result["latitude"], result["longitude"])
                display_city = result.get("name", city)
                print(f"🌍 [地理编码] {city} → {display_city} ({coords[0]:.2f}, {coords[1]:.2f})")
            else:
                print(f"⚠️ 未找到城市：{city}，使用默认北京")
                coords = (39.9042, 116.4074)
                display_city = f"{city}（未找到，默认北京）"
        except Exception as e:
            print(f"⚠️ 地理编码失败：{e}，使用默认北京")
            coords = (39.9042, 116.4074)
            display_city = f"{city}（查询失败，默认北京）"

    # 获取天气
    try:
        response = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": coords[0],
                "longitude": coords[1],
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "auto"
            },
            timeout=10.0
        )
        data = response.json()
        current = data["current"]

        weather_codes = {
            0: "☀️ 晴朗", 1: "🌤️ 主要晴朗", 2: "⛅ 部分多云", 3: "☁️ 阴天",
            45: "🌫️ 雾", 48: "🌫️ 雾凇", 51: "🌦️ 毛毛雨", 53: "🌦️ 中度毛毛雨",
            55: "🌦️ 密集毛毛雨", 56: "🌦️ 冻毛毛雨", 57: "🌦️ 密集冻毛毛雨",
            61: "🌧️ 小雨", 63: "🌧️ 中雨", 65: "🌧️ 大雨", 
            66: "🌧️ 冻雨", 67: "🌧️ 大冻雨",
            71: "🌨️ 小雪", 73: "🌨️ 中雪", 75: "🌨️ 大雪", 77: "🌨️ 雪粒",
            80: "🌦️ 阵雨", 81: "🌦️ 中度阵雨", 82: "🌦️ 大阵雨",
            85: "🌨️ 阵雪", 86: "🌨️ 大阵雪",
            95: "⛈️ 雷雨", 96: "⛈️ 雷雨伴冰雹", 99: "⛈️ 大雷雨伴冰雹"
        }

        return {
            "city": display_city,
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "weather": weather_codes.get(current["weather_code"], "未知"),
            "wind_speed": current["wind_speed_10m"]
        }
    except Exception as e:
        return {"error": str(e)}

# ========== 意图识别 ==========

def detect_intent(user_input: str):
    """手动识别用户意图和提取参数"""
    text = user_input.lower().strip()

    # 时间相关
    time_keywords = ["几点", "时间", "现在", "几点了", "当前时间", "什么时候", "何时", "几点钟"]
    if any(kw in text for kw in time_keywords):
        return "time", None

    # 天气相关
    weather_keywords = ["天气", "气温", "温度", "下雨", "下雪", "多云", "晴天", "forecast", "weather", "forecast"]
    if any(kw in text for kw in weather_keywords):
        # 尝试提取城市名（支持中英文）
        import re
        # 匹配「城市名+天气」或「天气+城市名」
        # 简单做法：找常见城市名
        cities = [
            "北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "西安", "驻马店", "郑州",
            "南京", "重庆", "天津", "苏州", "长沙", "青岛", "厦门", "昆明", "大连", "宁波",
            "沈阳", "哈尔滨", "济南", "福州", "合肥", "南昌", "石家庄", "太原", "长春", "南宁",
            "贵阳", "兰州", "海口", "乌鲁木齐", "拉萨", "银川", "西宁", "呼和浩特", "香港", "澳门", "台北",
            "东京", "纽约", "伦敦", "巴黎", "悉尼", "莫斯科", "新加坡", "曼谷", "首尔", "迪拜",
            "孟买", "开罗", "伊斯坦布尔", "多伦多", "温哥华", "洛杉矶", "旧金山", "芝加哥",
            "墨尔本", "柏林", "罗马", "马德里", "阿姆斯特丹", "维也纳", "苏黎世",
            "beijing", "shanghai", "guangzhou", "shenzhen", "tokyo", "new york", "london",
            "paris", "sydney", "moscow", "singapore", "bangkok", "seoul", "dubai",
            "mumbai", "cairo", "istanbul", "toronto", "vancouver", "los angeles",
            "san francisco", "chicago", "melbourne", "berlin", "rome", "madrid",
            "amsterdam", "vienna", "zurich"
        ]

        for city in cities:
            if city.lower() in text:
                return "weather", city

        # 如果没找到城市，尝试提取任意中文字符作为城市
        chinese_chars = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        for chars in chinese_chars:
            if chars not in ["天气", "气温", "温度", "怎么样", "如何"]:
                return "weather", chars

        # 默认北京
        return "weather", "北京"

    return "unknown", None

# ========== 格式化输出 ==========

def format_time_result(data: dict) -> str:
    """格式化时间输出"""
    return (
        f"⏰ 当前时间\n"
        f"📅 {data['year']}年{data['month']}月{data['day']}日\n"
        f"🕐 {data['hour']}时{data['minute']}分{data['second']}秒"
    )

def format_weather_result(data: dict) -> str:
    """格式化天气输出"""
    if "error" in data:
        return f"❌ 获取天气失败：{data['error']}"

    return (
        f"🌤️ {data['city']}天气\n"
        f"{data['weather']}\n"
        f"🌡️ 温度：{data['temperature']}°C\n"
        f"💧 湿度：{data['humidity']}%\n"
        f"💨 风速：{data['wind_speed']} km/h"
    )

# ========== Agent 核心逻辑 ==========

async def run_agent(user_input: str):
    intent, param = detect_intent(user_input)

    if intent == "time":
        print("🔧 [调用工具] get_current_time()")
        result = get_current_time()
        print(f"📊 [工具结果] {result['full']}")
        reply = format_time_result(result)

    elif intent == "weather":
        print(f"🔧 [调用工具] get_weather(city={param})")
        result = get_weather(param)
        if "error" in result:
            print(f"📊 [工具结果] 错误：{result['error']}")
        else:
            print(f"📊 [工具结果] {result['city']}: {result['temperature']}°C, {result['weather']}")
        reply = format_weather_result(result)

    else:
        reply = (
            "抱歉，我只能帮你查询天气和时间 ⏰🌤️\n\n"
            "你可以这样问我：\n"
            "  • 「现在几点了？」\n"
            "  • 「北京天气怎么样？」\n"
            "  • 「上海今天温度多少？」\n"
            "  • 「伦敦天气如何？」"
        )

    return reply

# ========== 交互循环 ==========

async def main():
    print("=" * 50)
    print("🌤️  天气助手 Agent 已启动！")
    print("=" * 50)
    print("支持功能：")
    print("  • 查询天气：「北京天气怎么样？」")
    print("  • 查询时间：「现在几点了？」")
    print("  • 支持国内外任意城市（自动地理编码）")
    print("  • 输入 quit / exit / q 退出")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("👤 你：").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 再见！")
                break

            print("🤖 Agent 思考中...")
            reply = await run_agent(user_input)
            print(f"🤖 Agent：\n{reply}\n")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 出错了：{e}\n")

if __name__ == "__main__":
    asyncio.run(main())