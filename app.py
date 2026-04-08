import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
from twilio.rest import Client  # <--- إضافة مكتبة تويليو

# --- إعدادات Twilio (احصل عليها من حسابك في Twilio Console) ---
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxx' 
TWILIO_AUTH_TOKEN = 'your_auth_token_here'
TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886' # رقم الساند بوكس الافتراضي
YOUR_WHATSAPP_NUMBER = 'whatsapp:+9665XXXXXXXX' # رقمك الشخصي (يجب أن يبدأ بـ +)

# --- دالة إرسال الواتساب ---
def send_whatsapp_alert(ticket_id, name, dept, issue):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_body = (
            f"🎫 *طلب دعم جديد*\n\n"
            f"*رقم الطلب:* {ticket_id}\n"
            f"*المرسل:* {name}\n"
            f"*القسم:* {dept}\n"
            f"*المشكلة:* {issue}"
        )
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=message_body,
            to=YOUR_WHATSAPP_NUMBER
        )
        return True
    except Exception as e:
        print(f"خطأ في إرسال الواتساب: {e}")
        return False

# --- إعدادات قاعدة البيانات (نفس الكود السابق) ---
DB_FILE = "tickets_db.csv"
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["ID", "Name", "Department", "Issue", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- الواجهة ---
st.set_page_config(page_title="نظام الدعم الفني", layout="wide")
df = load_data()

menu = ["إرسال طلب جديد", "لوحة تحكم الدعم الفني"]
choice = st.sidebar.selectbox("اختر الواجهة", menu)

if choice == "إرسال طلب جديد":
    st.header("📝 تقديم طلب دعم")
    with st.form("ticket_form"):
        name = st.text_input("الاسم الكامل")
        dept = st.selectbox("الموقع", ["مستشفى الدرب العام"])
        issue = st.text_area("القسم")
        issue = st.text_area("وصف المشكلة")
        submit = st.form_submit_button("إرسال الطلب")
        
        if submit:
            if name and issue:
                new_id = len(df) + 1001
                new_row = {
                    "ID": new_id, "Name": name, "Department": dept, 
                    "Issue": issue, "Status": "جديد", 
                    "Reply": "لا يوجد رد", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                
                # --- تشغيل تنبيه الواتساب هنا ---
                with st.spinner('جاري إرسال تنبيه واتساب للفريق...'):
                    success = send_whatsapp_alert(new_id, name, dept, issue)
                    if success:
                        st.success(f"تم إرسال الطلب بنجاح! رقم الطلب: {new_id}. تم تنبيه الفريق عبر واتساب ✅")
                    else:
                        st.warning(f"تم حفظ الطلب برقم {new_id}، ولكن فشل إرسال تنبيه الواتساب.")
            else:
                st.error("يرجى تعبئة الحقول المطلوبة.")

# (باقي كود لوحة التحكم يظل كما هو دون تغيير)
else:
    st.info("سجل دخولك من القائمة الجانبية لإدارة الطلبات.")
    # ... كود لوحة التحكم السابق ...
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
