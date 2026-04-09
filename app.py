import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
from streamlit_autorefresh import st_autorefresh

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

l_col1, l_col2 = st.columns([8, 1])
with l_col2:
    current_lang = st.selectbox("🌐", ["العربية", "English"], label_visibility="collapsed")
    st.session_state.lang_choice = current_lang

lang = st.session_state.lang_choice

t = {
    "العربية": {
        "title": "نظام الدعم الفني", "user_tab": "طلب دعم جديد", "admin_tab": "لوحة الإدارة",
        "stats_total": "إجمالي الطلبات", "stats_pending": "تحت المعالجة", "stats_done": "تم الحل",
        "search": "🔍 بحث في الطلبات...", "reply_btn": "تحديث الحالة والرد", "del_btn": "حذف الطلب",
        "del_all_btn": "🗑️ حذف كافة البيانات", "delete_section": "⚙️ إدارة وحذف البيانات",
        "login": "🔐 دخول المشرف", "dir": "rtl", "align": "right"
    },
    "English": {
        "title": "Technical Support", "user_tab": "New Ticket", "admin_tab": "Admin Dashboard",
        "stats_total": "Total", "stats_pending": "Pending", "stats_done": "Resolved",
        "search": "🔍 Search...", "reply_btn": "Update & Reply", "del_btn": "Delete Ticket",
        "del_all_btn": "🗑️ Delete All", "delete_section": "⚙️ Data Management",
        "login": "🔐 Admin Login", "dir": "ltr", "align": "left"
    }
}

# --- 3. التنسيق المتقدم (تكبير وتعريض الخط) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@500;700;900&display=swap');
    
    /* الخط العام للتطبيق */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[lang]['dir']};
        text-align: {t[lang]['align']};
    }}

    /* تكبير نصوص العناوين */
    h1 {{ font-size: 3rem !important; font-weight: 900 !important; color: #4361ee !important; }}
    h2 {{ font-size: 2.5rem !important; font-weight: 800 !important; }}
    h3 {{ font-size: 1.8rem !important; font-weight: 700 !important; }}

    /* تكبير وتعريض نصوص الحقول والأسماء */
    label, .stMarkdown p {{
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #2b2d42 !important;
    }}

    /* تكبير نصوص الإدخال (Input) */
    input, textarea, [data-baseweb="select"] {{
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }}

    /* تكبير نصوص التبويبات العلوية */
    button[data-baseweb="tab"] p {{
        font-size: 1.5rem !important;
        font-weight: 800 !important;
    }}

    /* تكبير الإحصائيات (Metrics) */
    [data-testid="stMetricValue"] {{
        font-size: 2.5rem !important;
        font-weight: 900 !important;
    }}
    [data-testid="stMetricLabel"] p {{
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }}

    /* أزرار ضخمة وعريضة */
    .stButton>button {{
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 12px !important;
    }}

    [data-testid="stSidebar"] {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 4. القائمة العلوية ---
tab_user, tab_admin = st.tabs([f"🏠 {t[lang]['user_tab']}", f"📊 {t[lang]['admin_tab']}"])

# --- 5. واجهة المستخدم ---
with tab_user:
    st.markdown(f"<h1 style='text-align: center;'>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name" if lang=="English" else "الاسم")
            empid = st.text_input("ID" if lang=="English" else "الرقم الوظيفي")
        with c2:
            dept = st.text_input("Dept" if lang=="English" else "القسم")
            issue_desc = st.text_area("Desc" if lang=="English" else "الوصف")
        if st.form_submit_button("Submit"):
            new_id = str(len(df) + 1001)
            new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Department": dept, "Status": "New" if lang=="English" else "جديد", "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df); st.success(f"ID: {new_id}")

# --- 6. واجهة الإدارة ---
with tab_admin:
    st_autorefresh(interval=10000, key="datarefresh")
    st.markdown(f"<h2 style='text-align: center;'>{t[lang]['admin_tab']}</h2>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.expander(t[lang]["login"], expanded=True):
            admin_user = st.text_input("Username", key="u_adm")
            admin_pass = st.text_input("Password", type="password", key="p_adm")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric(t[lang]["stats_total"], len(df))
        m2.metric(t[lang]["stats_pending"], len(df[df['Status'].isin(["New", "جديد", "Pending", "قيد المعالجة"])]))
        m3.metric(t[lang]["stats_done"], len(df[df['Status'].isin(["Resolved", "تم الحل"])]))
        
        st.divider()
        st.dataframe(df, use_container_width=True)
        
        # قسم التحكم
        st.markdown("---")
        col_reply, col_del = st.columns(2)
        all_ids = df['ID'].tolist()
        
        with col_reply:
            st.subheader(t[lang]["reply_btn"])
            if all_ids:
                selected_id = st.selectbox("ID", all_ids, key="sel_rep")
                if st.button(t[lang]["reply_btn"], key="btn_upd"):
                    pass # منطق التحديث

        with col_del:
            st.subheader(t[lang]["delete_section"])
            d_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids, key="sel_del")
            if st.button(t[lang]["del_btn"], key="btn_del"):
                if d_id:
                    df = df[df['ID'] != str(d_id)]
                    save_data(df); st.rerun()
