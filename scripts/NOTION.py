from notion_client import Client
from dotenv import load_dotenv
import os

load_dotenv()

# 填入你的資訊（放在 .env 檔）
NOTION_TOKEN    = os.getenv("NOTION_TOKEN")
PARENT_PAGE_ID  = os.getenv("PARENT_PAGE_ID")

notion = Client(auth=NOTION_TOKEN)

# ===== 1. 建立旅程總覽 =====
trips_db = notion.databases.create(
    parent={"type": "page_id", "page_id": PARENT_PAGE_ID},
    title=[{"type": "text", "text": {"content": "🗺️ 旅程總覽"}}],
    properties={
        "旅程名稱": {"title": {}},
        "出發日期": {"date": {}},
        "回程日期": {"date": {}},
        "人數": {"number": {"format": "number"}},
        "總預算(TWD)": {"number": {"format": "number"}},
        "狀態": {
            "select": {
                "options": [
                    {"name": "計畫中", "color": "yellow"},
                    {"name": "確認",   "color": "blue"},
                    {"name": "完成",   "color": "green"},
                ]
            }
        },
    },
)
trips_db_id = trips_db["id"]
print(f"✅ 旅程總覽建立完成！ID: {trips_db_id}")


# ===== 2. 建立每日行程 =====
itinerary_db = notion.databases.create(
    parent={"type": "page_id", "page_id": PARENT_PAGE_ID},
    title=[{"type": "text", "text": {"content": "📅 每日行程"}}],
    properties={
        "景點名稱": {"title": {}},
        "所屬旅程": {
            "relation": {
                "database_id": trips_db_id,
                "single_property": {}
            }
        },
        "日期": {"date": {}},
        "時間": {"rich_text": {}},
        "類型": {
            "select": {
                "options": [
                    {"name": "🏛️ 景點",  "color": "blue"},
                    {"name": "🍽️ 餐廳",  "color": "orange"},
                    {"name": "🚉 交通",  "color": "gray"},
                    {"name": "🏨 住宿",  "color": "purple"},
                    {"name": "🛍️ 購物",  "color": "pink"},
                ]
            }
        },
        "地址": {"rich_text": {}},
        "Google Maps": {"url": {}},
        "預估費用(JPY)": {"number": {"format": "yen"}},
        "備註": {"rich_text": {}},
        "完成": {"checkbox": {}},
    },
)
itinerary_db_id = itinerary_db["id"]
print(f"✅ 每日行程建立完成！ID: {itinerary_db_id}")


# ===== 3. 建立費用記錄 =====
expenses_db = notion.databases.create(
    parent={"type": "page_id", "page_id": PARENT_PAGE_ID},
    title=[{"type": "text", "text": {"content": "💰 費用記錄"}}],
    properties={
        "項目": {"title": {}},
        "所屬旅程": {
            "relation": {
                "database_id": trips_db_id,
                "single_property": {}
            }
        },
        "金額(JPY)": {"number": {"format": "yen"}},
        "類別": {
            "select": {
                "options": [
                    {"name": "🍽️ 餐飲",  "color": "orange"},
                    {"name": "🚉 交通",  "color": "gray"},
                    {"name": "🛍️ 購物",  "color": "pink"},
                    {"name": "🏨 住宿",  "color": "purple"},
                    {"name": "🎟️ 門票",  "color": "blue"},
                    {"name": "📦 其他",  "color": "default"},
                ]
            }
        },
        "日期": {"date": {}},
        "付款人": {"rich_text": {}},
        "備註": {"rich_text": {}},
    },
)
expenses_db_id = expenses_db["id"]
print(f"✅ 費用記錄建立完成！ID: {expenses_db_id}")


# ===== 完成，印出所有 ID =====
print("\n=============================")
print("🎉 全部建立完成！")
print(f"旅程總覽 ID   : {trips_db_id}")
print(f"每日行程 ID   : {itinerary_db_id}")
print(f"費用記錄 ID   : {expenses_db_id}")
print("=============================")
print("把以上三個 ID 提供給我，我來幫你做網頁！")
