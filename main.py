import os
from playwright.sync_api import sync_playwright
import time

C_USER = os.environ.get("C_USER")
XS = os.environ.get("XS")

print("DEBUG: C_USER =", C_USER)
print("DEBUG: XS =", XS)

if not C_USER or not XS:
    raise Exception("❌ יש להגדיר את C_USER ו־XS כסודות.")

def get_latest_post():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies([
            {"name": "c_user", "value": C_USER, "domain": ".facebook.com", "path": "/"},
            {"name": "xs", "value": XS, "domain": ".facebook.com", "path": "/"}
        ])
        page = context.new_page()
        page.goto("https://www.facebook.com/groups/fuadex", timeout=60000)
        time.sleep(5)
        html = page.content()
        print("✅ HTML נטען בהצלחה.")
        browser.close()
        return html

def main():
    print("🔍 מזוהה פוסט חדש לבדיקה...")
    html = get_latest_post()
    print("אורך ה־HTML שהתקבל:", len(html))

if __name__ == "__main__":
    main()
