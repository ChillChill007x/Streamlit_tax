import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import os
import tempfile
from fpdf import FPDF
from xhtml2pdf import pisa
from pathlib import Path
from weasyprint import HTML
import weasyprint

def setup_pdf_fonts():
    if 'THSarabunNew' not in pdfmetrics._fonts:
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'THSarabunNew.ttf')
        bold_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'THSarabunNew-Bold.ttf')
        
        if not os.path.exists(font_path):
            return False
        
        pdfmetrics.registerFont(TTFont('THSarabunNew', font_path))
        if os.path.exists(bold_font_path):
            pdfmetrics.registerFont(TTFont('THSarabunNew-Bold', bold_font_path))
        return True
    return True
##setup_pdf_fonts
##"THSarabunNew" ถูกลงทะเบียนหรือยัง
##หากไม่พบฟอนต์ จะพยายามโหลดจากโฟลเดอร์ fonts
##ใช้ pdfmetrics.registerFont() เพื่อเพิ่มฟอนต์ให้ reportlab

def simple_pdf_download(df, filename="คำนวณภาษี"):
    try:
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>รายงานคำนวณภาษี</title>
            <style>
                body {{ font-family: sans-serif; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid black; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>รายงานคำนวณภาษี</h1>
            <p>วันที่ออกรายงาน: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            {df.to_html(index=False)}
        </body>
        </html>
        """
        
        pdf_data = weasyprint.HTML(string=html_content).write_pdf()
        
        b64 = base64.b64encode(pdf_data).decode()
        filename_with_timestamp = f"{filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename_with_timestamp}">ดาวน์โหลดผลการคำนวณภาษี (PDF แบบง่าย)</a>'
        
        return href
    except Exception as e:
        return f"<p>เกิดข้อผิดพลาดในการสร้าง PDF: {str(e)}</p>"
##simple_pdf_download(df, filename)
##แปลงข้อมูล DataFrame เป็น HTML
##ใช้ weasyprint สร้างไฟล์ PDF
##เข้ารหัส PDF เป็น Base64 เพื่อให้ดาวน์โหลดผ่านลิงก์


def setup_page_config():
    st.set_page_config(
        page_title="คำนวณภาษี - Thai Tax Calculator",
        page_icon="💸",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
##setup_page_config
##ตั้งค่าหน้า Streamlit เช่นชื่อ, ไอคอน, และ layout

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Arial', '', 'Arial.ttf', uni=True)
        
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)
        
        thai_font_path = os.path.join(fonts_dir, "THSarabunNew.ttf")
        thai_font_bold_path = os.path.join(fonts_dir, "THSarabunNew-Bold.ttf")
        
        if os.path.exists(thai_font_path):
            self.add_font('THSarabunNew', '', thai_font_path, uni=True)
            self.set_font('THSarabunNew', '', 14)
        else:
            self.set_font('Arial', '', 12)
            print("ไม่พบฟอนต์ไทย กรุณาติดตั้งฟอนต์ THSarabunNew ในโฟลเดอร์ fonts")
        
        if os.path.exists(thai_font_bold_path):
            self.add_font('THSarabunNew', 'B', thai_font_bold_path, uni=True)
##class PDF(FPDF)
##ใช้ FPDF สร้างเอกสาร PDF
##ตรวจสอบและโหลดฟอนต์ "THSarabunNew"
    def header(self):
        if 'THSarabunNew' in self.fonts:
            self.set_font('THSarabunNew', 'B', 16)
        else:
            self.set_font('Arial', 'B', 14)
        
        self.cell(0, 10, 'รายงานคำนวณภาษี', 0, 1, 'C')
        
        if 'THSarabunNew' in self.fonts:
            self.set_font('THSarabunNew', '', 12)
        else:
            self.set_font('Arial', '', 10)
        
        self.cell(0, 10, f'วันที่ออกรายงาน: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        # หมายเลขหน้า
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'หน้า {self.page_no()}/{{nb}}', 0, 0, 'C')

# สร้าง PDF จาก DataFrame
def create_pdf(df, title="รายงานคำนวณภาษี"):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # ตั้งค่าสำหรับตาราง
    col_width = [140, 50]  # ความกว้างของคอลัมน์ (รายการ, จำนวนเงิน)
    row_height = 10
    
    # สร้างส่วนหัวของตาราง
    pdf.set_fill_color(217, 237, 247)  # สีฟ้าอ่อน
    pdf.set_font('THSarabunNew', 'B', 14) if 'THSarabunNew' in pdf.fonts else pdf.set_font('Arial', 'B', 12)
    
    pdf.cell(col_width[0], row_height, df.columns[0], 1, 0, 'C', 1)
    pdf.cell(col_width[1], row_height, df.columns[1], 1, 1, 'C', 1)
    
    # สร้างข้อมูลในตาราง
    pdf.set_font('THSarabunNew', '', 14) if 'THSarabunNew' in pdf.fonts else pdf.set_font('Arial', '', 12)
    
    for _, row in df.iterrows():
      
        item_text = str(row[0])
        pdf.cell(col_width[0], row_height, item_text, 1, 0, 'L')
        
        amount_text = str(row[1])
        pdf.cell(col_width[1], row_height, amount_text, 1, 1, 'R')
    
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    
    return buffer
##ฟังก์ชันสร้าง PDF create_pdf(df, title)
##ใช้ FPDF วาดตารางจาก DataFrame
def create_download_link(df, filename="คำนวณภาษี"):
    try:
        pdf_buffer = create_pdf(df)
        
        b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
        
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf">ดาวน์โหลดผลการคำนวณภาษี (PDF)</a>'
        return href
    except Exception as e:
        return f"<p>เกิดข้อผิดพลาดในการสร้างไฟล์ PDF: {str(e)}</p>"


def apply_custom_css():
    # 1. กำหนดเส้นทางไปยังไฟล์ CSS ที่ต้องการใช้งาน
    css_path = "C:\\Users\PC\PycharmProjects\Streamlit_\styles.css"

    # 2. เปิดไฟล์ CSS ในโหมดอ่าน (read) พร้อมกับการเข้ารหัสแบบ UTF-8
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()  # อ่านเนื้อหาจากไฟล์และเก็บในตัวแปร css

    # 3. นำ CSS ไปใช้กับแอป Streamlit โดยใช้ Markdown และอนุญาตให้แสดง HTML ที่ไม่ปลอดภัย
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def initialize_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 1
    ##กำหนดค่าเริ่มต้นให้ตัวแปรในsession_state
    defaults = {
        'marital_status': "โสด", 'has_children': False, 'children_count': 0,
        'monthly_salary': 0, 'annual_salary': 0, 'bonus': 0, 'other_income': 0,
        'personal_expense': 0, 'family_deduction': 0, 'provident_fund': 0,
        'social_security': 0, 'home_loan_interest': 0, 'life_insurance': 0,
        'health_insurance': 0, 'parent_health_insurance': 0, 'pension_insurance': 0,
        'government_pension': 0, 'national_savings': 0, 'rmf': 0, 'ssf': 0,
        'thai_esg': 0, 'donation': 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value



def render_step_navigation():
    steps = ["รายรับ", "ลดหย่อนครอบครัว", "กองทุนสำรองเลี้ยงชีพ\nเงินประกันสังคม\nและที่อยู่อาศัย",
             "ประกัน", "กองทุน อื่น ๆ", "คำนวณภาษี"]
    st.markdown("<div class='step-container'><div class='step-line'></div></div>", unsafe_allow_html=True)
    cols = st.columns(6)
    for i, (col, step_name) in enumerate(zip(cols, steps), start=1):
        with col:
            if i == st.session_state.step:
                st.markdown(f"<div class='step active'>{i}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='step'>{i}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='step-label'>{step_name}</div>", unsafe_allow_html=True)

def render_step_content(debug_mode, calculate_tax_func):
    if st.session_state.step == 1:
        render_step_1()
    elif st.session_state.step == 2:
        render_step_2()
    elif st.session_state.step == 3:
        render_step_3()
    elif st.session_state.step == 4:
        render_step_4()
    elif st.session_state.step == 5:
        render_step_5()
    elif st.session_state.step == 6:
        render_step_6(debug_mode, calculate_tax_func)


def render_step_1():
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("รายรับ")
        
        if 'monthly_salary_filled' not in st.session_state:
            st.session_state.monthly_salary_filled = False
        if 'bonus_filled' not in st.session_state:
            st.session_state.bonus_filled = False
        if 'other_income_filled' not in st.session_state:
            st.session_state.other_income_filled = False

        monthly_salary = st.number_input("เงินเดือน (บาท/เดือน)", min_value=0, value=0, step=1000, format="%d", key="monthly_salary_input",
                                        help="กรุณากรอกเงินเดือนต่อเดือน (บังคับกรอก)")
        if monthly_salary > 0:
            st.session_state.monthly_salary_filled = True
        else:
            st.session_state.monthly_salary_filled = False

        annual_salary = monthly_salary * 12
        st.info(f"เงินเดือนทั้งปี: {annual_salary:,.2f} บาท (เงินเดือน x 12)")
        
        # Input โบนัส (บังคับกรอก)
        bonus = st.number_input("โบนัส (บาท)", min_value=0, value=0, step=1000, format="%d", key="bonus_input",
                               help="กรุณากรอกโบนัสที่คุณได้รับในปี (บังคับกรอก)")
        if bonus > 0:
            st.session_state.bonus_filled = True
        else:
            st.session_state.bonus_filled = False

        other_income = st.number_input("รายได้อื่นๆ เช่น การขายของออนไลน์, รับจ้างฟรีแลนซ์ (บาท)", 
                                      min_value=0, value=0, step=1000, format="%d", key="other_income_input",
                                      help="กรุณากรอกรายได้นอกเหนือจากเงินเดือนและโบนัส (บังคับกรอก)")
        if other_income > 0:
            st.session_state.other_income_filled = True
        else:
            st.session_state.other_income_filled = False

        total_annual_income = annual_salary + bonus + other_income
        st.info(f"รายได้ทั้งหมดที่ใช้ในการคำนวณภาษี: {total_annual_income:,.2f} บาท")
        
        if st.button("ถัดไป", key="next_1"):
            if not st.session_state.monthly_salary_filled:
                st.error("กรุณากรอกเงินเดือนก่อนกดปุ่ม 'ถัดไป'")
            else:
                st.session_state.monthly_salary = monthly_salary
                st.session_state.annual_salary = annual_salary
                st.session_state.bonus = bonus
                st.session_state.other_income = other_income
                st.session_state.step = 2
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
# Step 2: เบี้ยเลี้ยงส่วนตัว
def render_step_2():
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("รายการลดหย่อนภาษี : ครอบครัว")
        ##ฟังก์ชันrender_step_2()ทำหน้าที่แสดงแบบฟอร์มให้ผู้ใช้กรอกข้อมูลเกี่ยวกับค่าลดหย่อนภาษีในหมวดหมู่"ครอบครัว"
        ##โดยใช้Streamlit(st).
        
        marital_status_options = ["โสด", "หย่า", "คู่สมรสมีเงินได้(แยกยื่น)", "คู่สมรสไม่มีเงินได้"]
        marital_status = st.selectbox("สถานะสมรส", marital_status_options)
        st.session_state.marital_status = marital_status
        ##เลือกสถานะสมรสst.number_input() ใช้สร้าง input ตัวเลขที่ไม่สามารถเปลี่ยนแปลงได้ (disabled=True)ค่าคงที่ 60,000 บาท (ตามกฎหมายไทย)

        st.markdown("#### ลดหย่อนส่วนบุคคล")
        st.number_input("ลดหย่อนส่วนบุคคล (บาท)", min_value=60000, value=60000, step=1000, format="%d", disabled=True)
        ##ลดหย่อนส่วนบุคคล

        parent_allowance = 0
        child_allowance = 0
        spouse_parent_allowance = 0
        disabled_allowance = 0
        ##คำนวณค่าลดหย่อนตามเงื่อนไงกำหนดตัวแปรค่าลดหย่อนเริ่มต้นทั้งหมดเป็น 0
        
        if marital_status in ["หย่า", "คู่สมรสมีเงินได้(แยกยื่น)", "คู่สมรสไม่มีเงินได้"]:
            st.markdown("#### ลดหย่อนบิดา-มารดา (ตนเอง)")
            col1, col2 = st.columns(2)
            with col1:
                has_father = st.checkbox("บิดา", key="father_allowance_key")
            with col2:
                has_mother = st.checkbox("มารดา", key="mother_allowance_key")
            parent_allowance = (has_father + has_mother) * 30000
            if parent_allowance > 0:
                st.info(f"ลดหย่อนบิดา-มารดา: {parent_allowance:,d} บาท (ท่านละ 30,000 บาท)")
            ##ลดหย่อนบิดา - มารดาของตนเองเฉพาะกรณีที่ผู้ใช้"หย่า", "คู่สมรสมีเงินได้(แยกยื่น)", "คู่สมรสไม่มีเงินได้"ผู้ใช้สามารถเลือก "บิดา" หรือ "มารดา" ได้ถ้าถูกเลือก ค่าลดหย่อนจะถูกเพิ่ม 30,000 บาทต่อคน
            
            st.markdown("#### บุตรคนที่ 1 (เกิดก่อนปี 2561)")
            has_children = st.radio("มีบุตรหรือไม่", ["มี", "ไม่มี"], horizontal=True, key="has_children_radio")
            ##ลดหย่อนบุตรเช็คว่าผู้ใช้มีบุตรหรือไม่

            if has_children == "มี":
                st.session_state.has_children = True
                child_allowance += 30000
                st.info(f"ลดหย่อน: 30,000 บาท")
                
                st.markdown("#### บุตรคนที่ 2 เป็นต้นไป")
                col1, col2 = st.columns(2)
                with col1:
                    born_before_2018 = st.number_input("จำนวนบุตรที่เกิดก่อนปี 2561", min_value=0, value=0, step=1, key="born_before_2018")
                with col2:
                    born_after_2018 = st.number_input("จำนวนบุตรที่เกิดหลังปี 2561 เป็นต้นไป", min_value=0, value=0, step=1, key="born_after_2018")
                st.session_state.children_count = 1 + born_before_2018 + born_after_2018
                if born_before_2018 > 0:
                    child_allowance += born_before_2018 * 30000
                    st.info(f"ลดหย่อนบุตรเกิดก่อนปี 2561: {born_before_2018 * 30000:,d} บาท")
                if born_after_2018 > 0:
                    child_allowance += born_after_2018 * 60000
                    st.info(f"ลดหย่อนบุตรเกิดหลังปี 2561: {born_after_2018 * 60000:,d} บาท")
            ##บุตรเกิดก่อนปี 2561 ได้ลดหย่อน 30,000 บาท/คนบุตรเกิดหลังปี 2561 ได้ลดหย่อน 60,000 บาท/คน
            else:
                st.session_state.has_children = False
                st.session_state.children_count = 0
            
            st.markdown("#### ลดหย่อนผู้พิการหรือทุพพลภาพ (ไม่มีเงินได้)")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                disabled_self = st.checkbox("ตนเอง", key="disabled_self_key")
            with col2:
                disabled_father = st.checkbox("บิดา", key="disabled_father_key")
            with col3:
                disabled_mother = st.checkbox("มารดา", key="disabled_mother_key")
            with col4:
                disabled_child = st.checkbox("บุตร (เช่น พี่ น้อง หลาน)", key="disabled_child_key")
            disabled_allowance = (disabled_self + disabled_father + disabled_mother + disabled_child) * 60000
            ##ลดหย่อนผู้พิการเลือกได้ 4 ตัวเลือก: ตนเอง, บิดา, มารดา, บุตรคนละ 60,000 บาท

            if disabled_allowance > 0:
                st.info(f"ลดหย่อนผู้พิการหรือทุพพลภาพ: {disabled_allowance:,d} บาท (คนละ 60,000 บาท)")
            
            if marital_status in ["คู่สมรสมีเงินได้(แยกยื่น)", "คู่สมรสไม่มีเงินได้"]:
                st.markdown("#### ลดหย่อนบิดา-มารดา (คู่สมรส)")
                col1, col2 = st.columns(2)
                with col1:
                    has_spouse_father = st.checkbox("บิดาของคู่สมรส", key="spouse_father_allowance_key")
                with col2:
                    has_spouse_mother = st.checkbox("มารดาของคู่สมรส", key="spouse_mother_allowance_key")
                spouse_parent_allowance = (has_spouse_father + has_spouse_mother) * 30000
                if spouse_parent_allowance > 0:
                    st.info(f"ลดหย่อนบิดา-มารดาของคู่สมรส: {spouse_parent_allowance:,d} บาท (ท่านละ 30,000 บาท)")
        ##ลดหย่อนบิดา - มารดาของคู่สมรสเฉพาะกรณีที่คู่สมรสไม่มีรายได้ หรือยื่นภาษีแยกคนละ 30,000 บาท


        standard_deduction = 60000
        spouse_deduction = 60000 if marital_status == "คู่สมรสไม่มีเงินได้" else 0
        total_family_deduction = standard_deduction + spouse_deduction + parent_allowance + child_allowance + disabled_allowance + spouse_parent_allowance
        st.session_state.family_deduction = total_family_deduction
        st.markdown("---")
        st.info(f"รวมค่าลดหย่อนครอบครัว: {total_family_deduction:,.2f} บาท")
        ##รวมค่าลดหย่อนทั้งหมดที่คำนวณได้


        ##คำนวณค่าใช้จ่ายจากรายได้ประจำปีหรือฟรีแลนซ์จำกัดค่าใช้จ่ายที่สามารถหักได้ไม่เกิน 100,000 บาท
        st.markdown("---")
        st.subheader("ค่าใช้จ่ายส่วนตัว")
        expense_options = ["เงินเดือน (หักได้ 50% แต่ไม่เกิน 100,000 บาท)", "อิสระ/ฟรีแลนซ์ (หักได้ตามจริงหรือเหมา)"]
        expense_type = st.selectbox("ประเภทรายได้", expense_options, key="expense_type_select")
        
        if expense_type == expense_options[0]:
            annual_salary = st.session_state.annual_salary
            salary_expense = min(annual_salary * 0.5, 100000)
            st.info(f"""
            การคำนวณค่าใช้จ่ายส่วนตัว (เงินเดือน):
            - เงินเดือนทั้งปี: {annual_salary:,.2f} บาท
            - 50% ของเงินเดือนทั้งปี: {annual_salary * 0.5:,.2f} บาท
            - ค่าใช้จ่ายสูงสุดที่หักได้: 100,000 บาท
            - ค่าใช้จ่ายส่วนตัวที่หักได้: {salary_expense:,.2f} บาท
            """)
            st.session_state.personal_expense = salary_expense
        else:
            freelance_income = st.session_state.other_income
            expense_method = st.radio("วิธีหักค่าใช้จ่าย", ["หักแบบเหมา (หักตาม % ที่กฎหมายกำหนด)", "หักตามจริง (มีหลักฐานการใช้จ่าย)"], key="expense_method_radio")
            if expense_method == "หักแบบเหมา (หักตาม % ที่กฎหมายกำหนด)":
                freelance_rate = 0.6
                expense_calc = min(freelance_income * freelance_rate, 100000)
                st.info(f"""
                การคำนวณค่าใช้จ่ายส่วนตัว (อิสระ/ฟรีแลนซ์):
                - รายได้อื่นๆ: {freelance_income:,.2f} บาท
                - 60% ของรายได้อื่นๆ: {freelance_income * 0.6:,.2f} บาท
                - ค่าใช้จ่ายสูงสุดที่หักได้: 100,000 บาท
                - ค่าใช้จ่ายส่วนตัวที่หักได้: {expense_calc:,.2f} บาท
                """)
            else:
                actual_expense = st.number_input("ค่าใช้จ่ายจริง (บาท)", min_value=0, value=0, step=1000, format="%d", key="actual_expense_input")
                expense_calc = min(actual_expense, freelance_income * 0.6)
                st.info(f"""
                การคำนวณค่าใช้จ่ายส่วนตัว (อิสระ/ฟรีแลนซ์):
                - รายได้อื่นๆ: {freelance_income:,.2f} บาท
                - ค่าใช้จ่ายจริง: {actual_expense:,.2f} บาท
                - ค่าใช้จ่ายสูงสุดที่หักได้ (60% ของรายได้): {freelance_income * 0.6:,.2f} บาท
                - ค่าใช้จ่ายส่วนตัวที่หักได้: {expense_calc:,.2f} บาท
                """)
            st.session_state.personal_expense = expense_calc
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ย้อนกลับ", key="back_2"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("ถัดไป", key="next_2"):
                st.session_state.step = 3
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    ##กำหนดให้ผู้ใช้ย้อนกลับไปStep1หรือไปต่อStep3

# Step 3: กองทุนสำรองเลี้ยงชีพ, ประกันสังคม, สินเชื่อที่อยู่อาศัย
def render_step_3():
    with st.container():  # ใช้ container เพื่อจัดกลุ่มองค์ประกอบใน UI
        st.markdown("<div class='card'>", unsafe_allow_html=True)  # เปิดแท็ก `<div>` สำหรับใช้ CSS สไตล์ card
        st.subheader("รายการลดหย่อนภาษี : กองทุน เงินประกันสังคม และที่อยู่อาศัย")  # หัวข้อหลักของหน้า
##สร้าง container เพื่อรวม UI ของ Step 3ใช้ st.markdown() เพื่อเพิ่ม HTML <div class='card'> สำหรับตกแต่ง UI (ต้องมี CSS ที่กำหนด .card ไว้)st.subheader() แสดงหัวข้อหลักของหน้าสำหรับแสดงข้อมูลค่าลดหย่อน


        ##ค่าลดหย่อนกองทุนสำรองเลี้ยงชีพ (PVD)
        pvd_amount = st.number_input("ค่าลดหย่อนกองทุนสำรองเลี้ยงชีพ (PVD)", min_value=0, value=0, step=1000,format="%d", key="pvd_input")
        if pvd_amount > 0:
            annual_salary = st.session_state.annual_salary  # ดึงเงินเดือนทั้งปีจาก session_state
            max_pvd = min(annual_salary * 0.15,
                          500000)  # คำนวณค่าลดหย่อนสูงสุดที่ 15% ของเงินเดือนทั้งปี หรือ 500,000 บาท (น้อยกว่าระหว่างสองค่า)
            capped_pvd = min(pvd_amount, max_pvd)  # จำกัดค่าลดหย่อนไม่ให้เกิน max_pvd
            st.info(
                f"ลดหย่อน PVD: ไม่เกิน 15% ของเงินเดือนทั้งปี ({max_pvd:,.2f}) หรือไม่เกิน 500,000 บาท")  # แสดงข้อมูลลดหย่อน
            st.session_state.provident_fund = capped_pvd  # บันทึกค่าลดหย่อนลง session_state
        else:
            st.session_state.provident_fund = 0  # หากไม่มีค่า PVD ให้เก็บเป็น 0

        ##ค่าลดหย่อนเงินประกันสังคม
        social_security = st.number_input("เงินประกันสังคม (ทั้งปี)", min_value=0, value=0, step=500, format="%d",key="social_security_input")
        if social_security > 0:
            capped_social = min(social_security, 9000)  # จำกัดค่าลดหย่อนไม่ให้เกิน 9,000 บาท
            st.info(f"ลดหย่อนประกันสังคม: ไม่เกิน 9,000 บาท")  # แสดงข้อความแจ้งเตือน
            st.session_state.social_security = capped_social  # บันทึกค่าลดหย่อนลง session_state
        else:
            st.session_state.social_security = 0  # หากไม่มีค่าให้เก็บเป็น 0

        ##ค่าลดหย่อนดอกเบี้ยเงินกู้ยืมเพื่อที่อยู่อาศัย
        home_loan_interest = st.number_input("ดอกเบี้ยเงินกู้ยืมเพื่อที่อยู่อาศัย (บาท/ปี)", min_value=0, value=0,step=1000, format="%d", key="home_loan_input")
        if home_loan_interest > 0:
            capped_interest = min(home_loan_interest, 100000)  # จำกัดค่าลดหย่อนไม่ให้เกิน 100,000 บาท
            st.info(f"ลดหย่อนดอกเบี้ยเงินกู้ที่อยู่อาศัย: ไม่เกิน 100,000 บาท")  # แสดงข้อความแจ้งเตือน
            st.session_state.home_loan_interest = capped_interest  # บันทึกค่าลดหย่อนลง session_state
        else:
            st.session_state.home_loan_interest = 0  # หากไม่มีค่าให้เก็บเป็น 0

        ##คำนวณรวมค่าลดหย่อน
        total_deduction = st.session_state.provident_fund + st.session_state.social_security + st.session_state.home_loan_interest
        st.markdown("---")  # เส้นคั่น
        st.info(f"รวมค่าลดหย่อนกองทุน ประกันสังคม และที่อยู่อาศัย: {total_deduction:,.2f} บาท")  # แสดงผลรวมค่าลดหย่อน

        ##ปุ่มย้อนกลับและถัดไป
        col1, col2 = st.columns(2)  # แบ่งเป็น 2 คอลัมน์
        with col1:
            if st.button("ย้อนกลับ", key="back_3"):  # ปุ่มย้อนกลับไปที่ Step 2
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("ถัดไป", key="next_3"):  # ปุ่มไป Step 4
                st.session_state.step = 4
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)  # ปิดแท็ก <div>


# Step 4: ประกันภัย
def render_step_4():
    with st.container():  # ใช้ container เพื่อจัดกลุ่ม UI ของหน้านี้
        st.markdown("<div class='card'>", unsafe_allow_html=True)  # ใช้ CSS สำหรับ styling
        st.subheader("รายการลดหย่อนภาษี : ประกัน")  # แสดงหัวข้อของหน้า

        ##คำนวณค่าลดหย่อนเบี้ยประกันชีวิต
        life_insurance = st.number_input("เบี้ยประกันชีวิต (บาท/ปี)", min_value=0, value=0, step=1000, format="%d", key="life_insurance_input")
        capped_life_insurance = min(life_insurance, 100000)
        if life_insurance > 0:
            st.info(f"ลดหย่อนเบี้ยประกันชีวิต: ไม่เกิน 100,000 บาท")
        st.session_state.life_insurance = capped_life_insurance

        ##คำนวณค่าลดหย่อนเบี้ยประกันสุขภาพ
        health_insurance = st.number_input("เบี้ยประกันสุขภาพ (บาท/ปี)", min_value=0, value=0, step=1000, format="%d", key="health_insurance_input")
        capped_health_insurance = min(health_insurance, 25000)
        if health_insurance > 0:
            st.info(f"ลดหย่อนเบี้ยประกันสุขภาพ: ไม่เกิน 25,000 บาท")
        st.session_state.health_insurance = capped_health_insurance

        ##คำนวณค่าลดหย่อนเบี้ยประกันสุขภาพของบิดา-มารดา
        parent_health_insurance = st.number_input("เบี้ยประกันสุขภาพบิดา มารดา (บาท/ปี)", min_value=0, value=0, step=1000, format="%d", key="parent_health_insurance_input")
        capped_parent_health = min(parent_health_insurance, 15000)
        if parent_health_insurance > 0:
            st.info(f"ลดหย่อนเบี้ยประกันสุขภาพบิดา มารดา: ไม่เกิน 15,000 บาท")
        st.session_state.parent_health_insurance = capped_parent_health

        ##คำนวณค่าลดหย่อนเบี้ยประกันชีวิตแบบบำนาญ
        annual_salary = st.session_state.annual_salary
        annual_income = annual_salary + st.session_state.bonus + st.session_state.other_income
        pension_insurance = st.number_input("เบี้ยประกันชีวิตแบบบำนาญ (บาท/ปี)", min_value=0, value=0, step=1000, format="%d", key="pension_insurance_input")
        max_percentage = min(annual_income * 0.15, 200000)
        capped_pension = min(pension_insurance, max_percentage)
        if pension_insurance > 0:
            st.info(f"ลดหย่อนเบี้ยประกันชีวิตแบบบำนาญ: ไม่เกิน 15% ของเงินได้ (สูงสุด 200,000 บาท)")
            if capped_pension < pension_insurance:
                st.warning(f"คุณกรอกเบี้ยประกันชีวิตแบบบำนาญเกินที่กฎหมายกำหนด ระบบคำนวณให้ไม่เกิน {max_percentage:,.2f} บาท")
        st.session_state.pension_insurance = capped_pension

        ##แสดงผลรวมค่าลดหย่อนประกันทั้งหมด
        total_insurance = capped_life_insurance + capped_health_insurance + capped_parent_health + capped_pension
        st.markdown("---")
        st.info(f"รวมค่าลดหย่อนด้านประกัน: {total_insurance:,.2f} บาท")

        ##ปุ่มย้อนกลับและไปหน้าถัดไป
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ย้อนกลับ", key="back_4"):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button("ถัดไป", key="next_4"):
                st.session_state.step = 5
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Step 5: กองทุนและการบริจาคอื่นๆ
#สร้างโครงสร้างหน้าจอ
def render_step_5():
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("รายการลดหย่อนภาษี : กองทุนอื่นๆ")

        ##กองทุนบำเหน็จบำนาญข้าราชการ
        annual_salary = st.session_state.annual_salary
        annual_income = annual_salary + st.session_state.bonus + st.session_state.other_income
        government_pension = st.number_input("กองทุนบำเหน็จบำนาญข้าราชการ (กบข.)", min_value=0, value=0, step=1000, format="%d", key="government_pension_input")
        gov_pension_max = min(annual_income * 0.15, 500000)
        capped_gov_pension = min(government_pension, gov_pension_max)
        if government_pension > 0:
            st.info(f"ลดหย่อนกองทุน กบข.: ไม่เกิน 15% ของรายได้ และรวมทุกกองทุนไม่เกิน 500,000 บาท")
        st.session_state.government_pension = capped_gov_pension

        ##กองทุนออมแห่งชาติ(กอช.)
        national_savings = st.number_input("กองทุนออมแห่งชาติ (กอช.)", min_value=0, value=0, step=1000, format="%d", key="national_savings_input")
        national_max = min(13200, annual_income * 0.30)
        capped_national = min(national_savings, national_max)
        if national_savings > 0:
            st.info(f"ลดหย่อนกองทุน กอช.: ไม่เกิน 13,200 บาท และรวมกับกองทุนอื่นๆและเบี้ยประกันแบบบำนาญแล้วไม่เกิน 500,000 บาท")
        st.session_state.national_savings = capped_national

        ##กองทุนรวมเพื่อการเลี้ยงชีพ (RMF)
        rmf_contribution = st.number_input("กองทุนรวมเพื่อการเลี้ยงชีพ (RMF)", min_value=0, value=0, step=1000, format="%d", key="rmf_contribution_input")
        rmf_max = min(annual_income * 0.30, 500000)
        capped_rmf = min(rmf_contribution, rmf_max)
        if rmf_contribution > 0:
            st.info(f"ลดหย่อนกองทุน RMF: ไม่เกิน 30% ของรายได้ และรวมกับกองทุนอื่นๆและเบี้ยประกันแบบบำนาญแล้วไม่เกิน 500,000 บาท")
        st.session_state.rmf = capped_rmf

        ##ตรวจสอบว่ากองทุนเพื่อการเกษียณรวมกันเกิน500,000บาทหรือไม่
        total_retirement_funds = capped_gov_pension + capped_national + capped_rmf + st.session_state.pension_insurance
        combined_retirement_cap = 500000
        if total_retirement_funds > combined_retirement_cap:
            st.warning(f"กองทุนเพื่อการเกษียณทั้งหมด (กบข. กอช. RMF และประกันแบบบำนาญ) รวมกันแล้วเกิน {combined_retirement_cap:,} บาท ระบบจะคำนวณให้ไม่เกิน {combined_retirement_cap:,} บาท")
            if total_retirement_funds > 0:
                reduction_factor = combined_retirement_cap / total_retirement_funds
                st.session_state.government_pension = round(capped_gov_pension * reduction_factor)
                st.session_state.national_savings = round(capped_national * reduction_factor)
                st.session_state.rmf = round(capped_rmf * reduction_factor)
                st.session_state.pension_insurance = round(st.session_state.pension_insurance * reduction_factor)


        ##กองทุนอื่นๆ (SSF & Thai ESG)
        ssf_contribution = st.number_input("กองทุนรวมเพื่อการออม (SSF)", min_value=0, value=0, step=1000, format="%d", key="ssf_contribution_input")
        ssf_max = min(annual_income * 0.30, 200000)
        capped_ssf = min(ssf_contribution, ssf_max)
        if ssf_contribution > 0:
            st.info(f"ลดหย่อนกองทุน SSF: ไม่เกิน 30% ของรายได้ และไม่เกิน 200,000 บาท") ##จำกัดค่าลดหย่อน SSF: ไม่เกิน 30% ของรายได้ หรือ 200,000 บาท
        st.session_state.ssf = capped_ssf
        
        thai_esg = st.number_input("กองทุน Thai ESG", min_value=0, value=0, step=1000, format="%d", key="thai_esg_input")
        thai_esg_max = min(annual_income * 0.30, 300000)
        capped_thai_esg = min(thai_esg, thai_esg_max)
        if thai_esg > 0:
            st.info(f"ลดหย่อนกองทุน Thai ESG: ไม่เกิน 30% ของรายได้ และไม่เกิน 300,000 บาท") ##จำกัดค่าลดหย่อน Thai ESG: ไม่เกิน 30% ของรายได้ หรือ 300,000 บาท
        st.session_state.thai_esg = capped_thai_esg
        
        st.markdown("---")
        st.subheader("เงินบริจาค")
        ##คำนวณค่าลดหย่อนจากเงินบริจาค
        education_donation = st.number_input("เงินบริจาคเพื่อการศึกษา การกีฬา การพัฒนาสังคม และโรงพยาบาลรัฐ", min_value=0, value=0, step=1000, format="%d", key="education_donation_input")
        edu_donation_max = (annual_income * 0.10) * 2
        capped_edu_donation = min(education_donation, edu_donation_max)
        general_donation = st.number_input("เงินบริจาคทั่วไป", min_value=0, value=0, step=1000, format="%d", key="general_donation_input")
        general_donation_max = annual_income * 0.10
        capped_general_donation = min(general_donation, general_donation_max)
        total_donations = capped_edu_donation + capped_general_donation
        st.session_state.donation = total_donations
        ##เงินบริจาคเพื่อการศึกษาลดหย่อนได้สูงสุด10 % ของรายได้ เงินบริจาคทั่วไปลดหย่อนได้สูงสุด10 % ของรายได้

        ##ปุ่มย้อนกลับและไปหน้าถัดไป
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ย้อนกลับ", key="back_5"):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button("คำนวณภาษี", key="calculate"):
                st.session_state.step = 6
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# Step 6: ผลการคำนวณภาษี
def render_step_6(debug_mode, calculate_tax_func):
    try:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("ผลการคำนวณภาษี")

            ##การคำนวณเงินได้รวมและภาษี
            annual_salary = st.session_state.annual_salary
            annual_income = annual_salary + st.session_state.bonus + st.session_state.other_income
            income_after_personal_expense = annual_income - st.session_state.personal_expense
            ##คำนวณรายได้รวม (เงินเดือน + โบนัส + รายได้อื่นๆ) และหักค่าใช้จ่ายส่วนตัว (เช่น ค่าใช้จ่ายส่วนตัวที่ผู้ใช้กรอก) เพื่อให้ได้ เงินได้หลังหักค่าใช้จ่ายส่วนตัว

            ##การคำนวณค่าลดหย่อนภาษี
            deductions = {
                "ค่าลดหย่อนครอบครัว": st.session_state.family_deduction,
                "กองทุนสำรองเลี้ยงชีพ": st.session_state.provident_fund,
                "ประกันสังคม": st.session_state.social_security,
                "ดอกเบี้ยเงินกู้ยืมเพื่อที่อยู่อาศัย": st.session_state.home_loan_interest,
                "เบี้ยประกันชีวิต": st.session_state.life_insurance,
                "เบี้ยประกันสุขภาพ": st.session_state.health_insurance,
                "เบี้ยประกันสุขภาพบิดา มารดา": st.session_state.parent_health_insurance,
                "เบี้ยประกันชีวิตแบบบำนาญ": st.session_state.pension_insurance,
                "กองทุนบำเหน็จบำนาญข้าราชการ": st.session_state.government_pension,
                "กองทุนออมแห่งชาติ": st.session_state.national_savings,
                "เงินลงทุน RMF": st.session_state.rmf,
                "เงินลงทุน SSF": st.session_state.ssf,
                "เงินลงทุน Thai ESG": st.session_state.thai_esg,
                "เงินบริจาค": st.session_state.donation
            }
            ##สร้างdictionaryที่ประกอบไปด้วยรายการค่าลดหย่อนต่างๆที่ผู้ใช้กรอกไว้ในst.session_stateเช่นค่าลดหย่อนครอบครัว, กองทุนสำรองเลี้ยงชีพ, ประกันสังคม เป็นต้น
            deductions_without_funds = {k: v for k, v in deductions.items() if k not in ["เงินลงทุน SSF", "เงินลงทุน RMF", "เงินลงทุน Thai ESG"]}
            ##การคำนวณภาษี
            tax_without_investment_funds, taxable_without_funds, bracket_details_without_funds = calculate_tax_func(income_after_personal_expense, deductions_without_funds) ##ภาษีที่ต้องจ่าย (ก่อนหักลดหย่อนกองทุน SSF/RMF/ThaiESG)
            tax_amount, taxable_income, bracket_details = calculate_tax_func(income_after_personal_expense, deductions) ##ภาษีที่ต้องจ่าย (หลังหักลดหย่อนกองทุน SSF/RMF/ThaiESG)


            ##แสดงผลการคำนวณ
            result_dict = {
                "รายการ": ["รวมเงินได้ทั้งหมด", "หักค่าใช้จ่ายส่วนตัว", "เงินได้หลังหักค่าใช้จ่าย", "ภาษีที่ต้องจ่าย (ก่อนหักลดหย่อนกองทุน SSF/RMF/ThaiESG)"],
                "จำนวนเงิน (บาท)": [
                    "{:,.2f}".format(annual_income),
                    "{:,.2f}".format(st.session_state.personal_expense),
                    "{:,.2f}".format(income_after_personal_expense),
                    "{:,.2f}".format(tax_without_investment_funds)
                ]
            }
            for deduction_name, amount in deductions.items():
                if amount > 0:
                    result_dict["รายการ"].append(deduction_name)
                    result_dict["จำนวนเงิน (บาท)"].append("{:,.2f}".format(amount))
            result_dict["รายการ"].extend(["รวมค่าลดหย่อนทั้งหมด", "เงินได้สุทธิ (หลังหักค่าลดหย่อน)", "ภาษีที่ต้องชำระ"])
            result_dict["จำนวนเงิน (บาท)"].extend(["{:,.2f}".format(sum(deductions.values())), "{:,.2f}".format(taxable_income), "{:,.2f}".format(tax_amount)])
            result_df = pd.DataFrame(result_dict)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("<h3>รวมเงินได้สุทธิ</h3>", unsafe_allow_html=True)
                st.markdown(f'<h3 class="amount-display">{taxable_income:,.0f}</h3>', unsafe_allow_html=True)
                st.markdown("<p>บาท</p>", unsafe_allow_html=True)
            with col2:
                st.markdown("<h3>ภาษีที่ต้องจ่าย</h3>", unsafe_allow_html=True)
                if st.session_state.ssf > 0 or st.session_state.rmf > 0 or st.session_state.thai_esg > 0:
                    st.markdown(f'<h3 class="tax-display">{tax_without_investment_funds:,.0f}</h3>', unsafe_allow_html=True)
                    st.caption("(ก่อนลดหย่อนด้วย SSF/RMF/ThaiESG)")
                else:
                    st.markdown(f'<h3 class="tax-display">{tax_amount:,.0f}</h3>', unsafe_allow_html=True)
                st.markdown("<p>บาท</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            if debug_mode:
                st.subheader("รายละเอียดการคำนวณเงินได้และภาษี")
                with st.expander("ดูรายละเอียดการคำนวณ", expanded=True):
                    st.markdown(f"""
                    #### 1. รวมเงินได้ทั้งปี
                    - เงินเดือน ({st.session_state.monthly_salary:,.0f} × 12 เดือน) = {annual_salary:,.0f} บาท
                    - โบนัส = {st.session_state.bonus:,.0f} บาท
                    - รายได้อื่นๆ = {st.session_state.other_income:,.0f} บาท
                    - **รวมเงินได้ทั้งหมด = {annual_income:,.0f} บาท**
                    
                    #### 2. หักค่าใช้จ่ายส่วนตัว
                    - **ค่าใช้จ่ายส่วนตัวที่หักได้จริง = {st.session_state.personal_expense:,.0f} บาท**
                    - **เงินได้หลังหักค่าใช้จ่ายส่วนตัว = {income_after_personal_expense:,.0f} บาท**
                    
                    #### 3. หักค่าลดหย่อนอื่นๆ
                    """)
                    total_deductions = 0
                    for name, amount in deductions.items():
                        if amount > 0:
                            st.markdown(f"- {name}: {amount:,.0f} บาท")
                            total_deductions += amount
                    st.markdown(f"- **รวมค่าลดหย่อนทั้งหมด = {total_deductions:,.0f} บาท**")
                    st.markdown(f"#### 4. เงินได้สุทธิที่ต้องเสียภาษี: {taxable_income:,.0f} บาท")
                    st.markdown("#### 5. คำนวณภาษีตามขั้นบันได")
                    bracket_df = pd.DataFrame([{"ขั้นภาษี": item['bracket'], "อัตราภาษี": item['rate'], "เงินได้ในขั้น": item['income_in_bracket'], "ภาษีในขั้น": item['tax_in_bracket']} for item in bracket_details])
                    st.table(bracket_df)
                    st.markdown(f"- **ภาษีที่ต้องชำระ = {tax_amount:,.0f} บาท**")
            
            # ส่วนแสดงข้อมูลการลดหย่อนด้วยกองทุน
            st.subheader("ลดหย่อนภาษีกับกองทุน SSF / RMF / ThaiESG")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### จำนวนเงินคงเหลือที่ลงทุนได้ (บาท)")
                max_ssf = min(annual_income * 0.30, 200000)
                max_rmf = min(annual_income * 0.30, 500000)
                max_thai_esg = min(annual_income * 0.30, 300000)
                remaining_ssf = max_ssf - st.session_state.ssf
                remaining_rmf = max_rmf - st.session_state.rmf
                remaining_thai_esg = max_thai_esg - st.session_state.thai_esg
                st.markdown(f"**ลงทุน SSF อย่างเดียว**: {remaining_ssf:,.2f}")
                st.markdown(f"**ลงทุน RMF อย่างเดียว**: {remaining_rmf:,.2f}")
                st.markdown(f"**ลงทุน ThaiESG**: {remaining_thai_esg:,.2f}")
                st.markdown("กองทุนสำรองเลี้ยงชีพ, ประกันชีวิตแบบบำนาญ, กบข., กอช. และ RMF รวมกันไม่เกิน 500,000 บาท")
            with col2:
                st.markdown("### จำนวนเงินที่ตรวจสอบได้ (บาท)")
                st.number_input("ลงทุน SSF อย่างเดียว", min_value=0.0, value=0.0, key="ssf_verification")
                st.number_input("ลงทุน RMF อย่างเดียว", min_value=0.0, value=0.0, key="rmf_verification")
                st.number_input("ลงทุน ThaiESG", min_value=0.0, value=0.0, key="thai_esg_verification")
                st.info("*ข้อมูลเพื่อตรวจสอบเท่านั้นไม่มีผลต่อการคำนวณภาษี")
            funds_total = remaining_ssf + remaining_rmf + remaining_thai_esg
            st.markdown(f"<h3>สามารถลงทุนได้อีก: <span class='amount-display'>{funds_total:,.2f}</span> บาท</h3>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown(simple_pdf_download(result_df), unsafe_allow_html=True)
            

            st.markdown("---")
            st.markdown("### อัตราภาษีเงินได้บุคคลธรรมดา")
            tax_brackets_df = pd.DataFrame([
                {"เงินได้สุทธิ": "0 - 150,000", "อัตราภาษี": "ยกเว้น"},
                {"เงินได้สุทธิ": "150,001 - 500,000", "อัตราภาษี": "10%"},
                {"เงินได้สุทธิ": "500,001 - 1,000,000", "อัตราภาษี": "15%"},
                {"เงินได้สุทธิ": "1,000,001 - 2,000,000", "อัตราภาษี": "20%"},
                {"เงินได้สุทธิ": "2,000,001 - 5,000,000", "อัตราภาษี": "25%"},
                {"เงินได้สุทธิ": "5,000,001 ขึ้นไป", "อัตราภาษี": "35%"}
            ])
            st.table(tax_brackets_df)
            
            st.markdown("### วิธีคำนวณภาษี")
            st.markdown("1. นำเงินได้ทั้งหมดมาหักค่าใช้จ่ายส่วนตัว\n2. นำค่าลดหย่อนต่างๆ มาหักออก\n3. คำนวณภาษีตามตารางอัตราภาษีเงินได้บุคคลธรรมดา")

            ##ปุ่มสำหรับการย้อนกลับหรือเริ่มใหม่
            col1, col2 = st.columns(2)
            with col1:
                if st.button("ย้อนกลับ", key="back_6"):
                    st.session_state.step = 5
                    st.rerun()
            with col2:
                if st.button("เริ่มใหม่", key="restart"):
                    for key in list(st.session_state.keys()):
                        if key != "step":
                            del st.session_state[key]
                    st.session_state.step = 1
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการคำนวณภาษี: {str(e)}")
        if debug_mode:
            st.exception(e)



