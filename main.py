import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from Analisys import send_image_to_plantnet
from ChatGpt import chat

# مفاتيح API
plantnet_api_key = st.secrets.get("plantnet_api_key")
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY")

# إعداد CSS للاستجابة
st.markdown(
    """
    <style>
    .centered { text-align: center; }
    .highlight { font-size: 20px; color: #4CAF50; }
    .subtitle { font-size: 16px; color: #666; }
    .small-text { font-size: 12px; color: #555; }
    .footer {
        position: fixed; bottom: 10px; width: 100%;
        text-align: center; font-size: 12px; color: #aaa;
    }
    .responsive-map { width: 100% !important; height: 300px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# العنوان
st.markdown("<h1 class='centered highlight'>هاكثون منارة حائل</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='centered subtitle'>⛰️ فريق سلمى ⛰️</h2>", unsafe_allow_html=True)
st.markdown("<h3 class='centered'>🗺️ حدد الموقع وابدأ تحليلك</h3>", unsafe_allow_html=True)

# الخريطة
map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width="100%", height=350, returned_objects=["last_clicked"])

# التحقق من الموقع
if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    # تحويل الإحداثيات إلى موقع
    def get_location_from_coordinates(lat, lon):
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            return f"{address.get('city', 'غير معروف')}, {address.get('state', '')}, {address.get('country', '')}"
        return "تعذر تحديد الموقع"

    location_name = get_location_from_coordinates(lat, lon)
    st.markdown(f"<p class='centered highlight'>🗺️ الموقع: {location_name}</p>", unsafe_allow_html=True)

    # زر توقعات الأمطار
    if st.button("☔ جلب توقعات هطول الأمطار"):
        def get_rain_forecast(api_key, lat, lon):
            url = "http://api.weatherapi.com/v1/forecast.json"
            params = {"key": api_key, "q": f"{lat},{lon}", "days": 3}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return [{"date": day["date"], "rain": day["day"]["totalprecip_mm"]} for day in data["forecast"]["forecastday"]]
            return []

        forecast = get_rain_forecast(WEATHER_API_KEY, lat, lon)
        st.markdown("<h3 class='centered subtitle'>☁️ توقعات الأمطار:</h3>", unsafe_allow_html=True)
        for day in forecast:
            st.markdown(f"<p class='small-text'>📅 {day['date']}: {day['rain']} ملم</p>", unsafe_allow_html=True)

# رفع الصورة
st.markdown("<div style='text-align: center; margin: 10px;'>"
            "<span style='font-size: 18px; font-weight: bold; color: #4CAF50;'>📸 اختر صورة:</span></div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="unique_file_uploader")

# تحليل الصورة وإرسال البيانات لـ ChatGPT
if uploaded_file:
    st.image(uploaded_file, caption="📸 الصورة المرفوعة", use_container_width=True)
    with st.spinner("🔍 جاري تحليل الصورة..."):
        result = send_image_to_plantnet(uploaded_file, plantnet_api_key)
        if result:
            st.markdown(f"<p class='small-text'>🔬 اسم النبات العلمي: {result['scientific_name']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='small-text'>🌱 الأسماء الشائعة: {', '.join(result['common_names'])}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='small-text'>📊 نسبة التطابق: {float(result['score']):.2f}%</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='small-text'>🔍 الجنس: {result['genus']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='small-text'>🌳 العائلة: {result['family']}</p>", unsafe_allow_html=True)

            # إرسال البيانات إلى ChatGPT
            with st.spinner("💬 تحليل البيانات باستخدام الذكاء الاصطناعي..."):
                analysis_data = f"اسم النبات: {result['scientific_name']}, نسبة التطابق: {result['score']}%, الموقع: {location_name}"
                chat_response = chat(analysis_data, location_name)
                st.markdown("<h3 class='centered subtitle'>💡 التحليل الإضافي:</h3>", unsafe_allow_html=True)
                st.markdown(f"<p class='small-text'>{chat_response}</p>", unsafe_allow_html=True)
        else:
            st.error("❌ تعذر تحليل الصورة. حاول مجددًا.")

# تذييل الصفحة
st.markdown("<div class='footer'>Hakathon Manarah - Team Salma 🌟</div>", unsafe_allow_html=True)
