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

import json

db = notion.databases.retrieve(database_id=TRIPS_DB_ID)
print("=== 旅程總覽 原始回應 (前 2000 字) ===")
print(json.dumps(db, ensure_ascii=False, indent=2)[:2000])
