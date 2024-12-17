import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from Analisys import convert_image_to_base64, send_image_to_plant_id, display_results
from ChatGpt import chat  # تأكد من استيراد الدالة chat

# مفاتيح API
WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
PLANT_API_KEY = st.secrets["PLANT_API_KEY"]

# دالة جلب توقعات الأمطار
def get_rain_forecast(api_key, lat, lon):
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {"key": api_key, "q": f"{lat},{lon}", "days": 90, "aqi": "no", "alerts": "no"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            forecasts = [{"date": day["date"], "rain": round(day["day"]["totalprecip_mm"], 5)}
                         for day in data["forecast"]["forecastday"]]
            return f"{data['location']['name']}, {data['location']['region']}", forecasts
        else:
            return "تعذر الحصول على البيانات", []
    except Exception as e:
        return f"حدث خطأ: {e}", []

# تحسين التصميم
st.markdown("""
    <style>
        h1, h2 {
            text-align: center;
            font-family: Arial, sans-serif;
        }
        h1 { font-size: 10px; color: #4CAF50; }
        h2 { font-size: 15px; color: #1E88E5; }
        .center-text {
            text-align: center;
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .small-map {
            width: 600px !important;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# العناوين
st.markdown("<h1> هاكثون منارة حائل</h1>", unsafe_allow_html=True)
st.markdown("<h2>🏔️ فريق سلمى</h2>", unsafe_allow_html=True)

# الخريطة
st.markdown("---")
st.markdown('<p class="center-text">🌍 حدد موقع على الخريطة</p>', unsafe_allow_html=True)

map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=350, height=350)

if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    st.markdown(f'<p class="center-text">📍 الإحداثيات: ({lat:.6f}, {lon:.6f})</p>', unsafe_allow_html=True)

    # جلب التوقعات
    if st.button("☁️ عرض توقعات الأمطار"):
        with st.spinner("⏳ جاري جلب البيانات..."):
            location_name, forecasts = get_rain_forecast(WEATHER_API_KEY, lat, lon)
            if forecasts:
                st.markdown(f'<p class="center-text">📍 الموقع: {location_name}</p>', unsafe_allow_html=True)
                for forecast in forecasts:
                    if forecast["rain"] > 0:
                        st.markdown(f'<p class="center-text">📅 {forecast["date"]}: 🌧️ {forecast["rain"]} ملم</p>', unsafe_allow_html=True)
                if not any(f["rain"] > 0 for f in forecasts):
                    st.info("☀️ لا توجد توقعات بهطول أمطار.")
            else:
                st.error("تعذر الحصول على البيانات.")

# رفع الصورة
st.markdown("---")
st.markdown('<p class="center-text">🌿 ارفع صورة النبات لتحليلها:</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📸 اختر صورة:", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with st.spinner("🔍 جارٍ تحليل الصورة..."):
        st.image(uploaded_file, caption="📸 الصورة المرفوعة", use_container_width=True)
        base64_image = convert_image_to_base64(uploaded_file)
        if base64_image:
            response = send_image_to_plant_id(base64_image, PLANT_API_KEY)
            if response:
                classification, plant_name, probability, health = display_results(response)
                st.markdown(f'<p class="center-text">🌿 **النبات:** {plant_name}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="center-text">🔢 **احتمالية التصنيف:** {probability:.5f}%</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="center-text">🩺 **الصحة:** {"✅ صحي" if health else "❌ غير صحي"}</p>', unsafe_allow_html=True)

                # استدعاء ChatGPT لتحليل النبات بناءً على البيانات
                with st.spinner("💬 جاري تحليل النبات ..."):
                    analysis_data = f"اسم النبات: {plant_name}, احتمالية التصنيف: {probability:.2f}%, الموقع: ({lat}, {lon})"
                    chat_response = chat(analysis_data, f"الموقع: ({lat}, {lon})")
                    st.markdown("### 📝 توصيات ChatGPT:")
                    st.write(chat_response)
            else:
                st.error("فشل في تحليل الصورة.")
