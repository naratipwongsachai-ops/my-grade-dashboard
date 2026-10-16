import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเพจและธีม
st.set_page_config(page_title="My Subject Grade Dashboard", layout="wide", page_icon="🎓")
st.markdown("""
    <style>
    .main-title { text-align: center; color: #845EC2; font-weight: bold; }
    .sub-title { text-align: center; color: #0089BA; margin-bottom: 20px; }
    div.stButton > button:first-child { background-color: #845EC2; color: white; width: 100%; border-radius: 8px; }
    div.stButton > button:first-child:hover { background-color: #2C73D2; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎓 My Academic Performance Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>ระบบสรุปคะแนนดิบรวม 100 เต็ม บันทึก ดาวน์โหลด และแก้ไขไฟล์ได้ตลอดเวลา</p>", unsafe_allow_html=True)
st.markdown("---")

THEME_COLORS = ["#845EC2", "#2C73D2", "#0081CF", "#0089BA", "#008E9B", "#008F7A"]
COLUMNS_LIST = [
    "วิชา", "คะแนนเข้าเรียน", "คะแนนการบ้าน", "คะแนนสอบกลางภาค(Midterm)", 
    "คะแนนสอบปลายภาค(Final)", "คะแนนminiproject", "คะแนนLab", "คะแนนแบบฝึกหัด",
    "คะแนนรวมสุทธิ (100 คะแนนเต็ม)", "เกรด"
]

# 2. จัดการข้อมูลผ่าน Session State
if 'grade_data' not in st.session_state:
    st.session_state.grade_data = pd.DataFrame(columns=COLUMNS_LIST)

form_fields = ["sub_name", "s_att", "s_hw", "s_mid", "s_final", "s_proj", "s_lab", "s_ex"]
for field in form_fields:
    if field not in st.session_state:
        st.session_state[field] = "" if field == "sub_name" else 0.0

def calculate_custom_grade(score, cut_a, cut_b, cut_c, cut_d, cut_e):
    if score >= cut_a: return 'A'
    elif score >= cut_b: return 'B'
    elif score >= cut_c: return 'C'
    elif score >= cut_d: return 'D'
    elif score >= cut_e: return 'E'
    else: return 'F'

# 📂 โซนจัดการอัปโหลดไฟล์เก่า (Open File)
st.markdown("### 📂 ดึงข้อมูลเดิมมาทำต่อ (Open File)")
uploaded_file = st.file_uploader("อัปโหลดไฟล์คะแนนเดิมของคุณ (รองรับ .csv หรือ .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            loaded_df = pd.read_csv(uploaded_file)
        else:
            loaded_df = pd.read_excel(uploaded_file)
            
        # ตรวจสอบว่าคอลัมน์ตรงกันไหม
        if set(COLUMNS_LIST).issubset(loaded_df.columns):
            st.session_state.grade_data = loaded_df[COLUMNS_LIST]
            st.success("📂 โหลดข้อมูลเดิมเข้าสู่ระบบสำเร็จ!")
        else:
            st.error("🚨 โครงสร้างไฟล์ไม่ถูกต้อง กรุณาใช้ไฟล์ที่ดาวน์โหลดจากระบบนี้เท่านั้น")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

st.markdown("---")

# 3. จัดวางแผงควบคุมและช่องกรอกข้อมูล
col_config, col_form = st.columns(2)

with col_config:
    st.markdown("### 📊 1. เกณฑ์ตัดเกรดวิชานั้นๆ")
    g_a = st.number_input("เกรด A เริ่มที่ ≥", 0.0, 100.0, 80.0)
    g_b = st.number_input("เกรด B เริ่มที่ ≥", 0.0, 100.0, 70.0)
    g_c = st.number_input("เกรด C เริ่มที่ ≥", 0.0, 100.0, 60.0)
    g_d = st.number_input("เกรด D เริ่มที่ ≥", 0.0, 100.0, 50.0)
    g_e = st.number_input("เกรด E เริ่มที่ ≥", 0.0, 100.0, 45.0)

with col_form:
    st.markdown("### 📝 2. ช่องกรอกคะแนนดิบรายวิชา")
    sub_input = st.text_input("ชื่อวิชา *", value=st.session_state["sub_name"], placeholder="ระบุชื่อรายวิชา เช่น กลศาสตร์")
    st.session_state["sub_name"] = sub_input

    c1, c2 = st.columns(2)
    with c1:
        att_input = st.number_input("คะแนนเข้าเรียน", min_value=0.0, max_value=100.0, value=float(st.session_state["s_att"]))
        st.session_state["s_att"] = att_input
        hw_input = st.number_input("คะแนนการบ้าน", min_value=0.0, max_value=100.0, value=float(st.session_state["s_hw"]))
        st.session_state["s_hw"] = hw_input
        mid_input = st.number_input("คะแนนสอบกลางภาค(Midterm)", min_value=0.0, max_value=100.0, value=float(st.session_state["s_mid"]))
        st.session_state["s_mid"] = mid_input
        final_input = st.number_input("คะแนนสอบปลายภาค(Final)", min_value=0.0, max_value=100.0, value=float(st.session_state["s_final"]))
        st.session_state["s_final"] = final_input
    with c2:
        proj_input = st.number_input("คะแนนminiproject", min_value=0.0, max_value=100.0, value=float(st.session_state["s_proj"]))
        st.session_state["s_proj"] = proj_input
        lab_input = st.number_input("คะแนนLab", min_value=0.0, max_value=100.0, value=float(st.session_state["s_lab"]))
        st.session_state["s_lab"] = lab_input
        ex_input = st.number_input("คะแนนแบบฝึกหัด", min_value=0.0, max_value=100.0, value=float(st.session_state["s_ex"]))
        st.session_state["s_ex"] = ex_input

    submit_btn = st.button("📊 บันทึกและคำนวณสรุปผลคะแนน")
    
    if submit_btn:
        if not sub_input.strip(): 
            st.error("🚨 กรุณากรอกชื่อวิชาให้ถูกต้อง")
        else:
            final_score = att_input + hw_input + mid_input + final_input + proj_input + lab_input + ex_input
            calculated_grade = calculate_custom_grade(final_score, g_a, g_b, g_c, g_d, g_e)
            
            new_row = pd.DataFrame([{
                "วิชา": sub_input, "คะแนนเข้าเรียน": att_input, "คะแนนการบ้าน": hw_input,
                "คะแนนสอบกลางภาค(Midterm)": mid_input, "คะแนนสอบปลายภาค(Final)": final_input,
                "คะแนนminiproject": proj_input, "คะแนนLab": lab_input, "คะแนนแบบฝึกหัด": ex_input,
                "คะแนนรวมสุทธิ (100 คะแนนเต็ม)": round(final_score, 2), "เกรด": calculated_grade
            }])
            
            st.session_state.grade_data = pd.concat([st.session_state.grade_data, new_row], ignore_index=True)
            st.success(f"🎉 บันทึกวิชา {sub_input} สำเร็จ!")
            
            for field in form_fields:
                st.session_state[field] = "" if field == "sub_name" else 0.0
            st.rerun()

st.markdown("---")

# 4. หน้าจอแสดงผลสรุปและเซฟข้อมูล
if st.session_state.grade_data.empty:
    st.info("💡 ยังไม่มีข้อมูลวิชา กรุณากรอกคะแนนด้านบน หรืออัปโหลดไฟล์ข้อมูลเดิมเพื่อแสดง Dashboard")
else:
    df = st.session_state.grade_data
    st.markdown("### 📋 ตารางสรุปคะแนนและผลการเรียนทั้งหมด")
    st.dataframe(df, use_container_width=True)
    
    # 💾 โซนปุ่มดาวน์โหลดเก็บไว้ในเครื่อง (Save File)
    c_save1, c_save2 = st.columns(2)
    with c_save1:
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="💾 บันทึกเป็นไฟล์ CSV (Save File)",
            data=csv_data,
            file_name="my_grades.csv",
            mime="text/csv"
        )
    with c_save2:
        if st.button("🗑️ ล้างประวัติทั้งหมดบนเว็บ"):
            st.session_state.grade_data = pd.DataFrame(columns=COLUMNS_LIST)
            st.rerun()
        
    st.markdown("---")
    st.markdown("### 🎨 กราฟสรุปผลการวิเคราะห์แบบ Interactive")
    
    f_bar = px.bar(df, x="วิชา", y="คะแนนรวมสุทธิ (100 คะแนนเต็ม)", text="เกรด", color="วิชา",
                   title="🎯 กราฟแท่ง: คะแนนรวมดิบและเกรดแยกสีตามรายวิชา", color_discrete_sequence=THEME_COLORS)
    f_bar.update_traces(textposition='outside')
    st.plotly_chart(f_bar, use_container_width=True)
    
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        f_pie = px.pie(df, names='วิชา', values='คะแนนรวมสุทธิ (100 คะแนนเต็ม)', hole=0.4,
                       title="🍕 กราฟวงกลม: สัดส่วนคะแนนรวมของแต่ละวิชา", color_discrete_sequence=THEME_COLORS)
        st.plotly_chart(f_pie, use_container_width=True)
    with c_chart2:
        m_df = df.melt(id_vars=["วิชา"], value_vars=["คะแนนเข้าเรียน", "คะแนนการบ้าน", "คะแนนสอบกลางภาค(Midterm)", "คะแนนสอบปลายภาค(Final)", "คะแนนminiproject", "คะแนนLab", "คะแนนแบบฝึกหัด"], var_name="หมวดหมู่คะแนน", value_name="คะแนนดิบ")
        f_line = px.line(m_df, x="หมวดหมู่คะแนน", y="คะแนนดิบ", color="วิชา", markers=True,
                         title="📈 กราฟเส้น: วิเคราะห์องค์ประกอบคะแนนดิบแยกตามวิชา", color_discrete_sequence=THEME_COLORS)
        f_line.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(f_line, use_container_width=True)
