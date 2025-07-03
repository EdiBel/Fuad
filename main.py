import os
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

C_USER = os.getenv("C_USER")
XS = os.getenv("XS")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://www.facebook.com/groups/fuadex/?sorting_setting=CHRONOLOGICAL"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
}
COOKIES = {
    "c_user": C_USER,
    "xs": XS,
}

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    response = requests.post(url, data=data)
    print("Telegram response:", response.text)

def get_latest_post():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(8000)
        content = page.content()
        browser.close()

        soup = BeautifulSoup(content, "html.parser")
        articles = soup.find_all("div", {"data-ad-comet-preview": "message"})
        if not articles:
            return None, None

        post = articles[0]
        text = post.get_text(strip=True)
        link = URL

        return text, link

def read_last_post_id():
    try:
        with open("latestpost.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def write_last_post_id(post_id):
    with open("latestpost.txt", "w", encoding="utf-8") as f:
        f.write(post_id.strip())

def main():
    last_post = read_last_post_id()
    current_text, link = get_latest_post()

    if not current_text:
        print("❌ לא נמצא פוסט חדש.")
        return

    if current_text != last_post:
        write_last_post_id(current_text)
        send_telegram_message(f"""📢 פוסט חדש בקבוצת פואד:

{current_text}

{link}""")
        print("✅ נשלחה התראה בטלגרם.")
    else:
        print("ℹ️ אין פוסט חדש.")

if __name__ == "__main__":
    main()