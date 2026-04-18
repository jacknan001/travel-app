import sys, io, time, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from notion_client import Client
from dotenv import load_dotenv
load_dotenv()

NOTION_TOKEN    = os.getenv("NOTION_TOKEN")
TRIPS_DB_ID     = os.getenv("TRIPS_DB_ID")
ITINERARY_DB_ID = os.getenv("ITINERARY_DB_ID")
EXPENSES_DB_ID  = os.getenv("EXPENSES_DB_ID")

notion = Client(auth=NOTION_TOKEN)


# ── 1. 建立旅程 ────────────────────────────────────────────────────────────────
trip = notion.pages.create(
    parent={"database_id": TRIPS_DB_ID},
    properties={
        "旅程名稱":     {"title": [{"text": {"content": "福岡男子旅 🍺"}}]},
        "出發日期":     {"date": {"start": "2026-11-15"}},
        "回程日期":     {"date": {"start": "2026-11-19"}},
        "人數":         {"number": 4},
        "總預算(TWD)": {"number": 37000},
        "狀態":         {"select": {"name": "計畫中"}},
    }
)
TRIP_ID = trip["id"]
print(f"✅ 旅程建立完成：{TRIP_ID}")


# ── 2. 行程資料 ────────────────────────────────────────────────────────────────
itinerary = [
    # Day 1
    {"date": "2026-11-15", "time": "16:00", "type": "🚉 交通",  "name": "福岡機場落地",     "notes": "放行李、換錢",               "cost": None},
    {"date": "2026-11-15", "time": "18:00", "type": "🍽️ 餐廳",  "name": "一蘭拉麵 博多店",  "notes": "個人隔間超爽",               "cost": 1500},
    {"date": "2026-11-15", "time": "20:00", "type": "🏛️ 景點",  "name": "中洲屋台街",       "notes": "拉麵串燒邊走邊吃",           "cost": 3000},
    {"date": "2026-11-15", "time": "22:00", "type": "🏛️ 景點",  "name": "中洲酒吧街",       "notes": "福岡最熱鬧夜生活",           "cost": 3000},
    # Day 2
    {"date": "2026-11-16", "time": "09:00", "type": "🚉 交通",  "name": "博多 → 太宰府",    "notes": "西鐵電車約40分",             "cost": None},
    {"date": "2026-11-16", "time": "10:00", "type": "🏛️ 景點",  "name": "太宰府天滿宮",     "notes": "楓葉紅遍境內",               "cost": 0},
    {"date": "2026-11-16", "time": "10:30", "type": "🍽️ 餐廳",  "name": "梅枝餅",           "notes": "参道必吃名物",               "cost": 300},
    {"date": "2026-11-16", "time": "14:00", "type": "🏛️ 景點",  "name": "Round 1 博多",     "notes": "柏青哥夾娃娃保齡球",         "cost": 2000},
    {"date": "2026-11-16", "time": "19:00", "type": "🍽️ 餐廳",  "name": "博多焼肉 牛乃",    "notes": "九州黑毛和牛",               "cost": 8000},
    # Day 3
    {"date": "2026-11-17", "time": "09:00", "type": "🚉 交通",  "name": "博多 → 糸島",      "notes": "JR筑肥線約40分",             "cost": 800},
    {"date": "2026-11-17", "time": "12:00", "type": "🍽️ 餐廳",  "name": "糸島牡蠣小屋",     "notes": "11月產季現烤配啤酒",         "cost": 5000},
    {"date": "2026-11-17", "time": "14:00", "type": "🏛️ 景點",  "name": "二見ヶ浦 夫婦岩",  "notes": "海景打卡",                   "cost": 0},
    {"date": "2026-11-17", "time": "15:30", "type": "🏛️ 景點",  "name": "糸島海邊咖啡廳",   "notes": "放空",                       "cost": 1000},
    {"date": "2026-11-17", "time": "18:00", "type": "🍽️ 餐廳",  "name": "長濱鮮魚市場",     "notes": "超新鮮海產配啤酒",           "cost": 4000},
    # Day 4
    {"date": "2026-11-18", "time": "09:00", "type": "🚉 交通",  "name": "博多 → 柳川",      "notes": "西鐵電車約1小時",            "cost": 1500},
    {"date": "2026-11-18", "time": "10:00", "type": "🏛️ 景點",  "name": "柳川遊船",         "notes": "楓葉倒映水道絕景",           "cost": 2000},
    {"date": "2026-11-18", "time": "12:00", "type": "🍽️ 餐廳",  "name": "柳川鰻魚蒸飯",     "notes": "當地名物必吃",               "cost": 3500},
    {"date": "2026-11-18", "time": "14:00", "type": "🚉 交通",  "name": "柳川 → 鳥栖",      "notes": "約40分",                     "cost": 800},
    {"date": "2026-11-18", "time": "15:00", "type": "🛍️ 購物",  "name": "鳥栖 Premium Outlets", "notes": "Nike Adidas Coach 170+品牌", "cost": 20000},
    {"date": "2026-11-18", "time": "19:00", "type": "🍽️ 餐廳",  "name": "水炊き 博多",      "notes": "雞白湯火鍋",                 "cost": 6000},
    # Day 5
    {"date": "2026-11-19", "time": "08:00", "type": "🍽️ 餐廳",  "name": "博多拉麵當早餐",   "notes": "福岡人真的這樣做",           "cost": 1000},
    {"date": "2026-11-19", "time": "10:00", "type": "🛍️ 購物",  "name": "Canal City 博多",  "notes": "伴手禮掃貨",                 "cost": 5000},
    {"date": "2026-11-19", "time": "14:00", "type": "🚉 交通",  "name": "福岡機場 回台灣",   "notes": "返程",                       "cost": None},
]

