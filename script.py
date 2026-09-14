import os
from playwright.sync_api import sync_playwright

FIXED_HOST = "http://cf.caftanium.fit/"
FIXED_NAME = "pro"

def main():
    pairing_code = os.environ.get("INPUT_CODE", "").strip()
    username = os.environ.get("INPUT_USER", "").strip()
    password = os.environ.get("INPUT_PASS", "").strip()

    if not pairing_code or not username or not password:
        raise Exception("❌ يرجى ملء جميع الخانات (الرمز، اليوزر، وكلمة المرور)!")

    print(f"🚀 جاري الربط للتلفزيون بالرمز: {pairing_code}")

    with sync_playwright() as p:
        # تشغيل المتصفح
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        print("🌐 جاري فتح موقع 9Xtream Remote...")
        page.goto("https://remote.9xtream.net/", wait_until="networkidle")

        # تعبئة الرمز في المربع المرئي تحديداً
        print("🔑 إدخال رمز الربط...")
        code_input = page.locator("input[type='text']:visible, input:not([type='hidden']):visible").first
        code_input.fill(pairing_code)
        
        # الضغط على زر المتابعة/Submit
        submit_btn = page.locator("button[type='submit'], button:has-text('Submit'), button:has-text('Connect')").first
        if submit_btn.is_visible():
            submit_btn.click()
        else:
            code_input.press("Enter")
            
        page.wait_for_timeout(3000)

        # تعبئة بيانات IPTV
        print("📝 تعبئة بيانات الاشتراك...")
        page.locator("input[placeholder*='Name'], input[name*='name']").first.fill(FIXED_NAME)
        page.locator("input[placeholder*='Username'], input[name*='user']").first.fill(username)
        page.locator("input[placeholder*='Password'], input[name*='pass']").first.fill(password)
        page.locator("input[placeholder*='Host'], input[name*='host']").first.fill(FIXED_HOST)

        # الضغط على ADD PLAYLIST
        print("📤 إرسال البيانات للتلفزيون...")
        add_btn = page.locator("button:has-text('ADD PLAYLIST'), button[type='submit']").first
        add_btn.click()

        page.wait_for_timeout(4000)
        browser.close()

    print("🎉 تم التفعيل وإضافة القائمة بنجاح 100%!")

if __name__ == '__main__':
    main()
