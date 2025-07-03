import os
from datetime import datetime
import time
import requests

# שליחת הודעה בטלגרם
def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, data=payload)

# שליחת מייל (לא חובה אם אתה לא משתמש במייל)
def send_email(subject, body):
    import smtplib
    from email.mime.text import MIMEText
    email_to = os.getenv("EMAIL_TO")
    email_from = os.getenv("EMAIL_FROM")
    email_pass = os.getenv("EMAIL_PASS")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_from, email_pass)
        server.sendmail(email_from, email_to, msg.as_string())

def main():
    # ניצור תוכן פוסט חדש מזויף לפי השעה הנוכחית
    fake_post_text = f"פוסט בדיקה בזמן: {datetime.now().strftime('%H:%M:%S')}"
    fake_post_link = "https://facebook.com/groups/fuadex/posts/fake"

    print("🔍 מזוהה פוסט חדש לבדיקה...")

    # שלח התראה בטלגרם
    send_telegram_message(f"📢 פוסט חדש בקבוצת פואד:\n\n{fake_post_text}\n\n🔗 {fake_post_link}")

    # שלח התראה במייל (אם רלוונטי)
    try:
        send_email("פוסט חדש בקבוצת פואד", f"{fake_post_text}\n{fake_post_link}")
    except Exception as e:
        print(f"שגיאת מייל (התעלם אם אתה לא משתמש בזה): {e}")

if __name__ == "__main__":
    main()
