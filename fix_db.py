import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from notion_client import Client
from dotenv import load_dotenv
load_dotenv()

NOTION_TOKEN    = os.getenv("NOTION_TOKEN")
TRIPS_DB_ID     = os.getenv("TRIPS_DB_ID")
ITINERARY_DB_ID = os.getenv("ITINERARY_DB_ID")
EXPENSES_DB_ID  = os.getenv("EXPENSES_DB_ID")

notion = Client(auth=NOTION_TOKEN)


def find_title_prop(db_id):
    """找出資料庫現有的 title 欄位名稱"""
    db = notion.databases.retrieve(database_id=db_id)
    for name, val in db.get("properties", {}).items():
        if val.get("type") == "title":
            return name
    return "Name"  # Notion 預設


# ===== 修復 旅程總覽 =====
title = find_title_prop(TRIPS_DB_ID)
notion.databases.update(
    database_id=TRIPS_DB_ID,
    properties={
        title:          {"name": "旅程名稱"},   # 重新命名現有 title
        "出發日期":      {"date": {}},
        "回程日期":      {"date": {}},
        "人數":          {"number": {"format": "number"}},
        "總預算(TWD)":   {"number": {"format": "number"}},
        "狀態": {
            "select": {
                "options": [
                    {"name": "計畫中", "color": "yellow"},
                    {"name": "確認",   "color": "blue"},
                    {"name": "完成",   "color": "green"},
                ]
            }
        },
    }
)
print("✅ 旅程總覽 欄位補齊")

# ===== 修復 每日行程 =====
title = find_title_prop(ITINERARY_DB_ID)
notion.databases.update(
    database_id=ITINERARY_DB_ID,
    properties={
        title:          {"name": "景點名稱"},
        "所屬旅程":      {"relation": {"database_id": TRIPS_DB_ID, "single_property": {}}},
        "日期":          {"date": {}},
        "時間":          {"rich_text": {}},
        "類型": {
            "select": {
                "options": [
                    {"name": "🏛️ 景點", "color": "blue"},
                    {"name": "🍽️ 餐廳", "color": "orange"},
                    {"name": "🚉 交通", "color": "gray"},
                    {"name": "🏨 住宿", "color": "purple"},
                    {"name": "🛍️ 購物", "color": "pink"},
                ]
            }
        },
        "地址":          {"rich_text": {}},
        "Google Maps":   {"url": {}},
        "預估費用(JPY)":  {"number": {"format": "yen"}},
        "備註":          {"rich_text": {}},
        "完成":          {"checkbox": {}},
    }
)
print("✅ 每日行程 欄位補齊")

# ===== 修復 費用記錄 =====
title = find_title_prop(EXPENSES_DB_ID)
notion.databases.update(
    database_id=EXPENSES_DB_ID,
    properties={
        title:          {"name": "項目"},
        "所屬旅程":      {"relation": {"database_id": TRIPS_DB_ID, "single_property": {}}},
        "金額(JPY)":     {"number": {"format": "yen"}},
        "類別": {
            "select": {
                "options": [
                    {"name": "🍽️ 餐飲", "color": "orange"},
                    {"name": "🚉 交通", "color": "gray"},
                    {"name": "🛍️ 購物", "color": "pink"},
                    {"name": "🏨 住宿", "color": "purple"},
                    {"name": "🎟️ 門票", "color": "blue"},
                    {"name": "📦 其他", "color": "default"},
                ]
            }
        },
        "日期":          {"date": {}},
        "付款人":        {"rich_text": {}},
        "備註":          {"rich_text": {}},
    }
)
print("✅ 費用記錄 欄位補齊")
print("\n🎉 全部修復完成！現在可以執行 travel_app.py 了")
