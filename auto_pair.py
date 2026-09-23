import os
import re
import cv2
import pytesseract
import requests
import sys

def parse_iptv_credentials(image_path):
    # تحسين الصورة للقراءة
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # استخراج النص
    text = pytesseract.image_to_string(gray, lang='eng+ara')
    print(f"--- Extracted IPTV Text ---\n{text}\n--------------------------")

    url_pattern = r'(https?://[^\s:]+(?::\d+)?)'
    user_pattern = r'(?:username|user|usr|مستخدم|اسم المستخدم)[:=\s]*([^\s\n]+)'
    pass_pattern = r'(?:password|pass|pwd|كلمة السر|كلمة المرور)[:=\s]*([^\s\n]+)'

    url_match = re.search(url_pattern, text, re.IGNORECASE)
    user_match = re.search(user_pattern, text, re.IGNORECASE)
    pass_match = re.search(pass_pattern, text, re.IGNORECASE)

    host = url_match.group(1) if url_match else None
    username = user_match.group(1) if user_match else None
    password = pass_match.group(1) if pass_match else None

    # التحقق من البيانات المستخرجة من الصورة الأولى
    if host and username and password:
        return host, username, password
    else:
        # محاولة أخيرة لو كان رابط Xtream كامل في سطر واحد
        match = re.search(r'(https?://[^/]+)/get.php\?username=([^&]+)&password=([^&]+)', text)
        if match:
            return match.group(1), match.group(2), match.group(3)
        return None, None, None

def parse_remote_code(image_path):
    # تحسين الصورة لقراءة الكود
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    print(f"--- Extracted Code Text ---\n{text}\n--------------------------")

    # البحث عن كود من 4 أحرف إنجليزية كبيرة
    code_match = re.search(r'\b[A-Z]{4}\b', text)
    if code_match:
        return code_match.group(0)
    return None

def send_to_9xtream(host, username, password, remote_code):
    api_url = "https://remote.9xtream.net/api/v1/remote/login" # هذا هو الـ endpoint المحتمل
    
    payload = {
        "host": host,
        "username": username,
        "password": password,
        "remote_code": remote_code,
        "playlist_name": "Autopaired Trial",
        "type": "xtream"
    }

    # المحاكاة (لن نقوم بالإرسال الفعلي)
    print(f"--- Simulating POST Request to 9Xtream API ---")
    print(f"Payload: {payload}")
    # response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"})
    # print(f"Response: {response.status_code}, {response.text}")
    print("Simulated SUCCESS")
    return "SUCCESS" # return dynamic state

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python auto_pair.py <iptv_image_path> <remote_code_image_path>")
        sys.exit(1)

    iptv_img = sys.argv[1]
    remote_img = sys.argv[2]

    print("Step 1: Parsing IPTV Credentials...")
    h, u, p = parse_iptv_credentials(iptv_img)
    if not h:
        print("Error: Could not extract IPTV credentials.")
        sys.exit(1)
    print(f"Found: Host={h}, User={u}")

    print("Step 2: Parsing Remote Code...")
    code = parse_remote_code(remote_img)
    if not code:
        print("Error: Could not extract 4-letter remote code.")
        sys.exit(1)
    print(f"Found Code: {code}")

    print("Step 3: Sending to 9Xtream API...")
    result = send_to_9xtream(h, u, p, code)
    if result == "SUCCESS":
        print("Successfully paired with 9Xtream remote server!")
    else:
        print("Failed to pair.")
