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
                (time(8,30),  time(9,30), "Cooper Kearnes, 913-228-4654"),
                (time(9,30),  time(10,30), "Talis Sics, 913-548-5453"),
                (time(10,30), time(11,30), "Jackson Harrold, 913-304-9469"),
                (time(11,30),  time(12,30), "Finn Romeiser, 469-601-9301"),
                (time(12,30), time(13,30), "Reid Saugstad, 913-820-0901"),
                (time(13,30), time(14,30), "Ryan Levine, 918-902-8584"),
                (time(14,30), time(15,30), "Brady Mandlebaum, 913-291-7442"),
                (time(15,30), time(16,30), "Jacob Wright, 602-689-6301"),
            ],
            "Tuesday": [
                (time(8,30),  time(9,30), "Will Morgan, 913-335-2767"),
                (time(9,30),  time(10,30), "Hayden Coors, 720-346-0353"),
                (time(10,30), time(11,30), "Frank Jesse, 618-420-7856"),
                (time(11,30), time(12,30), "Jaden Dallen, 913-206-9161"),
                (time(12,30), time(13,30), "Brooklyn Ruble, 913-396-3844"),
                (time(13,30), time(14,30), "Nick Martini, 913-908-3369"),
                (time(14,30), time(15,30), "Peyton Ryan, 316-779-5111"),
                (time(15,30), time(16,30), "Jaden Dallen, 913-206-9161"),
            ],
            "Wednesday": [
                (time(8,30), time(9,30), "Joel Suh, 913-927-7191"),
                (time(9,30),  time(10,30), "Hayden Coors, 720-346-0353"),
                (time(10,30), time(11,30), "Jackson Harrold, 913-304-9469"),
                (time(11,30), time(12,30), "Rodney Ferguson, 913-605-5829"),
                (time(12,30), time(13,30), "Payne Elmore, 913-486-5342"),
                (time(13,30), time(14,30), "Brooklyn Ruble, 913-396-3844"),
                (time(14,30), time(15,30), "Cannon Cole, 316-617-2894"),
                (time(15,30), time(16,30), "Brady Mandlebaum, 913-291-7442"),
            ],
            "Thursday": [
                (time(8,30),  time(9,30), "Cooper Kearnes, 913-228-4654"),
                (time(9,30),  time(10,30), "Aidan Ultzsch, 316-364-0760"),
                (time(10,30), time(11,30), "Aidan Ultzsch, 316-364-0760"),
                (time(11,30), time(12,30), "Ryan Kelley, 913-433-4611"),
                (time(12,30), time(13,30), "Nick Martini, 913-908-3369"),
                (time(13,30), time(14,30), "Joel Suh, 913-927-7191"),
                (time(14,30), time(15,30), "Jack Vanblarcom, 913-276-8017"),
                (time(15,30), time(16,30), "Talis Sics, 913-548-5453"),
            ],
            "Friday": [
                (time(8,30),  time(9,30), "Ryan Levine, 918-902-8584"),
                (time(9,30),  time(10,30), "Reid Saugstad, 913-820-0901"),
                (time(10,30), time(11,30), "Ryan Kelley, 913-433-4611"),
                (time(11,30), time(12,30), "Jacob Wright, 602-689-6301"),
                (time(12,30), time(13,30), "Payne Elmore, 913-486-5342"),
                (time(13,30), time(14,30), "Zac Neid, 402-517-7973"), 
                (time(14,30), time(15,30), "Finn Romeiser, 469-601-9301"),
                (time(15,30), time(16,30), "Zac Neid, 402-517-7973"), 
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
