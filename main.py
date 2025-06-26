from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['POST'])
def groupme_webhook():
    data = request.get_json()

    # Ignore bot's own messages
    if data['sender_type'] == "bot":
        return "ok", 200

    message = data['text']
    sender = data['name']
    print(f"[{datetime.now()}] {sender}: {message}")

    # Optional: Add logic to respond (e.g., based on time of day)
    # You'd need to call GroupMe's POST message API to reply.

    return "ok", 200

@app.route('/', methods=['GET'])
def home():
    return "GroupMe bot is live!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
