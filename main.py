from flask import Flask, request
from datetime import datetime, time
from zoneinfo import ZoneInfo          # ← std-lib in Python 3.9+
import json, os, requests, logging

# ───────── basic logger setup ─────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# choose your local timezone
LOCAL_TZ = ZoneInfo("America/Chicago")   # change if needed

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# 1) GroupMe webhook — called on every POST from your group
# ─────────────────────────────────────────────────────────────
@app.route("/", methods=["POST"])
def groupme_webhook():
    data = request.get_json(silent=True) or {}
    logging.info("RAW PAYLOAD ↓\n%s", json.dumps(data, indent=2))

    # Ignore messages sent by this bot itself
    if data.get("sender_type") == "bot":
        return "ok", 200

    # Log the human‐readable part
    message = data.get("text", "")
    sender  = data.get("name", "unknown")
    logging.info("%s: %s", sender, message)

    # ─── time-based auto-reply ───
    bot_id = os.getenv("GROUPME_BOT_ID")     # set in Render ➜ Environment
    if bot_id:
        now   = datetime.now(LOCAL_TZ).time()
        morn  = time(7, 0)      # 07:00
        noon  = time(12, 0)     # 12:00
        aft   = time(17, 0)     # 17:00

        reply = None
        if morn <= now <= noon:
            reply = "Will is driving"
        elif noon < now <= aft:
            reply = "Hank is driving"

        if reply:
            resp = requests.post(
                "https://api.groupme.com/v3/bots/post",
                json={"bot_id": bot_id, "text": reply},
                timeout=5,
            )
            if resp.ok:
                logging.info("Sent reply: %s", reply)
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
