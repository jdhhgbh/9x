import os
import re
import sys
import cv2
import pytesseract
from playwright.sync_api import sync_playwright

def parse_iptv_credentials(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to open image {image_path}")
        return None, None, None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='eng+ara')
    print(f"--- Extracted Raw Text ---\n{text}\n--------------------------")

    # 1. استخراج الرابط بشكل مستقل من أي مكان في النص
    url_pattern = r'(https?://[^\s\n]+)'
    url_match = re.search(url_pattern, text, re.IGNORECASE)
    host = url_match.group(1).strip() if url_match else None

    # 2. استخراج Username
    user_pattern = r'Username[:=\s]*([^\s\n]+)'
    user_match = re.search(user_pattern, text, re.IGNORECASE)
    username = user_match.group(1).strip() if user_match else None

    # 3. استخراج Password
    pass_pattern = r'Password[:=\s]*([^\s\n]+)'
    pass_match = re.search(pass_pattern, text, re.IGNORECASE)
    password = pass_match.group(1).strip() if pass_match else None

    # في حال استخراج الرابط مع فتحات أو رموز زائدة في نهايته
    if host:
        host = host.rstrip('/')

    return host, username, password

def parse_remote_code(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to open image {image_path}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)

    code_match = re.search(r'\b[A-Z0-9]{4}\b', text)
    if code_match:
        return code_match.group(0)
    return None

def submit_via_playwright(host, username, password, remote_code):
    print(f"🚀 Automating 9Xtream web pairing for code: {remote_code}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://remote.9xtream.net/", timeout=30000)
            
            # إدخال الكود المكون من 4 أرقام/أحرف
            page.fill("input[name='code'], input[type='text']", remote_code)
            page.click("button[type='submit'], button:has-text('Connect'), button:has-text('Submit')")
            page.wait_for_timeout(3000)

            # تعبئة بيانات IPTV
            page.fill("input[name='host'], input[placeholder*='Host'], input[placeholder*='Server']", host)
            page.fill("input[name='username'], input[placeholder*='User']", username)
            page.fill("input[name='password'], input[placeholder*='Pass']", password)
            
            # الضغط على زر الحفظ/الإرسال
            page.click("button[type='submit'], button:has-text('Save'), button:has-text('Add')")
            page.wait_for_timeout(3000)
            
            print("✅ Successfully submitted IPTV credentials to 9Xtream!")
        except Exception as e:
            print(f"⚠️ Automation step execution notice: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    iptv_img = sys.argv[1] if len(sys.argv) > 1 else "iptv_image.jpg"
    remote_img = sys.argv[2] if len(sys.argv) > 2 else "remote_code.jpg"

    print("🔍 Extracting IPTV credentials...")
    h, u, p = parse_iptv_credentials(iptv_img)
    print(f"Extracted -> Host: {h} | User: {u} | Pass: {p}")

    print("🔍 Extracting Remote Code...")
    code = parse_remote_code(remote_img)
    print(f"Extracted -> Code: {code}")

    if h and u and p and code:
        submit_via_playwright(h, u, p, code)
    else:
        print("❌ Could not extract all required details from images.")
        sys.exit(1)
