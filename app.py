import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from Analisys import convert_image_to_base64, send_image_to_plant_id, display_results
from ChatGpt import chat

# مفاتيح API
PLANT_API_KEY = st.secrets["PLANT_API_KEY"]
WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]


def get_rain_forecast(api_key, lat, lon):
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {"key": api_key, "q": f"{lat},{lon}", "days": 30, "aqi": "no", "alerts": "no"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            location_name = f"{data['location']['name']}, {data['location']['region']}, {data['location']['country']}"
            forecasts = []
            for day in data["forecast"]["forecastday"]:
                date = day["date"]
                rain_amount = round(day["day"]["totalprecip_mm"], 5)
                forecasts.append({"date": date, "rain": rain_amount})
            return location_name, forecasts
        else:
            return "تعذر الحصول على البيانات", []
    except Exception as e:
        return f"حدث خطأ: {e}", []

# دالة لتحويل الإحداثيات إلى اسم الموقع
def get_location_from_coordinates(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "MyApp/1.0 (contact: example@email.com)"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            city = address.get("city", address.get("town", address.get("village", "غير معروف")))
            state = address.get("state", "")
            country = address.get("country", "")
            return f"{city}, {state}, {country}"
        else:
            return "تعذر الحصول على الموقع"
    except Exception as e:
        return f"حدث خطأ: {e}"

# تحسين التصميم وتكبير الخط
st.markdown("""
    <style>
        h1 {
            text-align: center;
            font-size: 60px !important; /* حجم العنوان */
            color: #4CAF50;
        }
        h2 {
            text-align: center;
            font-size: 50px !important; /* حجم العنوان الفرعي */
            color: #1E88E5;
        }
        .center-text {
            text-align: center;
            font-size: 20px;
            font-weight: bold;
        }
        .rain-text {
            font-size: 20px;
            color: #2E7D32;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# عناوين الصفحة
st.markdown("<h1>🌟هاكثون منارة حائل</h1>", unsafe_allow_html=True)
st.markdown("<h2>🏔️فريق سلمى</h2>", unsafe_allow_html=True)

# الخطوة الأولى: الخريطة
st.markdown("---")
st.markdown('<p class="center-text">🌍 الخطوة الأولى: حدد موقع على الخريطة لجلب توقعات هطول الأمطار.</p>', unsafe_allow_html=True)

# خريطة تفاعلية
map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=700, height=500)

# التحقق من الموقع
if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    st.markdown(f'<p class="center-text">📍 الإحداثيات المختارة: ({lat:.6f}, {lon:.6f})</p>', unsafe_allow_html=True)

    # جلب توقعات الأمطار
    if st.button("☁️ عرض توقعات الأمطار"):
        with st.spinner("⏳ جاري جلب بيانات هطول الأمطار..."):
            location_name, rain_forecast = get_rain_forecast(WEATHER_API_KEY, lat, lon)
            if rain_forecast:
                st.markdown(f'<p class="center-text rain-text">📍 الموقع: {location_name}</p>', unsafe_allow_html=True)
                for forecast in rain_forecast:
                    if forecast['rain'] > 0:
                        st.markdown(f'<p class="rain-text">📅 التاريخ: {forecast["date"]} - 🌧️ كمية الأمطار: {forecast["rain"]:.5f} ملم</p>', unsafe_allow_html=True)
                if not any(f['rain'] > 0 for f in rain_forecast):
                    st.info("☀️ لا توجد توقعات بهطول أمطار.")

    # الخطوة الثانية: تحميل صورة النبات
    st.markdown("---")
    st.markdown('<p class="center-text">🌿 الخطوة الثانية: ارفع صورة النبات لتحليلها.</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("🌱 ارفع صورة النبات", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        with st.spinner("🔍 جاري تحليل الصورة..."):
            st.image(uploaded_file, caption="📸 الصورة المرفوعة", use_column_width=True)
            base64_image = convert_image_to_base64(uploaded_file)
            if base64_image:
                response = send_image_to_plant_id(base64_image, PLANT_API_KEY)
                if response:
                    classification, plant_name, probability, health = display_results(response)
                    st.markdown(f'<p class="center-text">🌿 **اسم النبات:** {plant_name}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="center-text">🔢 **احتمالية التصنيف:** {probability:.5f}%</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="center-text">🩺 **صحة النبات:** {"✅ صحي" if health else "❌ غير صحي"}</p>', unsafe_allow_html=True)

                    location_name = get_location_from_coordinates(lat, lon)
                    st.markdown(f'<p class="center-text">📍 **الموقع:** {location_name}</p>', unsafe_allow_html=True)

                    # تحليل الموطن باستخدام ChatGPT
                    st.write("📝 **تحليل إضافي للموطن الأصلي...**")
                    analysis_data = f"اسم النبات: {plant_name}, الاحتمالية: {probability:.5f}%, الموقع: {location_name}"
                    chat_response = chat(analysis_data, f"الموقع: {location_name}")
                    st.write("📊 **بيانات التحليل:**")
                    st.write(chat_response)
                else:
                    st.error("❌ فشل في تحليل الصورة.")
            else:
                st.error("❌ فشل في تحويل الصورة إلى Base64.")
else:
    st.warning("⚠️ يرجى تحديد موقع على الخريطة قبل المتابعة.")
