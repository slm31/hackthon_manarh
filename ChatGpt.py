import time
from openai import OpenAI
import streamlit as st

# استخدام مفتاح OpenAI API من Streamlit Secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_6oadhNqT43dLfCQVhOndBvnD"  # معرف المساعد الخاص بك

# إنشاء عميل OpenAI باستخدام المفتاح
client = OpenAI(api_key=OPENAI_API_KEY)

# دالة الدردشة مع ChatGPT
def chat(analisys, location):
    try:
        # إنشاء جلسة جديدة مع رسائل المستخدم
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"تحليل النبات: {analisys}. الموقع: {location}."
                }
            ]
        )

        # بدء تشغيل مساعد OpenAI
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
        print(f"👉 Run Created: {run.id}")

        # انتظار انتهاء التشغيل
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"🏃 Run Status: {run.status}")
            time.sleep(1)

        print(f"🏁 Run Completed!")

        # جلب الرد النهائي من ChatGPT
        message_response = client.beta.threads.messages.list(thread_id=thread.id)
        messages = message_response.data
        latest_message = messages[0]

        # إعادة نص الرد النهائي
        return latest_message.content[0].text.value

    except Exception as e:
        print(f"❌ Error during ChatGPT API call: {e}")
        return "فشل في الحصول على البيانات."

