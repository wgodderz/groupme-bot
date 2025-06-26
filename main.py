from flask import Flask, request
from datetime import datetime
import json, os, requests

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# 1)  Receive every POST from GroupMe and log the full payload
# ─────────────────────────────────────────────────────────────
@app.route('/', methods=['POST'])
def groupme_webhook():
    data = request.get_json(silent=True) or {}
    print("----- RAW GROUPME PAYLOAD -----")
    print(json.dumps(data, indent=2))
    print("----- END RAW PAYLOAD ---------")

    # Ignore our own bot messages
    if data.get("sender_type") == "bot":
        return "ok", 200

    # Safely pull the fields we care about
    message = data.get("text")
    sender  = data.get("name")
    print(f"[{datetime.now()}] {sender}: {message}")

    # ───────── OPTIONAL REPLY EXAMPLE ─────────
    # If you want the bot to talk back, set GROUPME_BOT_ID
    # on Render (Environment ► +Add Variable) and uncomment ↓
    """
    bot_id = os.getenv("GROUPME_BOT_ID")
    if bot_id and message:
        requests.post(
            "https://api.groupme.com/v3/bots/post",
            json = {"bot_id": bot_id, "text": f"Echo: {message}"}
        )
    """
    # ──────────────────────────────────────────
    return "ok", 200


# Simple health-check endpoint
@app.route('/', methods=['GET'])
def home():
    return "GroupMe bot is live!"


if __name__ == "__main__":
    # Render exposes whichever port your code listens on
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
