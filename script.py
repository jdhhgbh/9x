import os
import time
from playwright.sync_api import sync_playwright

FIXED_HOST = "http://cf.caftanium.fit/"
FIXED_NAME = "pro"

def main():
    pairing_code = os.environ.get("INPUT_CODE", "").strip()
    username = os.environ.get("INPUT_USER", "").strip()
    password = os.environ.get("INPUT_PASS", "").strip()

    if not pairing_code or not username or not password:
        raise Exception("❌ يرجى ملء جميع الخانات (الرمز، اليوزر، وكلمة المرور)!")

    print(f"🚀 بدء عملية الربط للتلفزيون بالرمز: {pairing_code}")

    with sync_playwright() as p:
        # إعداد المتصفح بتمويه أمني لتخطي Cloudflare بدون مكتبات خارجية
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        # حذف متغيّر navigator.webdriver لمنع كشف البوت
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = context.new_page()

        print("🌐 1. فتح موقع 9Xtream والانتظار لتجاوز الحماية...")
        page.goto("https://remote.9xtream.net/", wait_until="domcontentloaded")
        
        # انتظار بسيط لتجاوز جدار الحماية
        time.sleep(4)

        print("🔑 2. تعبئة رمز الربط والضغط على Next...")
        # البحث عن خانة إدخال الرمز
        code_input = page.locator("input[placeholder*='Type Here'], input[type='text']").first
        code_input.wait_for(state="visible", timeout=30000)
        code_input.fill(pairing_code)

        # الضغط على زر Next
        next_btn = page.locator("button:has-text('Next'), button[type='submit']").first
        next_btn.click()

        time.sleep(3)

        print("📝 3. تعبئة بيانات الاشتراك...")
        # تعبئة Name
        page.locator("input[placeholder*='Optional'], input[name*='name']").first.fill(FIXED_NAME)
        # تعبئة Username
        page.locator("input[placeholder*='Username'], input[name*='user']").first.fill(username)
        # تعبئة Password
        page.locator("input[placeholder*='Password'], input[name*='pass']").first.fill(password)
        # تعبئة Host
        page.locator("input[placeholder*='example.com'], input[name*='host']").first.fill(FIXED_HOST)

        print("📤 4. إرسال البيانات للتلفزيون...")
        page.keyboard.press("Enter")
        
        time.sleep(3)
        browser.close()

    print("🎉 تم التنفيذ وإرسال البيانات بنجاح 100%!")

if __name__ == '__main__':
    main()
