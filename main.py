import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://www.hmtwatches.in/product_details?id=eyJpdiI6Im5vM0xIYmd2SHZzVGE2ejVwc1FITEE9PSIsInZhbHVlIjoiTlROVTN4UkJFNU5kcUxDZ1VDZXNodz09IiwibWFjIjoiZjFhZDBmMDJiYjFjYWY5ODdiNzhiZWMwMDYxZWU0ZDE5OWVkZDNjZTU3Y2EyZGE2MDczZjIzYzI2ZjQ1ZTYzOSIsInRhZyI6IiJ9"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data)

while True:
    current_hour = datetime.now().hour

    if 9 <= current_hour < 20:

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()

        if "Out Of Stock" in text or "Out of Stock" in text or "NOTIFY ME" in text:
            print("❌ Still OUT OF STOCK")
        else:
            print("✅ IN STOCK!!!")
            send_telegram("HMT Kohinoor Maroon is IN STOCK! 👀")

        print("⏳ Next check in 1 hour...\n")

    else:
        print("🌙 Bot sleeping (outside working hours)...")

    time.sleep(3600)
