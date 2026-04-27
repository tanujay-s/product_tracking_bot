import time
import requests
from bs4 import BeautifulSoup
import re

from product import get_all_active_products, deactivate_expired_products

from main import send_telegram 

HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        }

def is_shopify(url):
    try:
        res = requests.get(url + ".json", timeout=5)
        return res.status_code == 200
    except:
        return False
    
def check_product_url(url):
    try:
        if is_shopify(url):
            stock, price = check_product_api(url)

            if stock is not None and price is not None:
                return stock, price

    except Exception as e:
        print("Shopify API failed:", e)

    return check_product_scrape(url)

def check_product_api(url):
    try:
        api_url = url.rstrip("/") + ".json"

        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            return None, None 

        data = response.json()

        product = data.get("product", {})
        variants = product.get("variants", [])

        if not variants:
            return "⚠️ UNKNOWN", "N/A"

        variant = variants[0]

        price = variant.get("price")
        available = variant.get("available")

        stock = "✅ IN STOCK" if available else "❌ OUT OF STOCK"
        price = f"₹{price}" if price else "Not found"

        return stock, price

    except Exception as e:
        print("API error:", e)
        return None, None


def check_product_scrape(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        page_text = soup.get_text(" ", strip=True).lower()

        # -----------------------
        # 🔍 STOCK DETECTION
        # -----------------------
        out_of_stock_keywords = [
            "out of stock",
            "sold out",
            "currently unavailable",
            "unavailable"
        ]

        in_stock_keywords = [
            "in stock",
            "available",
            "add to cart",
            "buy now"
        ]

        stock = "⚠️ UNKNOWN"

        if any(k in page_text for k in out_of_stock_keywords):
            stock = "❌ OUT OF STOCK"
        elif any(k in page_text for k in in_stock_keywords):
            stock = "✅ IN STOCK"

        # -----------------------
        # 💰 PRICE DETECTION
        # -----------------------

        price = "Not found"

        selectors = [
            ("span", {"class": "price"}),
            ("span", {"class": "price-item"}),
            ("div", {"class": "price"}),
            ("span", {"class": "a-price-whole"}),
            ("div", {"class": "_30jeq3"}),
        ]

        for tag, attrs in selectors:
            el = soup.find(tag, attrs=attrs)
            if el:
                price = el.get_text(strip=True)
                break

        if price == "Not found":
            match = re.search(r"₹\s?[0-9,]+", soup.get_text())
            if match:
                price = match.group()

        if price != "Not found":
            price = price.replace("\n", "").strip()

        return stock, price

    except Exception as e:
        print("Error:", e)
        return "⚠️ ERROR", "N/A"


def run_scheduler():
    print("🚀 Scheduler started...")

    while True:
        print("⏳ Running check cycle...")

        deactivate_expired_products()

        products = get_all_active_products()

        print(products)

        for product in products:
            try:
                product_id, telegram_user_id, url, days, created_at = product

                print(f"Checking: {url}")

                stock, price = check_product_url(url)

                message = (
                    f"🔔 Product Update\n\n"
                    f"🔗 {url}\n\n"
                    f"{stock}\n"
                    f"💰 Price: {price}"
                )

                print('user_id---- ', telegram_user_id)

                send_telegram(telegram_user_id, message)

            except Exception as e:
                print("❌ Error processing product:", e)

        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
