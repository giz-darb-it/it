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

# --- 3. نظام اختيار اللغة ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'AR'

lang_col1, lang_col2, lang_col3 = st.columns([4, 1, 1])
with lang_col2:
    if st.button("AR", use_container_width=True, key="btn_ar"):
        st.session_state.lang = 'AR'; st.rerun()
with lang_col3:
    if st.button("EN", use_container_width=True, key="btn_en"):
        st.session_state.lang = 'EN'; st.rerun()

L = st.session_state.lang

t = {
    'AR': {
        'user_tab': "طلب دعم جديد", 'admin_tab': "لوحة الإدارة",
        'stats_total': "إجمالي الطلبات", 'stats_pending': "قيد المعالجة", 'stats_done': "تم الحل",
        'manage': "⚙️ إدارة طلب محدد", 'del_btn': "🗑️ حذف الطلب", 'update_btn': "تحديث الحالة والرد",
        'status_opt': ["جديد", "قيد المعالجة", "تم الحل"], 'search': "🔍 بحث..."
    },
    'EN': {
        'user_tab': "New Ticket", 'admin_tab': "Admin Dashboard",
        'stats_total': "Total Tickets", 'stats_pending': "Pending", 'stats_done': "Resolved",
        'manage': "⚙️ Manage Ticket", 'del_btn': "🗑️ Delete Ticket", 'update_btn': "Update Status/Reply",
        'status_opt': ["New", "In Progress", "Resolved"], 'search': "🔍 Search..."
    }
}

# --- 4. القائمة العلوية ---
tab_user, tab_admin = st.tabs([t[L]["user_tab"], t[L]["admin_tab"]])

df = load_data()

# --- 5. واجهة المستخدم ---
with tab_user:
    st.markdown(f"<h1 style='text-align: center;'>{'نظام الدعم الفني' if L=='AR' else 'IT Support'}</h1>", unsafe_allow_html=True)
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name" if L=='EN' else "الاسم")
        empid = c1.text_input("ID" if L=='EN' else "الرقم الوظيفي")
        email = c2.text_input("Email" if L=='EN' else "الايميل")
        dept = c2.text_input("Dept" if L=='EN' else "القسم")
        issue_desc = st.text_area("Description" if L=='EN' else "الوصف")
        if st.form_submit_button("Submit" if L=='EN' else "إرسال"):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueType": "General", "IssueDesc": issue_desc, "Status": t[L]['status_opt'][0], "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df); st.success(f"ID: {new_id}"); st.rerun()

# --- 6. واجهة الإدارة (مع الإحصائيات) ---
with tab_admin:
    st.markdown(f"<h2 style='text-align: center;'>{t[L]['admin_tab']}</h2>", unsafe_allow_html=True)
    l1, l2 = st.columns(2)
    admin_user = l1.text_input("User", key="au")
    admin_pass = l2.text_input("Pass", type="password", key="ap")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        st.divider()
        
        # --- قسم الإحصائيات (Metrics) ---
        total_count = len(df)
        # نحسب قيد المعالجة (سواء كان بالعربي أو الإنجليزي)
        pending_count = len(df[df['Status'].isin(["New", "In Progress", "جديد", "قيد المعالجة"])])
        # نحسب المكتمل
        resolved_count = len(df[df['Status'].isin(["Resolved", "تم الحل"])])

        m1, m2, m3 = st.columns(3)
        m1.metric(t[L]['stats_total'], total_count)
        m2.metric(t[L]['stats_pending'], pending_count, delta_color="inverse")
        m3.metric(t[L]['stats_done'], resolved_count)
        
        st.divider()

        # شاشة عرض البيانات والبحث
        search = st.text_input(t[L]["search"])
        f_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df
        st.dataframe(f_df, use_container_width=True)
        st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)

        # إدارة الطلبات
        st.markdown(f"### {t[L]['manage']}")
        all_ids = df['ID'].tolist()
        if all_ids:
            sel_id = st.selectbox("Select ID", all_ids)
            idx = df[df['ID'] == sel_id].index[0]
            
            c_act1, c_act2 = st.columns(2)
            new_status = c_act1.selectbox(t[L]['status'], t[L]['status_opt'], index=t[L]['status_opt'].index(df.at[idx, 'Status']) if df.at[idx, 'Status'] in t[L]['status_opt'] else 0)
            reply_txt = c_act2.text_area("Reply", value=df.at[idx, 'Reply'])
            
            b1, b2 = st.columns(2)
            if b1.button(t[L]["update_btn"], use_container_width=True):
                df.at[idx, 'Status'] = new_status
                df.at[idx, 'Reply'] = reply_txt
                save_data(df); st.rerun()
            if b2.button(t[L]["del_btn"], use_container_width=True):
                df = df[df['ID'] != sel_id]
                save_data(df); st.rerun()
