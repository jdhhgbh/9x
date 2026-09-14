import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

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
        # تشغيل المتصفح بإعدادات تتجاوز حماية البوتات
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()
        stealth_sync(page)

        print("🌐 1. فتح موقع remote.9xtream.net والانتظار لتخطي حماية Cloudflare...")
        page.goto("https://remote.9xtream.net/", wait_until="load")
        
        # الانتظار لتجاوز فحص الأمان (Cloudflare Check)
        time.sleep(5)

        # 2. تعبئة الرمز في المربع الأول (Type Here) والضغط على Next
        print("🔑 2. تعبئة رمز الربط والضغط على Next...")
        input_code = page.locator("input[placeholder*='Type Here'], input[type='text']").first
        input_code.wait_for(state="visible", timeout=30000)
        input_code.fill(pairing_code)
        
        # الضغط على زر Next الأخضر
        next_button = page.locator("button:has-text('Next'), button[type='submit']").first
        next_button.click()

        print("⏳ 3. الانتظار للانتقال لصفحة بيانات الحساب (Type remotely)...")
        time.sleep(3)

        # 3. تعبئة البيانات في الصفحة الثانية (Type remotely)
        print("📝 4. تعبئة بيانات الاشتراك (Name, User, Pass, Host)...")
        page.locator("input[placeholder*='Optional'], input[name*='name']").first.fill(FIXED_NAME)
        page.locator("input[placeholder*='Username'], input[name*='user']").first.fill(username)
        page.locator("input[placeholder*='Password'], input[name*='pass']").first.fill(password)
        
        # المربع الرابع لـ Host URL
        host_input = page.locator("input[placeholder*='example.com'], input[name*='host']").first
        host_input.fill(FIXED_HOST)

        # 4. إرسال البيانات للتلفزيون
        print("📤 5. الضغط على زر التفعيل وإرسال البيانات للتلفزيون...")
        # بالصفحة الثانية الزر عادة يتحول إلى Submit أو يتطلب الضغط على الشاشة في التلفزيون
        page.keyboard.press("Enter")
        time.sleep(3)

        browser.close()

    print("🎉 تم تجاوز الحماية وتعبئة البيانات بنجاح في التلفزيون!")

if __name__ == '__main__':
    main()
