import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from Analisys import send_image_to_plantnet
from ChatGpt import chat

plantnet_api_key = st.secrets.get("plantnet_api_key")
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY")


# إعداد CSS لتنسيق النصوص والعناصر
st.markdown(
    """
    <style>
    .centered {
        text-align: center;
    }
    .highlight {
        font-size: 26px;
        font-weight: bold;
        color: #4CAF50;
    }
    .subtitle {
        font-size: 20px;
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

# عنوان التطبيق
st.markdown("<h1 class='centered highlight'>🌟 هاكثون منارة حائل 🌟</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='centered subtitle'>⛰️ فريق سلمى ⛰️</h2>", unsafe_allow_html=True)

# تصغير حجم الخريطة
st.markdown("<h3 class='centered'>🗺️ حدد الموقع وابدأ تحليلك! 🌍</h3>", unsafe_allow_html=True)
map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=500, height=350)  # تصغير الخريطة

if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"📍 الإحداثيات: ({lat:.6f}, {lon:.6f})")

    # تحويل الإحداثيات إلى اسم الموقع
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

    location_name = get_location_from_coordinates(lat, lon)
    st.markdown(f"<p class='centered highlight'>🗺️ الموقع: {location_name}</p>", unsafe_allow_html=True)

    # زر جلب توقعات الأمطار
    if st.button("☔ جلب توقعات هطول الأمطار"):
        st.markdown("<h3 class='centered subtitle'>☁️ توقعات الأمطار</h3>", unsafe_allow_html=True)
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

        forecast = get_rain_forecast(st.secrets.get("WEATHER_API_KEY"), lat, lon)
        if forecast:
            for day in forecast:
                st.write(f"📅 {day['date']}: {day['rain']} ملم")
        else:
            st.warning("❌ تعذر جلب توقعات الأمطار.")

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

# أداة رفع الصورة
uploaded_file = st.file_uploader(
    label="",
    type=["jpg", "jpeg", "png"],
    key="unique_file_uploader"
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

            # إرسال البيانات إلى ChatGPT
            with st.spinner("💬 جاري تحليل البيانات بواسطة الذكاء الاصطناعي..."):
                analysis_data = f"اسم النبات: {result['scientific_name']}, نسبة التطابق: {result['score']}%"
                chat_response = chat(analysis_data, location_name)
                st.markdown("<h3 class='centered subtitle'>💡 التحليل الإضافي:</h3>", unsafe_allow_html=True)
                st.write(chat_response)
        else:
            st.error("❌ تعذر تحليل الصورة. حاول مجددًا.")

# تذييل الصفحة
st.markdown("<div class='footer'>Hakathon Manarah - Team Salma 🌟</div>", unsafe_allow_html=True)
