import os
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
C_USER = os.getenv("C_USER")
XS = os.getenv("XS")

GROUP_URL = "https://www.facebook.com/groups/fuadex/?sorting_setting=CHRONOLOGICAL"
LATEST_POST_FILE = "latestpost.txt"

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ טלגרם לא מוגדר. מדלג על שליחה.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        res = requests.post(url, data=payload)
        res.raise_for_status()
        print("✅ נשלחה הודעה בטלגרם.")
    except Exception as e:
        print("❌ שגיאה בשליחת הודעה לטלגרם:", e)

def get_latest_post():
    cookies = {"c_user": C_USER, "xs": XS}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies([{
            "name": "c_user", "value": C_USER, "domain": ".facebook.com", "path": "/"
        }, {
            "name": "xs", "value": XS, "domain": ".facebook.com", "path": "/"
        }])
        page = context.new_page()
        page.goto(GROUP_URL, timeout=60000)
        time.sleep(5)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        browser.close()

        # ניסיון למציאת מזהה/לינק של פוסט ראשון
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/posts/" in href:
                full_link = "https://www.facebook.com" + href.split("?")[0]
                post_id = href.split("/posts/")[1].split("/")[0]
                return post_id, full_link

        return None, None

def read_last_post_id():
    if not os.path.exists(LATEST_POST_FILE):
        return None
    with open(LATEST_POST_FILE, "r") as f:
        return f.read().strip()

def write_last_post_id(post_id):
    with open(LATEST_POST_FILE, "w") as f:
        f.write(post_id)

def main():
    print("🔍 מזוהה פוסט חדש לבדיקה...")
    last_id = read_last_post_id()
    current_id, link = get_latest_post()

    if current_id is None:
        print("❌ לא נמצא פוסט חדש.")
        return

    if current_id != last_id:
        print("✅ פוסט חדש מזוהה:", current_id)
        write_last_post_id(current_id)
        send_telegram_message(f"📢 פוסט חדש בקבוצת פואד:\n{link}")
    else:
        print("ℹ️ אין פוסט חדש.")

if __name__ == "__main__":
    main()
