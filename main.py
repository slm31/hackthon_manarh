import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from Analisys import send_image_to_plantnet
from ChatGpt import chat

# إعداد CSS لتنسيق النصوص والعناصر
st.markdown(
    """
    <style>
    .centered {
        text-align: center;
    }
    .highlight {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
    }
    .subtitle {
        font-size: 18px;
        color: #666;
    }
    .footer {
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 12px;
        color: #aaa;
    }
    .stButton>button {
        display: block;
        margin: 0 auto;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# مفاتيح API
plantnet_api_key = st.secrets.get("plantnet_api_key", None)
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", None)

if not plantnet_api_key or not WEATHER_API_KEY:
    st.error("❌ مفاتيح الـ API مفقودة. تأكد من إضافتها إلى secrets.toml أو إعدادات Streamlit Cloud.")

# دالة جلب توقعات الأمطار
def get_rain_forecast(api_key, lat, lon):
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {"key": api_key, "q": f"{lat},{lon}", "days": 30}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {"date": day["date"], "rain": day["day"]["totalprecip_mm"]}
            for day in data["forecast"]["forecastday"]
        ]
    return []

# دالة تحويل الإحداثيات إلى اسم موقع
def get_location_from_coordinates(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "MyApp/1.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            city = address.get("city", address.get("town", address.get("village", "غير معروف")))
            state = address.get("state", "")
            country = address.get("country", "")
            return f"{city}, {state}, {country}"
        else:
            return "تعذر الحصول على اسم الموقع"
    except Exception as e:
        return f"حدث خطأ: {e}"

# عنوان التطبيق
st.markdown("<h1 class='centered highlight'>🌿 فريق سلمى - هاكثون منارة حائل</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered subtitle'>حدد الموقع وابدأ تحليلك! 🌍</p>", unsafe_allow_html=True)

# عرض الخريطة
map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=700, height=500)

if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"📍 الإحداثيات: ({lat:.6f}, {lon:.6f})")

    # تحويل الإحداثيات إلى اسم الموقع
    location_name = get_location_from_coordinates(lat, lon)
    st.markdown(f"<p class='centered highlight'>🗺️ الموقع: {location_name}</p>", unsafe_allow_html=True)

    # زر جلب توقعات الأمطار
    if st.button("☔ جلب توقعات هطول الأمطار"):
        st.markdown("<h3 class='centered subtitle'>☁️ توقعات الأمطار</h3>", unsafe_allow_html=True)
        forecast = get_rain_forecast(WEATHER_API_KEY, lat, lon)
        if forecast:
            for day in forecast:
                st.write(f"📅 {day['date']}: {day['rain']} ملم")
        else:
            st.warning("❌ تعذر جلب توقعات الأمطار.")

   # رفع صورة النبات
st.markdown("<h3 class='centered highlight'>🌿 تحليل صورة النبات</h3>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="",
    type=["jpg", "jpeg", "png"]
)

# إضافة نص مخصص بالوسط
# نص "اختر صورة" فوق أداة الرفع
# نص "اختر صورة" فوق أداة الرفع
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 10px;'>
        <span style='font-size: 18px; font-weight: bold; color: #4CAF50;'>
            📸 اختر صورة:
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# أداة رفع الصورة (مرة واحدة فقط)
uploaded_file = st.file_uploader(
    label="",
    type=["jpg", "jpeg", "png"]
)

# عرض الصورة المرفوعة
if uploaded_file:
    st.image(uploaded_file, caption="📸 الصورة المرفوعة", use_container_width=True)
    with st.spinner("🔍 جاري تحليل الصورة..."):
        result = send_image_to_plantnet(uploaded_file, plantnet_api_key)
        if result:
            st.write(f"**🔬 اسم النبات العلمي:** {result['scientific_name']}")
            st.write(f"**🌱 الأسماء الشائعة:** {', '.join(result['common_names'])}")
            st.write(f"**📊 نسبة التطابق:** {float(result['score']):.2f}%")
            st.write(f"**🔍 الجنس:** {result['genus']}")
            st.write(f"**🌳 العائلة:** {result['family']}")
        else:
            st.error("❌ تعذر تحليل الصورة. حاول مجددًا.")

# تذييل الصفحة
st.markdown("<div class='footer'>Hakathon Manarah - Team Salma 🌟</div>", unsafe_allow_html=True)
