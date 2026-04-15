from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from notion_client import Client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

NOTION_TOKEN    = os.getenv("NOTION_TOKEN")
TRIPS_DB_ID     = os.getenv("TRIPS_DB_ID")
ITINERARY_DB_ID = os.getenv("ITINERARY_DB_ID")
EXPENSES_DB_ID  = os.getenv("EXPENSES_DB_ID")

notion = Client(auth=NOTION_TOKEN)


# ── helpers ──────────────────────────────────────────────────────────────────

def rich_text_value(prop):
    items = prop.get("rich_text", [])
    return items[0]["plain_text"] if items else ""

def title_value(prop):
    items = prop.get("title", [])
    return items[0]["plain_text"] if items else ""

def date_value(prop):
    d = prop.get("date")
    return d["start"] if d else None

def select_value(prop):
    s = prop.get("select")
    return s["name"] if s else None

def number_value(prop):
    return prop.get("number")

def url_value(prop):
    return prop.get("url")

def checkbox_value(prop):
    return prop.get("checkbox", False)

def relation_ids(prop):
    return [r["id"] for r in prop.get("relation", [])]


def parse_trip(page):
    p = page["properties"]
    return {
        "id": page["id"],
        "name": title_value(p.get("旅程名稱", {})),
        "start_date": date_value(p.get("出發日期", {})),
        "end_date": date_value(p.get("回程日期", {})),
        "people": number_value(p.get("人數", {})),
        "budget_twd": number_value(p.get("總預算(TWD)", {})),
        "status": select_value(p.get("狀態", {})),
    }


def parse_itinerary(page):
    p = page["properties"]
    return {
        "id": page["id"],
        "name": title_value(p.get("景點名稱", {})),
        "trip_ids": relation_ids(p.get("所屬旅程", {})),
        "date": date_value(p.get("日期", {})),
        "time": rich_text_value(p.get("時間", {})),
        "type": select_value(p.get("類型", {})),
        "address": rich_text_value(p.get("地址", {})),
        "maps_url": url_value(p.get("Google Maps", {})),
        "cost_jpy": number_value(p.get("預估費用(JPY)", {})),
        "notes": rich_text_value(p.get("備註", {})),
        "done": checkbox_value(p.get("完成", {})),
    }


def parse_expense(page):
    p = page["properties"]
    return {
        "id": page["id"],
        "name": title_value(p.get("項目", {})),
        "trip_ids": relation_ids(p.get("所屬旅程", {})),
        "amount_jpy": number_value(p.get("金額(JPY)", {})),
        "category": select_value(p.get("類別", {})),
        "date": date_value(p.get("日期", {})),
        "payer": rich_text_value(p.get("付款人", {})),
        "notes": rich_text_value(p.get("備註", {})),
    }


def paginate_query(fn, **kwargs):
    results = []
    cursor = None
    while True:
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = fn(**kwargs)
        results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return results


# ── routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# TRIPS -----------------------------------------------------------------------

@app.route("/api/trips", methods=["GET"])
def get_trips():
    pages = paginate_query(
        notion.databases.query,
        database_id=TRIPS_DB_ID,
        sorts=[{"property": "出發日期", "direction": "descending"}],
    )
    return jsonify([parse_trip(p) for p in pages])


@app.route("/api/trips", methods=["POST"])
def create_trip():
    data = request.get_json()
    properties = {
        "旅程名稱": {"title": [{"text": {"content": data.get("name", "")}}]},
    }
    if data.get("start_date"):
        properties["出發日期"] = {"date": {"start": data["start_date"]}}
    if data.get("end_date"):
        properties["回程日期"] = {"date": {"start": data["end_date"]}}
    if data.get("people") is not None:
        properties["人數"] = {"number": data["people"]}
    if data.get("budget_twd") is not None:
        properties["總預算(TWD)"] = {"number": data["budget_twd"]}
    if data.get("status"):
        properties["狀態"] = {"select": {"name": data["status"]}}

    page = notion.pages.create(
        parent={"database_id": TRIPS_DB_ID},
        properties=properties,
    )
    return jsonify(parse_trip(page)), 201


# ITINERARY -------------------------------------------------------------------

@app.route("/api/itinerary/<trip_id>", methods=["GET"])
def get_itinerary(trip_id):
    pages = paginate_query(
        notion.databases.query,
        database_id=ITINERARY_DB_ID,
        filter={"property": "所屬旅程", "relation": {"contains": trip_id}},
        sorts=[
            {"property": "日期", "direction": "ascending"},
            {"property": "時間", "direction": "ascending"},
        ],
    )
    return jsonify([parse_itinerary(p) for p in pages])


