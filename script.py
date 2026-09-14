import os
import glob
import re
import easyocr
import requests

def main():
    # 1. قراءة الرمز المدخل من GitHub Actions
    pairing_code = os.environ.get("INPUT_CODE", "").strip()
    if not pairing_code:
        raise Exception("❌ لم يتم كتابة رمز الربط!")
        
    print(f"✅ رمز الربط المدخل: {pairing_code}")

    # 2. قراءة بيانات الحساب من الصورة
    reader = easyocr.Reader(['en', 'ar'])
    images = glob.glob("*.jpg") + glob.glob("*.jpeg") + glob.glob("*.png")
    
    if not images:
        raise Exception("❌ لم يتم العثور على أي صورة للبيانات في المستودع!")

    print(f"🔍 جاري قراءة البيانات من الصورة: {images[0]}")
    data_text = " ".join(reader.readtext(images[0], detail=0))

    host_match = re.search(r'(https?://[^\s]+)', data_text)
    user_match = re.search(r'(?:username|user|المستخدم)[:\s]*([^\s]+)', data_text, re.IGNORECASE)
    pass_match = re.search(r'(?:password|pass|المرور)[:\s]*([^\s]+)', data_text, re.IGNORECASE)

    username = user_match.group(1) if user_match else ""
    password = pass_match.group(1) if pass_match else ""
    host = host_match.group(1) if host_match else ""

    print(f"📌 البيانات المستخرجة:")
    print(f"   - User: {username}")
    print(f"   - Host: {host}")

    # 3. إرسال البيانات مباشرة إلى سيرفر 9xtream المباشر
    print("🚀 جاري الربط وإرسال البيانات مباشرة عبر الـ API...")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://remote.9xtream.net/",
        "Origin": "https://remote.9xtream.net"
    })

    # إرسال طلب الربط والإضافة
    payload = {
        "code": pairing_code,
        "name": "IPTV Stream",
        "username": username,
        "password": password,
        "host": host
    }

    response = session.post("https://remote.9xtream.net/api/add-playlist", data=payload)

    if response.status_code == 200:
        print("🎉 تم ربط التلفزيون وإضافة القائمة بنجاح!")
    else:
        # محاولة عبر المسار البديل (Form Submit)
        response_alt = session.post("https://remote.9xtream.net/", data=payload)
        if response_alt.status_code == 200:
            print("🎉 تم ربط التلفزيون بنجاح عبر المسار البديل!")
        else:
            raise Exception(f"❌ فشل الربط! رمز الاستجابة: {response.status_code}")

if __name__ == '__main__':
    main()
