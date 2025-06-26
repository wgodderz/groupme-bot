from flask import Flask, request
from datetime import datetime, time
import json, os, requests, logging

# ────────── basic logger setup ──────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

app = Flask(__name__)

# ───────────────────────────────────────────────
# 1) webhook – runs every time GroupMe POSTs here
# ───────────────────────────────────────────────
@app.route("/", methods=["POST"])
def groupme_webhook():
    data = request.get_json(silent=True) or {}
    logging.info("RAW PAYLOAD ↓\n%s", json.dumps(data, indent=2))

    # Ignore this bot’s own messages
    if data.get("sender_type") == "bot":
        return "ok", 200

    message = data.get("text", "")
    sender  = data.get("name", "unknown")
    logging.info("%s: %s", sender, message)

    # ───────── time-based auto-reply ─────────
    bot_id = os.getenv("GROUPME_BOT_ID")     # set this in Render ➜ Environment
    if bot_id:
        now = datetime.now().time()
        morning  = time(7,  0)   # 07:00
        noon     = time(12, 0)   # 12:00
        afternoon= time(17, 0)   # 17:00

        reply = None
        if morning <= now <= noon:
            reply = "Will is driving"
        elif noon < now <= afternoon:
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
    # ────────────────────────────────────────
    return "ok", 200


# simple GET for health-checks
@app.route("/", methods=["GET"])
def home():
    return "GroupMe bot is live!"

if __name__ == "__main__":
    # Render sets $PORT; default to 8080 locally
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
