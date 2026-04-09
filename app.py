import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# --- 1. الإعدادات وقاعدة البيانات ---
DB_FILE = "tickets_db.csv"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "123123"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["ID", "Name", "EmpID", "Email", "Department", "IssueType", "IssueDesc", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- 2. إعدادات الصفحة واللغة ---
st.set_page_config(page_title="Support System | نظام الدعم", layout="wide")

# اختيار اللغة من القائمة الجانبية
lang = st.sidebar.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English"])

# قاموس الترجمة الكامل
t = {
    "العربية": {
        "title": "طلب الدعم الفني",
        "subtitle": "يرجى تعبئة النموذج أدناه وسيتم الرد عليكم في أقرب وقت",
        "name": "👤 الاسم الكامل",
        "empid": "🆔 الرقم الوظيفي",
        "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم (كتابة)",
        "type": "⚠️ نوع المشكلة",
        "desc": "📝 وصف المشكلة بالتفصيل",
        "submit": "إرسال الطلب",
        "admin_tab": "لوحة الإدارة",
        "user_tab": "طلب دعم جديد",
        "success": "✅ تم إرسال طلبك بنجاح! رقم المتابعة: ",
        "error": "⚠️ يرجى ملء كافة الحقول الأساسية",
        "login": "🔐 تسجيل دخول المشرف",
        "user_field": "اسم المستخدم",
        "pass_field": "كلمة المرور",
        "stats_total": "إجمالي الطلبات",
        "stats_pending": "تحت المعالجة",
        "stats_done": "تم الحل",
        "search": "🔍 بحث في الطلبات...",
        "reply_btn": "تحديث الحالة والرد",
        "dir": "rtl",
        "align": "right"
    },
    "English": {
        "title": "Technical Support Request",
        "subtitle": "Please fill out the form below and we will respond shortly",
        "name": "👤 Full Name",
        "empid": "🆔 Employee ID",
        "email": "📧 Email Address",
        "dept": "🏢 Department (Type here)",
        "type": "⚠️ Issue Type",
        "desc": "📝 Detailed Issue Description",
        "submit": "Submit Request",
        "admin_tab": "Admin Dashboard",
        "user_tab": "New Ticket",
        "success": "✅ Submitted successfully! Ticket ID: ",
        "error": "⚠️ Please fill all required fields",
        "login": "🔐 Admin Login",
        "user_field": "Username",
        "pass_field": "Password",
        "stats_total": "Total Tickets",
        "stats_pending": "Pending",
        "stats_done": "Resolved",
        "search": "🔍 Search Tickets...",
        "reply_btn": "Update & Reply",
        "dir": "ltr",
        "align": "left"
    }
}

# --- 3. تصميم الواجهة (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[lang]['dir']};
        text-align: {t[lang]['align']};
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4361ee;
        color: white;
        font-weight: bold;
        border: none;
    }}
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {{
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 4. القائمة الجانبية ---
st.sidebar.markdown("---")
choice = st.sidebar.radio(f"{'Menu' if lang=='English' else 'القائمة'}", [t[lang]["user_tab"], t[lang]["admin_tab"]])

# --- 5. واجهة المستخدم (ارسال طلب جديد) ---
if choice == t[lang]["user_tab"]:
    st.markdown(f"<h1 style='text-align: center; color: #4361ee;'>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{t[lang]['subtitle']}</p>", unsafe_allow_html=True)
    
    with st.container():
        with st.form("ticket_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(t[lang]["name"])
                empid = st.text_input(t[lang]["empid"])
                email = st.text_input(t[lang]["email"])
            with col2:
                # تم تغيير هذه الخانة من selectbox إلى text_input بناءً على طلبك
                dept = st.text_input(t[lang]["dept"]) 
                
                type_options = ["Hardware", "Software", "Network", "Other"] if lang == "English" else ["أجهزة", "أنظمة", "شبكات", "أخرى"]
                issue_type = st.selectbox(t[lang]["type"], type_options)
            
            issue_desc = st.text_area(t[lang]["desc"])
            submit = st.form_submit_button(t[lang]["submit"])
            
            if submit:
                if name and empid and dept and issue_desc:
                    new_id = len(df) + 1001
                    new_row = {
                        "ID": new_id, "Name": name, "EmpID": empid, "Email": email,
                        "Department": dept, "IssueType": issue_type, "IssueDesc": issue_desc,
                        "Status": "New" if lang == "English" else "جديد",
                        "Reply": "No reply" if lang == "English" else "لا يوجد رد",
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success(f"{t[lang]['success']} {new_id}")
                else:
                    st.error(t[lang]["error"])

# --- 6. واجهة الإدارة ---
else:
    st.markdown(f"<h1 style='text-align: center;'>{t[lang]['admin_tab']}</h1>", unsafe_allow_html=True)
    
    with st.sidebar.expander(t[lang]["login"]):
        admin_user = st.text_input(t[lang]["user_field"])
        admin_pass = st.text_input(t[lang]["pass_field"], type="password")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        c1, c2, c3 = st.columns(3)
        pending_count = len(df[df['Status'].isin(["New", "جديد", "Pending", "قيد المعالجة"])])
        done_count = len(df[df['Status'].isin(["Resolved", "تم الحل"])])
        
        c1.metric(t[lang]["stats_total"], len(df))
        c2.metric(t[lang]["stats_pending"], pending_count)
        c3.metric(t[lang]["stats_done"], done_count)

        st.divider()
        
        col_search, col_export = st.columns([3, 1])
        with col_search:
            search = st.text_input(t[lang]["search"])
        with col_export:
            st.write(" ") 
            st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx")

        display_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df
        st.dataframe(display_df, use_container_width=True)

        st.markdown("---")
        st.subheader(f"{'Process Ticket' if lang=='English' else 'معالجة الطلبات'}")
        
        all_ids = df['ID'].tolist()
        if all_ids:
            selected_id = st.selectbox("Ticket ID", all_ids)
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                reply_text = st.text_area(f"{'Official Reply' if lang=='English' else 'الرد الرسمي'}")
            with r_col2:
                status_options = ["Resolved", "Pending"] if lang == "English" else ["تم الحل", "قيد المعالجة"]
                new_status = st.selectbox(t[lang]["type"], status_options)
                if st.button(t[lang]["reply_btn"]):
                    idx = df[df['ID'] == selected_id].index[0]
                    df.at[idx, 'Reply'] = reply_text
                    df.at[idx, 'Status'] = new_status
                    save_data(df)
                    st.success("Updated / تم التحديث")
                    st.rerun()
    else:
        st.warning("Please login from the sidebar / يرجى تسجيل الدخول من القائمة الجانبية")