for item in itinerary:
    props = {
        "景點名稱": {"title": [{"text": {"content": item["name"]}}]},
        "所屬旅程": {"relation": [{"id": TRIP_ID}]},
        "日期":     {"date": {"start": item["date"]}},
        "時間":     {"rich_text": [{"text": {"content": item["time"]}}]},
        "類型":     {"select": {"name": item["type"]}},
        "備註":     {"rich_text": [{"text": {"content": item["notes"]}}]},
        "完成":     {"checkbox": False},
    }
    if item["cost"] is not None:
        props["預估費用(JPY)"] = {"number": item["cost"]}

    notion.pages.create(parent={"database_id": ITINERARY_DB_ID}, properties=props)
    print(f"  📍 {item['date']} {item['time']} {item['name']}")
    time.sleep(0.3)  # 避免 API rate limit

print("✅ 所有行程建立完成")


# ── 3. 費用記錄（預算分類） ────────────────────────────────────────────────────
# 注意：這裡用 TWD 換算 JPY（1 TWD ≈ 4.5 JPY）
expenses = [
    {"name": "機票（來回）", "category": "🚉 交通",  "date": "2026-11-15", "amount_jpy": 58500,  "notes": "13,000 TWD"},
    {"name": "住宿 4晚",    "category": "🏨 住宿",   "date": "2026-11-15", "amount_jpy": 45000,  "notes": "10,000 TWD"},
    {"name": "當地交通",    "category": "🚉 交通",  "date": "2026-11-15", "amount_jpy": 13500,  "notes": "3,000 TWD"},
    {"name": "餐飲總計",    "category": "🍽️ 餐飲",  "date": "2026-11-15", "amount_jpy": 40500,  "notes": "9,000 TWD"},
    {"name": "購物/娛樂",   "category": "🛍️ 購物",  "date": "2026-11-15", "amount_jpy": 22500,  "notes": "5,000 TWD"},
]

for exp in expenses:
    notion.pages.create(
        parent={"database_id": EXPENSES_DB_ID},
        properties={
            "項目":      {"title": [{"text": {"content": exp["name"]}}]},
            "所屬旅程":  {"relation": [{"id": TRIP_ID}]},
            "金額(JPY)": {"number": exp["amount_jpy"]},
            "類別":      {"select": {"name": exp["category"]}},
            "日期":      {"date": {"start": exp["date"]}},
            "備註":      {"rich_text": [{"text": {"content": exp["notes"]}}]},
        }
    )
    print(f"  💰 {exp['name']}")
    time.sleep(0.3)

print("✅ 費用記錄建立完成")
print("\n🎉 福岡男子旅 資料全部寫入 Notion！")
