import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import smtplib
from email.message import EmailMessage

# שליחת מייל
def send_email(subject, body):
    email_to = os.environ.get("EMAIL_TO")
    email_from = os.environ.get("EMAIL_FROM")
    email_pass = os.environ.get("EMAIL_PASS")

    if not (email_to and email_from and email_pass):
        print("⚠️ פרטי המייל לא הוגדרו. מדלג על שליחת מייל.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_from, email_pass)
            smtp.send_message(msg)
        print("✅ מייל נשלח בהצלחה.")
    except Exception as e:
        print(f"שגיאת מייל (התעלם אם אתה לא משתמש בזה): {e}")

# שליחת הודעת טלגרם
def send_telegram_message(text):
    import requests
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not (bot_token and chat_id):
        print("⚠️ טלגרם לא מוגדר. מדלג.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ הודעת טלגרם נשלחה.")
        else:
            print(f"שגיאת טלגרם: {response.text}")
    except Exception as e:
        print(f"שגיאת טלגרם: {e}")

# קריאת מזהה אחרון
def read_last_post_id():
    if not os.path.exists("latestpost.txt"):
        return "0"
    with open("latestpost.txt", "r") as f:
        return f.read().strip()

# כתיבת מזהה חדש
def write_last_post_id(post_id):
    with open("latestpost.txt", "w") as f:
        f.write(post_id)

# שליפת פוסט אחרון מהקבוצה
def get_latest_post():
    c_user = os.environ.get("C_USER")
    xs = os.environ.get("XS")

    if not (c_user and xs):
        raise Exception("❌ יש להגדיר את C_USER ו־XS כסודות.")

    cookies = [
        {
            "name": "c_user",
            "value": str(c_user),
            "domain": ".facebook.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        },
        {
            "name": "xs",
            "value": str(xs),
            "domain": ".facebook.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        print("🔍 טוען את הקבוצה...")
        page.goto("https://www.facebook.com/groups/fuadex", timeout=60000)
        page.wait_for_timeout(5000)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        articles = soup.find_all("div", {"role": "article"})

        for article in articles:
            if article.get("data-ad-comet-preview") == "message":
                continue
            text_content = article.get_text(strip=True)
            post_link_tag = article.find("a", href=True)
            post_link = (
                "https://www.facebook.com" + post_link_tag["href"]
                if post_link_tag
                else "ללא קישור"
            )
            post_id = article.get("data-ft", "")
            return text_content, post_link, post_id

        return None, None, None

# הפונקציה הראשית
def main():
    last_id = read_last_post_id()

    print("🔍 מזוהה פוסט חדש לבדיקה...")
    text, link, post_id = get_latest_post()

    if not post_id:
        print("❌ לא נמצא פוסט חדש.")
        return

    if post_id == last_id:
        print("ℹ️ אין פוסט חדש.")
    else:
        message = f"📢 פוסט חדש בקבוצת פואד:\n\n{text}\n\n🔗 {link}"
        print(message)

        send_email("📢 פוסט חדש בקבוצת פואד", f"{text}\n\n{link}")
        send_telegram_message(message)
        write_last_post_id(post_id)

if __name__ == "__main__":
    main()
