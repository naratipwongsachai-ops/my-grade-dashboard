import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าจอและสไตล์ CSS ปรับแต่งตารางรายงานให้กระชับสบายตา
st.set_page_config(page_title="My Subject Grade Dashboard", layout="wide", page_icon="🎓")
st.markdown("""
    <style>
    .main-title { text-align: center; color: #845EC2; font-weight: bold; }
    .sub-title { text-align: center; color: #0089BA; margin-bottom: 25px; }
    div.stButton > button:first-child { background-color: #845EC2; color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    div.stButton > button:first-child:hover { background-color: #2C73D2; }
    .score-header { text-align: center; color: #845EC2; font-weight: bold; margin-top: 15px; margin-bottom: 15px; font-size: 20px; }
    .item-title { color: #0089BA; font-weight: bold; margin-bottom: -5px; margin-top: 5px; }
    .gpa-box { background-color: #845EC2; padding: 20px; border-radius: 10px; color: white; text-align: center; font-size: 24px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎓 My Academic Performance Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>ระบบสรุปคะแนนและตัดเกรดอัตโนมัติ (เวอร์ชันคำนวณเกรดเฉลี่ย GPA และทำงานเสถียร 100%)</p>", unsafe_allow_html=True)

THEME_COLORS = ["#845EC2", "#2C73D2", "#0081CF", "#0089BA", "#008E9B", "#008F7A", "#B39DDB", "#90CAF9"]

ALL_COLUMNS = [
    "วิชา", "เข้าเรียน(เต็ม)", "เข้าเรียน(ได้)", "การบ้าน(เต็ม)", "การบ้าน(ได้)",
    "Midterm(เต็ม)", "Midterm(ได้)", "Final(เต็ม)", "Final(ได้)",
    "MiniProject(เต็ม)", "MiniProject(ได้)", "Lab(เต็ม)", "Lab(ได้)",
    "แบบฝึกหัด(เต็ม)", "แบบฝึกหัด(ได้)", "คะแนนรวมสุทธิที่ได้", "คะแนนเต็มรวมสุทธิ", "เกรด"
]

if 'grade_data' not in st.session_state:
    st.session_state.grade_data = pd.DataFrame(columns=ALL_COLUMNS)

form_fields = [
    "sub_name", "t_att", "s_att", "t_hw", "s_hw", "t_mid", "s_mid", 
    "t_final", "s_final", "t_proj", "s_proj", "t_lab", "s_lab", "t_ex", "s_ex"
]
for field in form_fields:
    if field not in st.session_state:
        if field == "sub_name": st.session_state[field] = ""
        elif field.startswith("t_"): st.session_state[field] = "10.0"
        else: st.session_state[field] = 0.0

def calculate_custom_grade(score, cut_a, cut_b, cut_c, cut_d, cut_e):
    if score >= cut_a: return 'A'
    elif score >= cut_b: return 'B'
    elif score >= cut_c: return 'C'
    elif score >= cut_d: return 'D'
    elif score >= cut_e: return 'E'
    else: return 'F'

st.markdown("### 📂 ดึงข้อมูลเดิมมาทำต่อ (Open File)")
uploaded_file = st.file_uploader("อัปโหลดไฟล์คะแนนเดิม (.csv หรือ .xlsx)", type=["csv", "xlsx"])
if uploaded_file is not None:
    try:
        loaded_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        if set(ALL_COLUMNS).issubset(loaded_df.columns):
            st.session_state.grade_data = loaded_df[ALL_COLUMNS]
            st.success("📂 โหลดข้อมูลเดิมเข้าสู่ระบบสำเร็จ!")
    except Exception as e:
        st.error(f"โหลดไฟล์ไม่สำเร็จ: {e}")

st.markdown("---")
# 3. โซนตั้งค่าเกณฑ์ตัดเกรดแบบหน้ากระดานแถวเดียว (ประหยัดพื้นที่มาก)
st.markdown("### 📊 1. เกณฑ์การตัดเกรดรายวิชา (อิงคะแนนรวมที่ได้จริง)")
c_ga, c_gb, c_gc, c_gd, c_ge = st.columns(5)
with c_ga: g_a = st.number_input("เกรด A เริ่มที่ ≥", 0.0, 100.0, 80.0)
with c_gb: g_b = st.number_input("เกรด B เริ่มที่ ≥", 0.0, 100.0, 70.0)
with c_gc: g_c = st.number_input("เกรด C เริ่มที่ ≥", 0.0, 100.0, 60.0)
with c_gd: g_d = st.number_input("เกรด D เริ่มที่ ≥", 0.0, 100.0, 50.0)
with c_ge: g_e = st.number_input("เกรด E เริ่มที่ ≥", 0.0, 100.0, 45.0)

st.markdown("---")

# 4. โซนฟอร์มกรอกคะแนนรายหมวดสไตล์ Compact 2 คอลัมน์
st.markdown("### 📝 2. ช่องกรอกคะแนนรายหมวด")
sub_input = st.text_input("ชื่อวิชา *", value=st.session_state["sub_name"], placeholder="ระบุชื่อรายวิชา เช่น แคลคูลัส, ฟิสิกส์")
st.session_state["sub_name"] = sub_input

st.markdown("<h3 class='score-header'>📊 Score</h3>", unsafe_allow_html=True)

# ฟังก์ชันช่วยสร้างคู่กรอกคะแนนเต็ม (มี "ไม่มี") และคะแนนที่ได้จริง
def render_score_input(label, t_key, s_key, default_total="10.0"):
    st.markdown(f"<p class='item-title'>🔹 {label}</p>", unsafe_allow_html=True)
    c_lbl1, c_lbl2 = st.columns(2)
    with c_lbl1: st.caption("📋 คะแนนเต็ม (เลือกตามที่มี/ไม่มี)")
    with c_lbl2: st.caption("✍️ คะแนนที่ได้จริง")
        
    c_t, c_s = st.columns(2)
    with c_t:
        options = ["5.0", "10.0", "15.0", "20.0", "25.0", "30.0", "35.0", "40.0", "45.0", "50.0", "60.0", "100.0", "ไม่มี"]
        current_val = str(st.session_state[t_key])
        if current_val not in options: options.append(current_val)
        idx = options.index(current_val) if current_val in options else options.index(default_total)
        tot_str = st.selectbox(f"เต็ม_{t_key}", options=options, index=idx, key=f"t_{t_key}", label_visibility="collapsed")
        st.session_state[t_key] = tot_str
    
    with c_s:
        is_disabled = (tot_str == "ไม่มี")
        default_earned = 0.0 if is_disabled else float(st.session_state[s_key])
        sc = st.number_input(f"ได้_{s_key}", min_value=0.0, max_value=100.0, value=default_earned, key=f"s_{s_key}", label_visibility="collapsed", disabled=is_disabled)
        st.session_state[s_key] = sc
        
    tot_val = 0.0 if tot_str == "ไม่มี" else float(tot_str)
    return tot_val, sc, tot_str

col_left, col_right = st.columns(2)
with col_left:
    t_att, s_att, t_att_str = render_score_input("คะแนนเข้าเรียน", "t_att", "s_att", default_total="10.0")
    t_hw, s_hw, t_hw_str = render_score_input("คะแนนการบ้าน", "t_hw", "s_hw", default_total="10.0")
    t_lab, s_lab, t_lab_str = render_score_input("คะแนน Lab", "t_lab", "s_lab", default_total="10.0")
    t_ex, s_ex, t_ex_str = render_score_input("คะแนนแบบฝึกหัด", "t_ex", "s_ex", default_total="10.0")

with col_right:
    t_mid, s_mid, t_mid_str = render_score_input("คะแนนสอบกลางภาค Midterm", "t_mid", "s_mid", default_total="40.0")
    t_final, s_final, t_final_str = render_score_input("คะแนนสอบปลายภาค Final", "t_final", "s_final", default_total="30.0")
    t_proj, s_proj, t_proj_str = render_score_input("คะแนน Mini Project", "t_proj", "s_proj", default_total="10.0")
    st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
submit_btn = st.button("📊 บันทึกและคำนวณสรุปผลคะแนน")
if submit_btn:
    if not sub_input.strip(): 
        st.error("🚨 กรุณาระบุชื่อวิชาให้ถูกต้องก่อนทำการบันทึก")
    elif s_att > t_att or s_hw > t_hw or s_mid > t_mid or s_final > t_final or s_proj > t_proj or s_lab > t_lab or s_ex > t_ex:
        st.error("🚨 ข้อผิดพลาด: คะแนนที่ได้ ห้ามกรอกเกินคะแนนเต็มอย่างเด็ดขาดครับ")
    else:
        total_earned = s_att + s_hw + s_mid + s_final + s_proj + s_lab + s_ex
        total_possible = t_att + t_hw + t_mid + t_final + t_proj + t_lab + t_ex
        calculated_grade = calculate_custom_grade(total_earned, g_a, g_b, g_c, g_d, g_e)
        
        new_row = pd.DataFrame([{
            "วิชา": sub_input, "เข้าเรียน(เต็ม)": t_att_str, "เข้าเรียน(ได้)": s_att,
            "การบ้าน(เต็ม)": t_hw_str, "การบ้าน(ได้)": s_hw, "Midterm(เต็ม)": t_mid_str, "Midterm(ได้)": s_mid,
            "Final(เต็ม)": t_final_str, "Final(ได้)": s_final, "MiniProject(เต็ม)": t_proj_str, "MiniProject(ได้)": s_proj,
            "Lab(เต็ม)": t_lab_str, "Lab(ได้)": s_lab, "แบบฝึกหัด(เต็ม)": t_ex_str, "แบบฝึกหัด(ได้)": s_ex,
            "คะแนนรวมสุทธิที่ได้": round(total_earned, 2), "คะแนนเต็มรวมสุทธิ": round(total_possible, 2), "เกรด": calculated_grade
        }])
        
        st.session_state.grade_data = pd.concat([st.session_state.grade_data, new_row], ignore_index=True)
        st.success(f"🎉 บันทึกวิชา {sub_input} สำเร็จ!")
        st.session_state["sub_name"] = ""
        for field in form_fields:
            if field != "sub_name" and not field.startswith("t_"): st.session_state[field] = 0.0
        st.rerun()

st.markdown("---")

if st.session_state.grade_data.empty:
    st.info("💡 หน้าจอรายงานจะโผล่ขึ้นมาตรงนี้ทันทีหลังจากที่คุณกดปุ่มบันทึกข้อมูล")
else:
    df = st.session_state.grade_data
    
    # ปรับปรุงคอลัมน์และลำดับตารางให้เริ่มที่เลข 1 พอดีหน้าจอ
    display_df = df[["วิชา", "คะแนนรวมสุทธิที่ได้", "คะแนนเต็มรวมสุทธิ", "เกรด"]].copy()
    display_df.index = range(1, len(display_df) + 1)
    display_df.index.name = "ลำดับ"
    
    st.markdown("### 📋 ตารางสรุปคะแนนและผลการเรียนทั้งหมด")
    st.dataframe(display_df, use_container_width=True)
    
    # ระบบเลือกและกดลบทีละรายวิชา
    st.markdown("### 🗑️ จัดการลบข้อมูลรายวิชา")
    c_del1, c_del2 = st.columns(2)
    with c_del1:
        selected_sub_to_delete = st.selectbox("เลือกวิชาที่ต้องการลบออกจากระบบ:", options=df["วิชา"].unique(), key="del_select")
    with c_del2:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("❌ ลบวิชานี้"):
            st.session_state.grade_data = df[df["วิชา"] != selected_sub_to_delete].reset_index(drop=True)
            st.success(f"ลบข้อมูลวิชา {selected_sub_to_delete} เรียบร้อยแล้ว!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c_save1, c_save2 = st.columns(2)
    with c_save1:
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="💾 บันทึกเป็นไฟล์ CSV (Save File)", data=csv_data, file_name="my_detailed_grades.csv", mime="text/csv")
    with c_save2:
        if st.button("🚨 ล้างประวัติทั้งหมดบนเว็บ (Reset All)"):
            st.session_state.grade_data = pd.DataFrame(columns=ALL_COLUMNS)
            st.rerun()
        
    st.markdown("---")
    st.markdown("### 🎨 กราฟสรุปสัดส่วนคะแนนที่ได้จริง")
    
    unique_subs = df["วิชา"].unique()
    sub_color_map = {sub: THEME_COLORS[i % len(THEME_COLORS)] for i, sub in enumerate(unique_subs)}
    
    f_pie = px.pie(df, names='วิชา', values='คะแนนรวมสุทธิที่ได้', hole=0.4, 
                   title="🍕 กราฟวงกลม: สัดส่วนคะแนนที่ได้จริงของแต่ละวิชา", color='วิชา', color_discrete_map=sub_color_map)
    st.plotly_chart(f_pie, use_container_width=True)

    st.markdown("---")
    
    # 💡 แก้ไขข้อเรียกร้อง: เพิ่มปุ่มกดคำนวณเกรดเฉลี่ยสะสม GPA และเอาไว้ด้านล่างสุดของเว็บ
    st.markdown("### 📊 3. สรุปผลการเรียนรวมทั้งหมด")
    
    if st.button("📈 กดเพื่อคำนวณเกรดเฉลี่ย (Calculate GPA)"):
        # แปลงตัวอักษรเกรดเป็นแต้มคะแนนเฉลี่ย
        grade_points_map = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'E': 0.5, 'F': 0.0}
        df['แต้มเกรด'] = df['เกรด'].map(grade_points_map)
        
        # คำนวณเกรดเฉลี่ยสะสม
        mean_gpa = df['แต้มเกรด'].mean()
        
        # แสดงผลกล่อง GPA ล่างสุดตามสไตล์กรอบแถวสีม่วงเด่นชัด
        st.markdown(f"<div class='gpa-box'>🎓 เกรดเฉลี่ยรวมสะสมของคุณ (GPA) คือ: {mean_gpa:.2f}</div>", unsafe_allow_html=True)
