import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# --- 1. الإعدادات وقاعدة البيانات ---
DB_FILE = "tickets_db.csv"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "Dit@123123"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype=str).fillna("")
    return pd.DataFrame(columns=["ID", "Name", "EmpID", "Email", "Department", "IssueType", "IssueDesc", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="Support System", layout="centered")

# --- 3. نظام اختيار اللغة في الأعلى ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'AR'

# حاوية علوية لأزرار اللغة
lang_col1, lang_col2, lang_col3 = st.columns([4, 1, 1])
with lang_col2:
    if st.button("AR", use_container_width=True, key="btn_ar"):
        st.session_state.lang = 'AR'
        st.rerun()
with lang_col3:
    if st.button("EN", use_container_width=True, key="btn_en"):
        st.session_state.lang = 'EN'
        st.rerun()

L = st.session_state.lang

t = {
    'AR': {
        'title': "نظام الدعم الفني",
        'sub': "يرجى تعبئة النموذج أدناه وسيتم الرد عليكم قريباً",
        'name': "👤 الاسم الكامل",
        'id': "🆔 الرقم الوظيفي",
        'email': "📧 البريد الإلكتروني",
        'dept': "🏢 القسم",
        'type': "⚠️ نوع المشكلة",
        'desc': "📝 وصف المشكلة بالتفصيل",
        'submit': "إرسال الطلب",
        'dir': "rtl",
        'align': "right",
        'user_tab': "طلب دعم جديد",
        'admin_tab': "لوحة الإدارة",
        'success': "✅ تم الإرسال بنجاح! رقم الطلب: ",
        'error': "⚠️ يرجى تعبئة الحقول الأساسية"
    },
    'EN': {
        'title': "IT Support System",
        'sub': "Please fill out the form below and we will reply soon",
        'name': "👤 Full Name",
        'id': "🆔 Employee ID",
        'email': "📧 Email",
        'dept': "🏢 Department",
        'type': "⚠️ Issue Type",
        'desc': "📝 Issue Description",
        'submit': "Submit Ticket",
        'dir': "ltr",
        'align': "left",
        'user_tab': "New Ticket",
        'admin_tab': "Admin Dashboard",
        'success': "✅ Submitted successfully! ID: ",
        'error': "⚠️ Please fill all required fields"
    }
}

# --- 4. القائمة العلوية للتنقل (Tabs) ---
tab_user, tab_admin = st.tabs([t[L]["user_tab"], t[L]["admin_tab"]])

# --- 5. CSS المحدث للواجهة العلوية ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[L]['dir']};
        background-color: #f8f9fa;
    }}

    /* تصميم أزرار التبويبات العلوية */
    button[data-baseweb="tab"] {{
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }}

    [data-testid="stForm"] {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: none;
        margin-top: 10px;
    }}

    .stButton>button {{
        border-radius: 10px !important;
        height: 3em !important;
        font-weight: bold !important;
    }}

    input, textarea, [data-baseweb="select"] {{
        text-align: {t[L]['align']} !important;
    }}
    
    /* إخفاء القائمة الجانبية تماماً إذا لم نعد نحتاجها */
    [data-testid="stSidebar"] {{
        display: none;
    }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 6. محتوى الصفحات بناءً على التبويب المختار ---

# الصفحة الأولى: واجهة المستخدم
with tab_user:
    st.markdown(f"<h1 style='text-align: center; color: #1e3a8a; margin-top:20px;'>{t[L]['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #6c757d;'>{t[L]['sub']}</p>", unsafe_allow_html=True)
    
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(t[L]["name"])
            empid = st.text_input(t[L]["id"])
        with c2:
            email = st.text_input(t[L]["email"])
            dept = st.text_input(t[L]["dept"])
        
        issue_type = st.selectbox(t[L]["type"], ["Hardware", "Software", "Network", "Other"] if L == 'EN' else ["أجهزة", "أنظمة", "شبكات", "أخرى"])
        issue_desc = st.text_area(t[L]["desc"], height=100)
        
        if st.form_submit_button(t[L]["submit"]):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {
                    "ID": new_id, "Name": name, "EmpID": empid, "Email": email, 
                    "Department": dept, "IssueType": issue_type, "IssueDesc": issue_desc, 
                    "Status": "New" if L == 'EN' else "جديد", "Reply": "No reply", 
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"{t[L]['success']} {new_id}")
            else:
                st.error(t[L]["error"])

# الصفحة الثانية: واجهة الإدارة
with tab_admin:
    st.markdown(f"<h2 style='text-align: center; margin-top:20px;'>{t[L]['admin_tab']}</h2>", unsafe_allow_html=True)
    
    # نموذج تسجيل دخول بسيط في الأعلى
    login_col1, login_col2 = st.columns(2)
    with login_col1:
        admin_user = st.text_input("User", key="admin_user_top")
    with login_col2:
        admin_pass = st.text_input("Pass", type="password", key="admin_pass_top")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        st.divider()
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)
    else:
        st.info("الرجاء تسجيل الدخول للمتابعة" if L == 'AR' else "Please login to view dashboard")
