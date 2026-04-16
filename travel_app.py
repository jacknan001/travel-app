from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import os
import json as _json

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

NOTION_TOKEN         = os.getenv("NOTION_TOKEN")
TRIPS_DB_ID          = os.getenv("TRIPS_DB_ID")
ITINERARY_DB_ID      = os.getenv("ITINERARY_DB_ID")
EXPENSES_DB_ID       = os.getenv("EXPENSES_DB_ID")
GOOGLE_MAPS_API_KEY  = os.getenv("GOOGLE_MAPS_API_KEY", "")

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

@app.route("/style.css")
def serve_css():
    return send_from_directory(".", "style.css", mimetype="text/css")


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


@app.route("/api/trips/<trip_id>", methods=["PUT"])
def update_trip(trip_id):
    data = request.get_json()
    properties = {}
    if "name" in data:
        properties["旅程名稱"] = {"title": [{"text": {"content": data["name"]}}]}
    if "start_date" in data:
        properties["出發日期"] = {"date": {"start": data["start_date"]}} if data["start_date"] else {"date": None}
    if "end_date" in data:
        properties["回程日期"] = {"date": {"start": data["end_date"]}} if data["end_date"] else {"date": None}
    if "people" in data:
        properties["人數"] = {"number": data["people"]}
    if "budget_twd" in data:
        properties["總預算(TWD)"] = {"number": data["budget_twd"]}
    if "status" in data:
        properties["狀態"] = {"select": {"name": data["status"]}} if data["status"] else {"select": None}

    page = notion.pages.update(page_id=trip_id, properties=properties)
    return jsonify(parse_trip(page))


@app.route("/api/trips/<trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    notion.pages.update(page_id=trip_id, archived=True)
    return jsonify({"success": True})


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


# CONFIG ----------------------------------------------------------------------

@app.route("/api/config")
def get_config():
    return jsonify({"maps_key": GOOGLE_MAPS_API_KEY or ""})


# TRANSIT ---------------------------------------------------------------------

JST = timezone(timedelta(hours=9))

@app.route("/api/transit", methods=["GET"])
def get_transit():
    if not GOOGLE_MAPS_API_KEY:
        return jsonify({"error": "GOOGLE_MAPS_API_KEY 尚未設定，請在 .env 填入您的 Google Maps API Key"}), 503

    origin      = request.args.get("from", "").strip()
    destination = request.args.get("to", "").strip()
    date_str    = request.args.get("date", "")
    time_str    = request.args.get("time", "")
    hint        = request.args.get("hint", "Japan")

    if not origin or not destination:
        return jsonify({"error": "缺少 from / to 參數"}), 400

    # Build departure timestamp (treat item time as JST)
    now_ts = int(datetime.now(tz=JST).timestamp())
    try:
        if date_str and time_str:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=JST)
            dep_ts = int(dt.timestamp())
        else:
            dep_ts = now_ts
    except Exception:
        dep_ts = now_ts

    # Transit schedules are only available ~few months ahead.
    # If departure is in the past OR more than 60 days away, use now.
    sixty_days = 60 * 24 * 3600
    if dep_ts < now_ts or dep_ts > now_ts + sixty_days:
        dep_ts = now_ts

    origin_q = origin
    dest_q   = destination

    def fetch_route(departure_time):
        qs = urlencode({
            "origin":         origin_q,
            "destination":    dest_q,
            "mode":           "transit",
            "departure_time": departure_time,
            "region":         "jp",
            "language":       "zh-TW",
            "key":            GOOGLE_MAPS_API_KEY,
        })
        url = f"https://maps.googleapis.com/maps/api/directions/json?{qs}"
        with urlopen(Request(url), timeout=8) as resp:
            return _json.loads(resp.read().decode())

    routes      = []
    seen        = set()
    cur_ts      = dep_ts
    last_status = None
    last_msg    = None

    for _ in range(7):          # try up to 7 times to collect 5 results
        if len(routes) >= 5:
            break
        try:
            data = fetch_route(cur_ts)
            last_status = data.get("status")
            last_msg    = data.get("error_message", "")
            if last_status != "OK" or not data.get("routes"):
                break

            route = data["routes"][0]
            leg   = route["legs"][0]

            dep_text  = leg.get("departure_time", {}).get("text", "")
            arr_text  = leg.get("arrival_time",   {}).get("text", "")
            dep_value = leg.get("departure_time", {}).get("value", 0)
            arr_value = leg.get("arrival_time",   {}).get("value", 0)

            dedup_key = dep_text or str(dep_value)
            if dedup_key in seen:
                cur_ts += 120   # advance 2 min and retry
                continue
            seen.add(dedup_key)

            steps = []
            for step in leg.get("steps", []):
                if step.get("travel_mode") != "TRANSIT":
                    continue
                td   = step.get("transit_details", {})
                line = td.get("line", {})
                steps.append({
                    "line":           line.get("name", ""),
                    "short_name":     line.get("short_name", ""),
                    "headsign":       td.get("headsign", ""),
                    "departure_stop": td.get("departure_stop", {}).get("name", ""),
                    "arrival_stop":   td.get("arrival_stop",  {}).get("name", ""),
                    "departure_time": td.get("departure_time", {}).get("text", ""),
                    "arrival_time":   td.get("arrival_time",   {}).get("text", ""),
                    "num_stops":      td.get("num_stops", 0),
                    "vehicle":        line.get("vehicle", {}).get("type", ""),
                    "color":          line.get("color", ""),
                    "text_color":     line.get("text_color", ""),
                })

            route_info = {
                "departure": dep_text,
                "arrival":   arr_text,
                "duration":  leg.get("duration", {}).get("text", ""),
                "steps":     steps,
            }
            if route.get("fare"):
                route_info["fare"] = route["fare"].get("text", "")

            routes.append(route_info)

            # Next iteration: 5 minutes after previous departure
            cur_ts = dep_value + 5 * 60 if dep_value else cur_ts + 1800

        except Exception as ex:
            last_msg = str(ex)
            break

    return jsonify({
        "routes":      routes,
        "origin":      origin_q,
        "destination": dest_q,
        "status":      last_status,
        "error":       last_msg,
    })


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
