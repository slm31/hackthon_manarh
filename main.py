# عرض الخريطة
st.title("🌿 مشروع مكافحة التصحر")
st.write("**حدد الموقع وابدأ تحليلك!**")

map_center = [25.0, 45.0]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=700, height=500)

if map_data and "last_clicked" in map_data:  # التحقق من وجود last_clicked
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"📍 الإحداثيات: ({lat:.6f}, {lon:.6f})")

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
else:
    st.warning("⚠️ يرجى تحديد موقع على الخريطة أولاً.")

