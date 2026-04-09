import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# محاولة استيراد مكتبة التحديث التلقائي
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

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
st.set_page_config(page_title="Support System", layout="wide")

if 'lang_choice' not in st.session_state:
    st.session_state.lang_choice = "العربية"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# تبديل اللغة (EN | AR)
col_spacer, col_en, col_ar = st.columns([10, 0.8, 0.8])
with col_en:
    if st.button("EN", use_container_width=True):
        st.session_state.lang_choice = "English"; st.rerun()
with col_ar:
    if st.button("AR", use_container_width=True):
        st.session_state.lang_choice = "العربية"; st.rerun()

lang = st.session_state.lang_choice

# --- 3. قاموس النصوص ---
t = {
    "العربية": {
        "title": "نظام الدعم الفني", "user_tab": "طلب دعم جديد", "admin_tab": "لوحة الإدارة",
        "name": "👤 الاسم الكامل", "empid": "🆔 الرقم الوظيفي", "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم", "desc": "📝 وصف المشكلة", "submit": "إرسال الطلب",
        "stats_total": "إجمالي الطلبات", "stats_pending": "قيد المعالجة", "stats_done": "تم الحل",
        "search": "🔍 بحث...", "login_btn": "دخول", "pass_field": "كلمة المرور", "user_field": "المستخدم",
        "status_label": "تحديث الحالة", "reply_label": "الرد الرسمي", "update_btn": "تحديث البيانات",
        "status_options": ["جديد", "قيد المعالجة", "تم الحل", "لم يتم الحل"],
        "del_btn": "🗑️ حذف", "dir": "rtl"
    },
    "English": {
        "title": "Support System", "user_tab": "New Ticket", "admin_tab": "Dashboard",
        "name": "👤 Full Name", "empid": "🆔 Employee ID", "email": "📧 Email",
        "dept": "🏢 Department", "desc": "📝 Description", "submit": "Submit",
        "stats_total": "Total", "stats_pending": "In Progress", "stats_done": "Resolved",
        "search": "🔍 Search...", "login_btn": "Login", "pass_field": "Password", "user_field": "User",
        "status_label": "Status Update", "reply_label": "Official Reply", "update_btn": "Update Ticket",
        "status_options": ["New", "In Progress", "Resolved", "Not Resolved"],
        "del_btn": "🗑️ Delete", "dir": "ltr"
    }
}

# --- 4. التنسيق (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ font-family: 'Tajawal', sans-serif; direction: {t[lang]['dir']}; }}
    h1 {{ font-size: 3rem !important; font-weight: 900 !important; color: #4361ee !important; text-align: center; }}
    label, p {{ font-size: 1.4rem !important; font-weight: 700 !important; }}
    .stButton>button {{ font-size: 1.3rem !important; font-weight: 800 !important; border-radius: 10px !important; }}
    [data-testid="stSidebar"] {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 5. القائمة العلوية ---
tab_user, tab_admin = st.tabs([f"🏠 {t[lang]['user_tab']}", f"📊 {t[lang]['admin_tab']}"])

# --- 6. واجهة المستخدم ---
with tab_user:
    st.markdown(f"<h1>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input(t[lang]["name"])
        empid = c1.text_input(t[lang]["empid"])
        email = c2.text_input(t[lang]["email"])
        dept = c2.text_input(t[lang]["dept"])
        issue_desc = st.text_area(t[lang]["desc"])
        if st.form_submit_button(t[lang]["submit"]):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "Status": t[lang]["status_options"][0], "Reply": "---", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df); st.success(f"ID: {new_id}")

# --- 7. واجهة الإدارة ---
with tab_admin:
    if st_autorefresh:
        st_autorefresh(interval=10000, key="admin_ref")

    # سطر تسجيل الدخول (المستخدم، كلمة المرور، زر الدخول في صف واحد)
    if not st.session_state.logged_in:
        st.markdown(f"### {t[lang]['admin_tab']}")
        l_col1, l_col2, l_col3 = st.columns([1.5, 1.5, 0.6])
        a_user = l_col1.text_input(t[lang]["user_field"], key="u_field")
        a_pass = l_col2.text_input(t[lang]["pass_field"], type="password", key="p_field")
        st.write("##") # موازنة الزر مع الحقول
        if l_col3.button(t[lang]["login_btn"], use_container_width=True):
            if a_user == ADMIN_USER and a_pass == ADMIN_PASSWORD:
                st.session_state.logged_in = True; st.rerun()
            else: st.error("❌")
    
    if st.session_state.logged_in:
        # الإحصائيات
        m1, m2, m3 = st.columns(3)
        m1.metric(t[lang]["stats_total"], len(df))
        m2.metric(t[lang]["stats_pending"], len(df[df['Status'].isin([t[lang]["status_options"][1], "New", "جديد"])]))
        m3.metric(t[lang]["stats_done"], len(df[df['Status'] == t[lang]["status_options"][2]]))
        
        st.divider()
        search = st.text_input(t[lang]["search"])
        st.dataframe(df, use_container_width=True)

        # إدارة الطلبات (الرد وتغيير الحالة)
        st.markdown("---")
        act_col1, act_col2 = st.columns([1.5, 1])
        
        all_ids = df['ID'].tolist()
        if all_ids:
            with act_col1:
                st.subheader("📝 " + t[lang]["reply_label"])
                sel_id = st.selectbox("ID", all_ids, key="sel_id")
                idx = df[df['ID'] == sel_id].index[0]
                
                # اختيار الحالة والرد
                c_stat, c_btn = st.columns([2, 1])
                new_status = c_stat.selectbox(t[lang]["status_label"], t[lang]["status_options"], index=0)
                new_reply = st.text_area(t[lang]["reply_label"], value=df.at[idx, 'Reply'], key="rep_area")
                
                if st.button(t[lang]["update_btn"], use_container_width=True):
                    df.at[idx, 'Status'] = new_status
                    df.at[idx, 'Reply'] = new_reply
                    save_data(df); st.success("OK"); st.rerun()

            with act_col2:
                st.subheader("🗑️")
                d_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids, key="d_sel")
                if st.button(t[lang]["del_btn"], use_container_width=True):
                    if d_id:
                        df = df[df['ID'] != d_id]
                        save_data(df); st.rerun()
