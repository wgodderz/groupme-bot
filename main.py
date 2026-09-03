from flask import Flask, request
from datetime import datetime, time
from zoneinfo import ZoneInfo          # ← std-lib in Python 3.9+
import json, os, requests, logging

# ───────── basic logger setup ─────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s", # this configs python logging
)

# choose your local timezone
LOCAL_TZ = ZoneInfo("America/Chicago")   # change if needed

app = Flask(__name__) # flask application object

@app.route("/", methods=["POST"]) # this defines the http post route
def groupme_webhook(): # group me calls this each time
    data = request.get_json(silent=True) or {} # parses and loads the data
    logging.info("RAW PAYLOAD ↓\n%s", json.dumps(data, indent=2))

    # Ignore messages sent by this bot itself
    if data.get("sender_type") == "bot":
        return "ok", 200

    # Log the human‐readable part
    message = data.get("text", "") # gets the message
    sender  = data.get("name", "unknown") # gets sender name
    logging.info("%s: %s", sender, message)
    if not message.strip().lower().startswith("/pd"): # return if message not /pd
        return "ok", 200

    bot_id = os.getenv("GROUPME_BOT_ID") # get the bot id
    if bot_id:
        now_dt = datetime.now(LOCAL_TZ) # gets the local date and time
        now_t  = now_dt.time() # gets the time
        weekday = now_dt.strftime("%A")   # "Monday", "Tuesday", etc.

        schedule = {
            "Monday": [
                (time(8,30),  time(9,30),  "Liam Buerge, 417-621-8929"),
                (time(9,30),  time(10,30), "Brodye Bradshaw, 913-334-7650"),
                (time(10,30), time(11,30), "Slate Swinford, 913-207-2283"),
                (time(11,30), time(12,30), "Nick Littlejohn, 816-315-8638"),
                (time(12,30), time(13,30), "Jacob Stirling, 913-523-4096"),
                (time(13,30), time(14,30), "Bradley Ellinger, 913-302-9196"),
                (time(14,30), time(15,30), "Kyan Jantzen, 316-670-7835"),
                (time(15,30), time(16,30), "William Yu, 913-258-4769"),
            ],
            "Tuesday": [
                (time(8,30),  time(9,30),  "Luke Thelen, 913-315-2080"),
                (time(9,30),  time(10,30), "Bryson Eiterich, 913-424-3736"),
                (time(10,30), time(11,30), "Tommy McDowell, 913-260-3400"),
                (time(11,30), time(12,30), "Preston Coors, 720-653-0443"),
                (time(12,30), time(13,30), "Trevor Widener, 913-660-3230"),
                (time(13,30), time(14,30), "Brady Flanigan, 210-371-5196"),
                (time(14,30), time(15,30), "Liam Rhoades, 414-345-0006"),
                (time(15,30), time(16,30), "Brady Collette, 402-630-9691"),
            ],
            "Wednesday": [
                (time(8,30),  time(9,30),  "Liam Buerge, 417-621-8929"),
                (time(9,30),  time(10,30), "Theo Hedican, 402-213-3124"),
                (time(10,30), time(11,30), "Graham Kruger, 913-749-2979"),
                (time(11,30), time(12,30), "Jeremiah Locke, 913-991-3014"),
                (time(12,30), time(13,30), "Carter Hense, 913-820-9372"),
                (time(13,30), time(14,30), "Parker Willis, 913-406-5183"),
                (time(14,30), time(15,30), "Kyan Jantzen, 316-670-7835"),
                (time(15,30), time(16,30), "Colton Matthews, 913-296-1853"),
            ],
            "Thursday": [
                (time(8,30),  time(9,30),  "Jacob Stirling, 913-523-4096"),
                (time(9,30),  time(10,30), "Carter Brock, 816-808-4717"),
                (time(10,30), time(11,30), "Mason Goff, 913-608-1652"),
                (time(11,30), time(12,30), "Preston Coors, 720-653-0443"),
                (time(12,30), time(13,30), "Trevor Widener, 913-660-3230"),
                (time(13,30), time(14,30), "Jeremiah Locke, 913-991-3014"),
                (time(14,30), time(15,30), "Owen McNair, 913-444-2944"),
                (time(15,30), time(16,30), "Oto Sics, 913-237-0406"),
            ],
            "Friday": [
                (time(8,30),  time(9,30),  "Kyan Jantzen, 316-670-7835"),
                (time(9,30),  time(10,30), "Oto Sics, 913-237-0406"),
                (time(10,30), time(11,30), "Carter Hense, 913-820-9372"),
                (time(11,30), time(12,30), "Stratton Leahy, 913-788-4626"),
                (time(12,30), time(13,30), "Parker Willis, 913-406-5183"),
                (time(13,30), time(14,30), "Bobby Knighton, 913-251-2919"),
                (time(14,30), time(15,30), "Theo Hedican, 402-213-3124"),
                (time(15,30), time(16,30), "Theo Hedican, 402-213-3124"),
            ],
        }

        todays_slots = schedule.get(weekday, [])
        current_person = None
        next_person = None

        for i, (start, end, person) in enumerate(todays_slots):
            if start <= now_t < end:
                current_person = person
                if i + 1 < len(todays_slots):
                    next_person = todays_slots[i + 1][2]
                break
            # if we're before this slot and haven't set next yet, this is next
            if next_person is None and now_t < start:
                next_person = person

        if not todays_slots:
            text = "Current driver: No one scheduled today\nNext driver: No one scheduled today"
        else:
            current_line = current_person or "No one right now"
            next_line = next_person or "No one later today"
            text = f"Current driver: {current_line}\nNext driver: {next_line}"

        resp = requests.post(
            "https://api.groupme.com/v3/bots/post",
            json={"bot_id": bot_id, "text": text},
            timeout=5,
        )
        if resp.ok:
            logging.info("Sent reply: %s", text)
        else:
            logging.warning("GroupMe POST failed: %s", resp.text)

    return "ok", 200

# simple GET for health-checks
@app.route("/", methods=["GET"])
def home():
    return "GroupMe bot is live!"


if __name__ == "__main__":
    # Render supplies $PORT; use 8080 for local testing
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
