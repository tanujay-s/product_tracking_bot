from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from user import (
    create_user,
    get_user
)
from product import (
    add_product
)

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")

@app.route("/")
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("webhook")
    print(data)

    message = data.get("message", {})
    text = message.get("text") or message.get("caption")
    chat_id = message.get("chat", {}).get("id")

    if not text:
        return "ok", 200

    parts = text.strip().split()

    if parts[0] == "/start":

        user = message.get("from", {})
        user_id = user.get("id")
        username = user.get("username") or user.get("first_name")

        create_user(user_id, username)

        send_telegram(chat_id,
            "👋 Welcome!\n\n"
            "I help you check products pricing and stock status in real-time \n"
            "📌 Use:\n/product <link>\n\n"
            "Example:\n/product https://www.example.com"
        )
        return "ok", 200

    if parts[0] != "/product":
        send_telegram(chat_id, "Use:\n/product <link>")
        return "ok", 200

    if len(parts) < 2:
        send_telegram(chat_id, "Please send:\n/product https://example.com")
        return "ok", 200

    url = parts[1]
    user = message.get("from", {})
    user_id = user.get("id")
    # username = user.get("username") or user.get("first_name")
    db_user = get_user(user_id)

    if not db_user:
        print("User not found")
        return "ok", 200

    db_user_id = db_user[0]

    if not url.startswith("http"):
        send_telegram(chat_id, "Invalid link. Must start with http/https")
        return "ok", 200

    print("URL:", url)
    add_product(db_user_id, url, 5) 
    send_telegram(chat_id, "✅ Product added successfully!")
    return "ok", 200
    

def send_telegram(chat_id, msg):
    print(chat_id, msg)
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": msg}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)