@app.route("/api/itinerary", methods=["POST"])
def create_itinerary():
    data = request.get_json()
    properties = {
        "景點名稱": {"title": [{"text": {"content": data.get("name", "")}}]},
    }
    if data.get("trip_id"):
        properties["所屬旅程"] = {"relation": [{"id": data["trip_id"]}]}
    if data.get("date"):
        properties["日期"] = {"date": {"start": data["date"]}}
    if data.get("time"):
        properties["時間"] = {"rich_text": [{"text": {"content": data["time"]}}]}
    if data.get("type"):
        properties["類型"] = {"select": {"name": data["type"]}}
    if data.get("address"):
        properties["地址"] = {"rich_text": [{"text": {"content": data["address"]}}]}
    if data.get("maps_url"):
        properties["Google Maps"] = {"url": data["maps_url"]}
    if data.get("cost_jpy") is not None:
        properties["預估費用(JPY)"] = {"number": data["cost_jpy"]}
    if data.get("notes"):
        properties["備註"] = {"rich_text": [{"text": {"content": data["notes"]}}]}
    if data.get("done") is not None:
        properties["完成"] = {"checkbox": data["done"]}

    page = notion.pages.create(
        parent={"database_id": ITINERARY_DB_ID},
        properties=properties,
    )
    return jsonify(parse_itinerary(page)), 201


@app.route("/api/itinerary/<item_id>", methods=["PUT"])
def update_itinerary(item_id):
    data = request.get_json()
    properties = {}

    if "name" in data:
        properties["景點名稱"] = {"title": [{"text": {"content": data["name"]}}]}
    if "trip_id" in data:
        properties["所屬旅程"] = {"relation": [{"id": data["trip_id"]}]}
    if "date" in data:
        properties["日期"] = {"date": {"start": data["date"]}} if data["date"] else {"date": None}
    if "time" in data:
        properties["時間"] = {"rich_text": [{"text": {"content": data["time"]}}]}
    if "type" in data:
        properties["類型"] = {"select": {"name": data["type"]}} if data["type"] else {"select": None}
    if "address" in data:
        properties["地址"] = {"rich_text": [{"text": {"content": data["address"]}}]}
    if "maps_url" in data:
        properties["Google Maps"] = {"url": data["maps_url"] or None}
    if "cost_jpy" in data:
        properties["預估費用(JPY)"] = {"number": data["cost_jpy"]}
    if "notes" in data:
        properties["備註"] = {"rich_text": [{"text": {"content": data["notes"]}}]}
    if "done" in data:
        properties["完成"] = {"checkbox": bool(data["done"])}

    page = notion.pages.update(page_id=item_id, properties=properties)
    return jsonify(parse_itinerary(page))


@app.route("/api/itinerary/<item_id>", methods=["DELETE"])
def delete_itinerary(item_id):
    # Soft delete: archive the page
    notion.pages.update(page_id=item_id, archived=True)
    return jsonify({"success": True})


# EXPENSES --------------------------------------------------------------------

@app.route("/api/expenses/<trip_id>", methods=["GET"])
def get_expenses(trip_id):
    pages = paginate_query(
        notion.databases.query,
        database_id=EXPENSES_DB_ID,
        filter={"property": "所屬旅程", "relation": {"contains": trip_id}},
        sorts=[{"property": "日期", "direction": "ascending"}],
    )
    return jsonify([parse_expense(p) for p in pages])


@app.route("/api/expenses", methods=["POST"])
def create_expense():
    data = request.get_json()
    properties = {
        "項目": {"title": [{"text": {"content": data.get("name", "")}}]},
    }
    if data.get("trip_id"):
        properties["所屬旅程"] = {"relation": [{"id": data["trip_id"]}]}
    if data.get("amount_jpy") is not None:
        properties["金額(JPY)"] = {"number": data["amount_jpy"]}
    if data.get("category"):
        properties["類別"] = {"select": {"name": data["category"]}}
    if data.get("date"):
        properties["日期"] = {"date": {"start": data["date"]}}
    if data.get("payer"):
        properties["付款人"] = {"rich_text": [{"text": {"content": data["payer"]}}]}
    if data.get("notes"):
        properties["備註"] = {"rich_text": [{"text": {"content": data["notes"]}}]}

    page = notion.pages.create(
        parent={"database_id": EXPENSES_DB_ID},
        properties=properties,
    )
    return jsonify(parse_expense(page)), 201


@app.route("/api/expenses/<item_id>", methods=["PUT"])
def update_expense(item_id):
    data = request.get_json()
    properties = {}
    if "name" in data:
        properties["項目"] = {"title": [{"text": {"content": data["name"]}}]}
    if "trip_id" in data:
        properties["所屬旅程"] = {"relation": [{"id": data["trip_id"]}]}
    if "amount_jpy" in data:
        properties["金額(JPY)"] = {"number": data["amount_jpy"]}
    if "category" in data:
        properties["類別"] = {"select": {"name": data["category"]}} if data["category"] else {"select": None}
    if "date" in data:
        properties["日期"] = {"date": {"start": data["date"]}} if data["date"] else {"date": None}
    if "payer" in data:
        properties["付款人"] = {"rich_text": [{"text": {"content": data["payer"]}}]}
    if "notes" in data:
        properties["備註"] = {"rich_text": [{"text": {"content": data["notes"]}}]}
    page = notion.pages.update(page_id=item_id, properties=properties)
    return jsonify(parse_expense(page))


@app.route("/api/expenses/<item_id>", methods=["DELETE"])
def delete_expense(item_id):
    notion.pages.update(page_id=item_id, archived=True)
    return jsonify({"success": True})


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
