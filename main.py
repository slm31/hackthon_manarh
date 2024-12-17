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
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return [
                {"date": day["date"], "rain": day["day"]["totalprecip_mm"]}
                for day in data["forecast"]["forecastday"]
            ]
        return []
    except Exception as e:
        st.error(f"❌ خطأ في جلب بيانات الطقس: {e}")
        return []

# عرض الخريطة
st.title("🌿 مشروع مكافحة التصحر")
st.write("**حدد الموقع وابدأ تحليلك!**")

map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=700, height=500)

if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    st.success(f"📍 الإحداثيات: ({lat}, {lon})")

    # جلب توقعات الأمطار
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

        # تحليل الصورة عبر PlantNet
        with st.spinner("🔍 جاري تحليل الصورة..."):
            result = send_image_to_plantnet(uploaded_file, plantnet_api_key)

            if result:
                # عرض نتائج تحليل الصورة
                st.write(f"**🔬 اسم النبات العلمي:** {result['scientific_name']}")
                st.write(f"**🌱 الأسماء الشائعة:** {', '.join(result['common_names'])}")
                st.write(f"**📊 نسبة التطابق:** {result['score']}%")
                st.write(f"**🔍 الجنس:** {result['genus']}")
                st.write(f"**🌳 العائلة:** {result['family']}")

                # إرسال البيانات إلى ChatGPT
                with st.spinner("💬 جاري تحليل البيانات بواسطة الذكاء الاصطناعي..."):
                    analysis_data = f"اسم النبات: {result['scientific_name']}, نسبة التطابق: {result['score']}%, الموقع: ({lat}, {lon})"
                    chat_response = chat(analysis_data, f"الموقع: ({lat}, {lon})")
                    st.write("### 💡 التحليل الإضافي:")
                    st.write(chat_response)
            else:
                st.error("❌ تعذر تحليل الصورة. حاول مجددًا.")
