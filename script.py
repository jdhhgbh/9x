import os
import glob
import re
import easyocr
from playwright.sync_api import sync_playwright

def main():
    # 1. قراءة الرمز المكتوب في GitHub Workflow
    pairing_code = os.environ.get("INPUT_CODE", "").strip()
    
    if not pairing_code:
        raise Exception("❌ لم يتم كتابة رمز الربط!")
        
    print(f"✅ رمز الربط المدخل: {pairing_code}")

    # 2. قراءة بيانات الحساب من الصورة المرفوعة
    reader = easyocr.Reader(['en', 'ar'])
    images = glob.glob("*.jpg") + glob.glob("*.jpeg") + glob.glob("*.png")
    
    if not images:
        raise Exception("❌ لم يتم العثور على أي صورة لبيانات الحساب في المستودع!")

    print(f"🔍 جاري قراءة البيانات من الصورة: {images[0]}")
    data_text = " ".join(reader.readtext(images[0], detail=0))

    host_match = re.search(r'(https?://[^\s]+)', data_text)
    user_match = re.search(r'(?:username|user|المستخدم)[:\s]*([^\s]+)', data_text, re.IGNORECASE)
    pass_match = re.search(r'(?:password|pass|المرور)[:\s]*([^\s]+)', data_text, re.IGNORECASE)

    username = user_match.group(1) if user_match else ""
    password = pass_match.group(1) if pass_match else ""
    host = host_match.group(1) if host_match else ""

    # 3. الأتمتة على موقع 9xtream
    print("🌐 جاري إدخال البيانات في الموقع...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://remote.9xtream.net/")
        page.fill("input", pairing_code)
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        page.fill("input[placeholder*='Name']", "IPTV Stream")
        page.fill("input[placeholder*='Username']", username)
        page.fill("input[placeholder*='Password']", password)
        page.fill("input[placeholder*='Host']", host)
        
        page.click("button:has-text('ADD PLAYLIST')")
        page.wait_for_timeout(3000)
        browser.close()

    print("🎉 تم ربط التلفزيون وإضافة القائمة بنجاح!")

if __name__ == '__main__':
    main()
