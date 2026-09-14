import os
import requests

# 1. الثوابت الجاهزة
FIXED_HOST = "http://cf.caftanium.fit/"
FIXED_NAME = "pro"

def main():
    # 2. قراءة الإدخالات من Workflow
    pairing_code = os.environ.get("INPUT_CODE", "").strip()
    username = os.environ.get("INPUT_USER", "").strip()
    password = os.environ.get("INPUT_PASS", "").strip()

    if not pairing_code or not username or not password:
        raise Exception("❌ يرجى ملء جميع الخانات (الرمز، اليوزر، وكلمة المرور)!")

    print(f"🚀 جاري ربط القائمة ({FIXED_NAME}) للتلفزيون بالرمز: {pairing_code}")
    print(f"👤 اليوزر: {username}")
    print(f"🌐 الرابط: {FIXED_HOST}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://remote.9xtream.net/",
        "Origin": "https://remote.9xtream.net"
    })

    payload = {
        "code": pairing_code,
        "name": FIXED_NAME,
        "username": username,
        "password": password,
        "host": FIXED_HOST
    }

    # إرسال البيانات المباشر
    response = session.post("https://remote.9xtream.net/api/add-playlist", data=payload)

    if response.status_code == 200:
        print("🎉 تم التفعيل وإضافة القائمة على التلفزيون بنجاح 100%!")
    else:
        # مسار إضافي احتياطي
        response_alt = session.post("https://remote.9xtream.net/", data=payload)
        if response_alt.status_code == 200:
            print("🎉 تم التفعيل بنجاح عبر المسار الاحتياطي!")
        else:
            raise Exception(f"❌ حدث خطأ أثناء الربط، رمز الاستجابة: {response.status_code}")

if __name__ == '__main__':
    main()
