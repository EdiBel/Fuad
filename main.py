import os
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

C_USER = os.getenv("C_USER")
XS = os.getenv("XS")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

GROUP_URL = "https://www.facebook.com/groups/fuadex/?sorting_setting=CHRONOLOGICAL"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
COOKIES = {
    "c_user": C_USER,
    "xs": XS
}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Failed to send Telegram message:", e)

def get_latest_post_id(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    links = soup.find_all("a", href=True)
    for a in links:
        href = a["href"]
        if "/posts/" in href:
            parts = href.split("/posts/")
            if len(parts) > 1:
                return parts[1].split("/")[0]
    return None

def read_last_post_id():
    if not os.path.exists("latest_post.txt"):
        return None
    with open("latest_post.txt", "r") as f:
        return f.read().strip()

def write_last_post_id(post_id):
    with open("latest_post.txt", "w") as f:
        f.write(post_id)

def main():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(extra_http_headers=HEADERS)
        context.add_cookies([
            {"name": "c_user", "value": C_USER, "domain": ".facebook.com", "path": "/"},
            {"name": "xs", "value": XS, "domain": ".facebook.com", "path": "/"}
        ])
        page = context.new_page()
        page.goto(GROUP_URL, timeout=60000)
        page_content = page.content()
        current_post_id = get_latest_post_id(page_content)
        browser.close()

    if not current_post_id:
        print("לא נמצא פוסט")
        return

    last_post_id = read_last_post_id()
    if current_post_id != last_post_id:
        write_last_post_id(current_post_id)
        send_telegram_message(f"📢 פוסט חדש בקבוצת פואד:
https://www.facebook.com/groups/fuadex/posts/{current_post_id}")
        print("✅ פוסט חדש נשלח")
    else:
        print("❌ אין פוסט חדש")

if __name__ == "__main__":
    main()