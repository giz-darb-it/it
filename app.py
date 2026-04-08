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

# --- الإعدادات وقاعدة البيانات (نفس الكود السابق) ---
DB_FILE = "tickets_db.csv"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "123123"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["ID", "Name", "Department", "Issue", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# دالة تحويل البيانات إلى Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

st.set_page_config(page_title="نظام الدعم الفني", layout="wide")
df = load_data()

# --- القائمة الجانبية ---
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
        if submit and name and issue:
            new_id = len(df) + 1001
            new_row = {"ID": new_id, "Name": name, "Department": dept, "Issue": issue, "Status": "جديد", "Reply": "لا يوجد رد", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"تم الإرسال بنجاح! رقم الطلب: {new_id}")

else:
    st.header("🛠️ لوحة تحكم الإدارة")
    user = st.sidebar.text_input("اسم المستخدم")
    passwd = st.sidebar.text_input("كلمة المرور", type="password")

    if user == ADMIN_USER and passwd == ADMIN_PASSWORD:
        st.success("مرحباً بك في لوحة التحكم")

        # --- أزرار التحميل والتصدير ---
        col1, col2 = st.columns(2)
        
        with col1:
            # تحميل Excel
            excel_data = to_excel(df)
            st.download_button(
                label="📥 تحميل قائمة الطلبات (Excel)",
                data=excel_data,
                file_name=f"Technical_Support_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            # خيار طباعة PDF (طريقة بسيطة تعتمد على متصفح المستخدم)
            if st.button("🖨️ تجهيز ملف للطباعة / PDF"):
                st.info("نصيحة: بعد ظهور الجدول، اضغط Ctrl + P واختر حفظ كـ PDF")
                st.table(df) # عرض الجدول بشكل ثابت يسهل طباعته

        st.divider()

        # --- عرض القائمة مع إمكانية البحث ---
        st.subheader("🔍 قائمة الطلبات الواردة")
        search = st.text_input("ابحث عن موظف أو قسم...")
        if search:
            display_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        else:
            display_df = df

        st.dataframe(display_df, use_container_width=True)

        st.divider()

        # --- نظام الرد (نفس السابق) ---
        pending_ids = df[df['Status'] != "تم الحل"]['ID'].tolist()
        if pending_ids:
            st.subheader("✍️ الرد على الطلبات المعلقة")
            selected_id = st.selectbox("رقم الطلب", pending_ids)
            reply_text = st.text_area("الرد الفني")
            new_status = st.selectbox("الحالة", ["قيد المعالجة", "تم الحل"])
            
            if st.button("تحديث"):
                idx = df[df['ID'] == selected_id].index[0]
                df.at[idx, 'Reply'] = reply_text
                df.at[idx, 'Status'] = new_status
                save_data(df)
                st.success("تم التحديث!")
                st.rerun()
    else:
        st.warning("يرجى إدخال بيانات الإدارة")