import streamlit as st
from components import (
    setup_page_config, apply_custom_css, initialize_session_state,
    render_step_navigation, render_step_content
)
from calculator import calculate_tax

# ตั้งค่าเริ่มต้นst
setup_page_config()
apply_custom_css()

# เริ่มต้น session state
initialize_session_state()

# หัวข้อหลัก
st.markdown("<h1 class='header'>คำนวณภาษี</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ช่วยคำนวณภาษีเงินได้บุคคลธรรมดาประจำปี</p>", unsafe_allow_html=True)

# โหมด debug
debug_mode = st.sidebar.checkbox("โหมดแสดงรายละเอียดการคำนวณ", value=False)

# แสดงขั้นตอน
render_step_navigation()

# แสดงเนื้อหาของแต่ละขั้นตอน
render_step_content(debug_mode, calculate_tax)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; color: #666;">
    <p>คำนวณภาษีนี้เป็นเพียงการประมาณการณ์เท่านั้น โปรดตรวจสอบกับเจ้าหน้าที่สรรพากรหรือผู้เชี่ยวชาญด้านภาษีเพื่อข้อมูลอย่างเป็นทางการ</p>
</div>
""", unsafe_allow_html=True)