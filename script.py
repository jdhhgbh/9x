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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        # ضبط مهلة الانتظار إلى 60 ثانية احتياطاً
        page.set_default_timeout(60000)

        print("🌐 جاري فتح موقع 9Xtream Remote...")
        page.goto("https://remote.9xtream.net/", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # إذا كانت الشاشة الأولى تطلب الرمز وتتغير لصفحة البيانات:
        # فحص وجود مربع الرمز أو المربعات المباشرة
        inputs = page.locator("input[type='text'], input:not([type='hidden'])")
        
        # إذا كان الموقع في الصفحة الأولى (إدخال الرمز)
        if page.locator("input[placeholder*='Name']").count() == 0:
            print("🔑 إدخال رمز الربط...")
            # البحث عن مربع النص الظاهر
            for i in range(inputs.count()):
                inp = inputs.nth(i)
                if inp.is_visible():
                    inp.fill(pairing_code)
                    break
            
            # الضغط على زر Submit أو Enter
            submit_btn = page.locator("button:has-text('Submit'), button[type='submit']")
            if submit_btn.count() > 0 and submit_btn.first.is_visible():
                submit_btn.first.click()
            else:
                page.keyboard.press("Enter")
                
            page.wait_for_timeout(3000)

        # تعبئة بيانات IPTV
        print("📝 تعبئة بيانات الاشتراك...")
        page.fill("input[placeholder*='Name']", FIXED_NAME)
        page.fill("input[placeholder*='Username']", username)
        page.fill("input[placeholder*='Password']", password)
        page.fill("input[placeholder*='Host']", FIXED_HOST)

        # الضغط على ADD PLAYLIST
        print("📤 إرسال البيانات للتلفزيون...")
        page.click("button:has-text('ADD PLAYLIST')")

        page.wait_for_timeout(4000)
        browser.close()

    print("🎉 تم التفعيل وإضافة القائمة بنجاح 100%!")

if __name__ == '__main__':
    main()
