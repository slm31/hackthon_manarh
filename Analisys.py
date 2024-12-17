import base64
import requests
import json
from ChatGpt import chat
# 1. تحويل الصورة إلى Base64
def convert_image_to_base64(image_file):
    try:
        # قراءة الصورة من كائن BytesIO
        image_file.seek(0)  # تأكد أن مؤشر القراءة في البداية
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_image
    except Exception as e:
        print(f"Error converting image to Base64: {e}")
        return None

# 2. إرسال الصورة إلى Plant.id API
def send_image_to_plant_id(base64_image, api_key):
    url = "https://plant.id/api/v3/identification"  # نقطة النهاية الصحيحة
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "images": [base64_image],  # الصورة بصيغة Base64
        "classification_level": "species",  # مستوى التصنيف المطلوب
        "health": "auto",  # تقييم صحة النبات (اختياري)
        "similar_images": True,  # تضمين صور مشابهة (اختياري)
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:  # اعتبر 201 نجاحًا أيضًا
            return response.json()  # النتائج
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error sending image to API: {e}")
        return None

# 3. عرض النتائج


def get_location_from_coordinates(lat, lon):
    try:
        # إعداد الرابط مع إضافة الإحداثيات
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {
            "User-Agent": "MyApp/1.0 (contact: example@email.com)"  # ضع هنا بريدك الإلكتروني كسياسة استخدام
        }

        # إرسال الطلب
        response = requests.get(url, headers=headers)

        # التحقق من النجاح
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            # استخراج المدينة أو البلدة
            city = address.get("city", address.get("town", address.get("village", "غير معروف")))
            state = address.get("state", "")
            country = address.get("country", "")
            return f"{city}, {state}, {country}"
        else:
            return f"فشل في الاتصال بـ Nominatim API: {response.status_code}"
    except Exception as e:
        return f"حدث خطأ: {e}"
    

def display_results(response):
    try:
        # استخراج اسم النبات، احتمالية التصنيف، وصحة النبات
        if response and "result" in response:
            classification = response["result"]["classification"]["suggestions"][0]
            plant_name = classification["name"]
            probability = classification["probability"] * 100  # تحويل النسبة إلى %
            health = response["result"]["is_healthy"]["binary"]

            # طباعة النتيجة
            print(f"اسم النبات: {plant_name}")
            print(f"احتمالية التصنيف: {probability:.2f}%")
            print(f"صحة النبات: {'صحي' if health else 'غير صحي'}")
            return classification , plant_name , probability , health
        else:
            print("لم يتم العثور على نتيجة صالحة.")
    except Exception as e:
        print(f"Error processing results: {e}")


