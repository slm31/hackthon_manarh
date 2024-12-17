import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from Analisys import send_image_to_plantnet
from ChatGpt import chat

# مفاتيح API
plantnet_api_key = st.secrets.get("plantnet_api_key")
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY")

# إعداد CSS للاستجابة (Responsive)
st.markdown(
    """
    <style>
    body {
        margin: 0;
        padding: 0;
    }
    .centered {
        text-align: center;
    }
    .highlight {
        font-size: 20px;
        color: #4CAF50;
    }
    .subtitle {
        font-size: 16px;
        color: #666;
    }
    .small-text {
        font-size: 12px;
        color: #555;
    }
    .footer {
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 12px;
        color: #aaa;
    }
    .responsive-map {
        width: 100% !important;
        height: 300px !important;
    }
    h1, h2, h3 {
        margin-top: 0;
        margin-bottom: 10px;
    }
    @media screen and (max-width: 768px) {
        .highlight {
            font-size: 18px;
        }
        .subtitle {
            font-size: 14px;
        }
        .small-text {
            font-size: 10px;
        }
        .responsive-map {
            height: 250px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# عنوان التطبيق
st.markdown("<h1 class='centered highlight'>🌟 هاكثون منارة حائل 🌟</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='centered subtitle'>⛰️ فريق سلمى ⛰️</h2>", unsafe_allow_html=True)
st.markdown("<h3 class='centered'>🗺️ حدد الموقع وابدأ تحليلك! 🌍</h3>", unsafe_allow_html=True)

# خريطة تفاعلية بحجم يتجاوب مع الشاشة
map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width="100%", height=350, returned_objects=["last_clicked"])

# التحقق من الموقع المختار
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
            params = {"key": api_key, "q": f"{lat},{lon}", "days": 7}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return [
                    {"date": day["date"], "rain": day["day"]["totalprecip_mm"]}
                    for day in data["forecast"]["forecastday"]
                ]
            return []

        forecast = get_rain_forecast(WEATHER_API_KEY, lat, lon)
        if forecast:
            for day in forecast:
                st.markdown(f"<p class='small-text'>📅 {day['date']}: {day['rain']} ملم</p>", unsafe_allow_html=True)
        else:
            st.warning("❌ تعذر جلب توقعات الأمطار.")

# نص "اختر صورة" فوق أداة الرفع
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 10px;'>
        <span style='font-size: 18px; font-weight: bold; color: #4CAF50;'>📸 اختر صورة:</span>
    </div>
    """,
    unsafe_allow_html=True
)

# أداة رفع الصورة
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="unique_file_uploader")

# عرض الصورة وتحليلها
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
        else:
            st.error("❌ تعذر تحليل الصورة. حاول مجددًا.")

# تذييل الصفحة
st.markdown("<div class='footer'>Hakathon Manarah - Team Salma 🌟</div>", unsafe_allow_html=True)
