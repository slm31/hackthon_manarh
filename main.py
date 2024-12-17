import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from Analisys import send_image_to_plantnet
from ChatGpt import chat

# مفاتيح API




plantnet_api_key = st.secrets["plantnet_api_key"]
WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
def get_rain_forecast(api_key, lat, lon):
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {"key": api_key, "q": f"{lat},{lon}", "days": 3}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {"date": day["date"], "rain": day["day"]["totalprecip_mm"]}
            for day in data["forecast"]["forecastday"]
        ]
    return []

# عرض الخريطة
st.title("🌿 مشروع مكافحة التصحر")
st.write("**حدد الموقع وابدأ تحليلك!**")

map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=700, height=500)

if map_data and "last_clicked" in map_data["last_clicked"]:
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    st.success(f"📍 الإحداثيات: ({lat}, {lon})")

    # زر جلب توقعات الأمطار
    if st.button("☔ جلب توقعات هطول الأمطار"):
        st.write("### ☁️ توقعات الأمطار")
        forecast = get_rain_forecast(WEATHER_API_KEY, lat, lon)
        if forecast:
            for day in forecast:
                st.write(f"📅 {day['date']}: {day['rain']} ملم")
        else:
            st.warning("❌ تعذر جلب توقعات الأمطار.")
    
    # رفع صورة النبات
    st.write("### 🌿 تحليل صورة النبات")
    uploaded_file = st.file_uploader("📸 اختر صورة:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="📸 الصورة المرفوعة", use_container_width=True)
