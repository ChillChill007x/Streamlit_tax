# 💸 Thai Tax Calculator — เครื่องคำนวณภาษีเงินได้บุคคลธรรมดา

> **ภาษาไทย** | [English](#english-version)

---

## ภาษาไทย

### ภาพรวมโครงการ

เครื่องคำนวณภาษีเงินได้บุคคลธรรมดาประจำปี พัฒนาด้วย **Streamlit** สำหรับผู้เสียภาษีชาวไทย รองรับการคำนวณภาษีแบบขั้นบันได (Progressive Tax) ตามอัตราภาษีของกรมสรรพากร พร้อมระบบลดหย่อนภาษีในหมวดหมู่ต่าง ๆ และสามารถดาวน์โหลดผลการคำนวณในรูปแบบ PDF ได้

> ⚠️ **ข้อสงวนสิทธิ์:** ผลการคำนวณนี้เป็นเพียงการประมาณการณ์เท่านั้น โปรดตรวจสอบกับเจ้าหน้าที่สรรพากรหรือผู้เชี่ยวชาญด้านภาษีเพื่อข้อมูลอย่างเป็นทางการ

---

### คุณสมบัติหลัก

- **กรอกข้อมูลแบบ Step-by-Step** — แบ่งการกรอกข้อมูลออกเป็น 6 ขั้นตอนชัดเจน
- **คำนวณภาษีขั้นบันได** — รองรับ 7 ขั้นอัตราภาษี (0% – 35%) ตามเกณฑ์ปัจจุบัน
- **ค่าลดหย่อนครอบคลุม** — ครอบครัว, ประกันชีวิต, กองทุนสำรอง, RMF, SSF, Thai ESG และอื่น ๆ
- **โหมดแสดงรายละเอียดการคำนวณ** — เปิดใช้งานผ่าน Sidebar เพื่อดูรายละเอียดทุกขั้นภาษี
- **ดาวน์โหลดผลเป็น PDF** — รองรับฟอนต์ภาษาไทย (THSarabunNew)

---

### ขั้นตอนการใช้งาน

แอปพลิเคชันแบ่งการกรอกข้อมูลออกเป็น 6 ขั้นตอน ดังนี้

| ขั้นตอน | หัวข้อ | รายละเอียด |
|---------|--------|------------|
| 1 | รายรับ | เงินเดือน, โบนัส, รายได้อื่น ๆ |
| 2 | ลดหย่อนครอบครัว | สถานะสมรส, บุตร, บิดา-มารดา, ผู้พิการ |
| 3 | กองทุนและที่อยู่อาศัย | กองทุนสำรองเลี้ยงชีพ, ประกันสังคม, ดอกเบี้ยบ้าน |
| 4 | ประกัน | ประกันชีวิต, ประกันสุขภาพ, ประกันชีวิตบำนาญ |
| 5 | กองทุนอื่น ๆ | RMF, SSF, Thai ESG, เงินบริจาค |
| 6 | ผลการคำนวณ | สรุปภาษีที่ต้องชำระและดาวน์โหลด PDF |

---

### อัตราภาษีที่รองรับ

| ขั้นที่ | เงินได้สุทธิ (บาท) | อัตราภาษี |
|---------|--------------------|-----------|
| 1 | 0 – 150,000 | 0% |
| 2 | 150,001 – 500,000 | 5% |
| 3 | 500,001 – 1,000,000 | 15% |
| 4 | 1,000,001 – 2,000,000 | 20% |
| 5 | 2,000,001 – 5,000,000 | 25% |
| 6 | 5,000,001 ขึ้นไป | 35% |

---

### โครงสร้างโปรเจกต์

```
Streamlit_tax-main/
├── main.py           # จุดเริ่มต้นของแอปพลิเคชัน
├── calculator.py     # ตรรกะการคำนวณภาษี
├── components.py     # UI Components และฟังก์ชันสร้าง PDF
├── styles.css        # Custom CSS สำหรับสไตล์หน้าเว็บ
└── fonts/            # ฟอนต์ภาษาไทย (THSarabunNew)
    ├── THSarabunNew.ttf
    └── THSarabunNew-Bold.ttf
```

---

### การติดตั้งและรันโปรแกรม

#### ข้อกำหนดเบื้องต้น

- Python 3.8 ขึ้นไป
- pip

#### ขั้นตอนการติดตั้ง

1. **โคลนหรือดาวน์โหลดโปรเจกต์**
   ```bash
   git clone <repository-url>
   cd Streamlit_tax-main
   ```

2. **ติดตั้ง Dependencies**
   ```bash
   pip install streamlit pandas reportlab fpdf2 xhtml2pdf weasyprint
   ```

3. **วางฟอนต์ภาษาไทย**

   ดาวน์โหลดฟอนต์ `THSarabunNew.ttf` และ `THSarabunNew-Bold.ttf` แล้ววางไว้ในโฟลเดอร์ `fonts/`

4. **แก้ไข Path ของ CSS** *(สำคัญ)*

   เปิดไฟล์ `components.py` และแก้ไข path ในฟังก์ชัน `apply_custom_css()` ให้ตรงกับตำแหน่งไฟล์ `styles.css` ในเครื่องของคุณ:
   ```python
   # เปลี่ยนบรรทัดนี้
   css_path = "C:\\Users\\PC\\PycharmProjects\\Streamlit_\\styles.css"
   
   # เป็น path แบบ relative (แนะนำ)
   css_path = os.path.join(os.path.dirname(__file__), "styles.css")
   ```

5. **รันแอปพลิเคชัน**
   ```bash
   streamlit run main.py
   ```

6. เปิดเบราว์เซอร์ที่ `http://localhost:8501`

---

### Dependencies หลัก

| ไลบรารี | การใช้งาน |
|---------|-----------|
| `streamlit` | Web UI Framework |
| `pandas` | จัดการข้อมูลตาราง |
| `reportlab` | สร้าง PDF (รองรับภาษาไทย) |
| `fpdf2` | สร้าง PDF แบบ FPDF |
| `weasyprint` | แปลง HTML เป็น PDF |
| `xhtml2pdf` | แปลง HTML/CSS เป็น PDF |

---

---

## English Version

### Project Overview

A **Thai Personal Income Tax Calculator** built with **Streamlit**. The application supports progressive tax calculation according to the Revenue Department of Thailand's current tax brackets, with comprehensive deduction categories and the ability to export results as a PDF report.

> ⚠️ **Disclaimer:** Results are estimates only. Please consult a tax professional or the Revenue Department for official guidance.

---

### Key Features

- **Step-by-Step Input Flow** — Guides users through 6 clearly defined steps
- **Progressive Tax Calculation** — Supports 7 tax brackets (0% – 35%)
- **Comprehensive Deductions** — Family, insurance, provident fund, RMF, SSF, Thai ESG, and more
- **Debug Mode** — Toggle via the sidebar to inspect per-bracket tax breakdown
- **PDF Export** — Thai-language PDF report with THSarabunNew font support

---

### Input Steps

| Step | Title | Details |
|------|-------|---------|
| 1 | Income | Monthly salary, bonus, other income |
| 2 | Family Deductions | Marital status, children, parents, disabled dependents |
| 3 | Fund & Housing | Provident fund, social security, mortgage interest |
| 4 | Insurance | Life insurance, health insurance, pension insurance |
| 5 | Other Funds | RMF, SSF, Thai ESG, donations |
| 6 | Tax Summary | Tax payable summary and PDF download |

---

### Supported Tax Brackets

| Bracket | Net Taxable Income (THB) | Tax Rate |
|---------|--------------------------|----------|
| 1 | 0 – 150,000 | 0% |
| 2 | 150,001 – 500,000 | 5% |
| 3 | 500,001 – 1,000,000 | 15% |
| 4 | 1,000,001 – 2,000,000 | 20% |
| 5 | 2,000,001 – 5,000,000 | 25% |
| 6 | 5,000,001 and above | 35% |

---

### Project Structure

```
Streamlit_tax-main/
├── main.py           # Application entry point
├── calculator.py     # Tax calculation logic
├── components.py     # UI components and PDF generation
├── styles.css        # Custom CSS styles
└── fonts/            # Thai fonts (THSarabunNew)
    ├── THSarabunNew.ttf
    └── THSarabunNew-Bold.ttf
```

---

### Installation & Running

#### Prerequisites

- Python 3.8 or higher
- pip

#### Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Streamlit_tax-main
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit pandas reportlab fpdf2 xhtml2pdf weasyprint
   ```

3. **Add Thai fonts**

   Download `THSarabunNew.ttf` and `THSarabunNew-Bold.ttf` and place them in the `fonts/` directory.

4. **Fix the CSS path** *(Important)*

   Open `components.py` and update the path in `apply_custom_css()` to use a relative path:
   ```python
   # Replace this hardcoded path
   css_path = "C:\\Users\\PC\\PycharmProjects\\Streamlit_\\styles.css"
   
   # With a relative path (recommended)
   css_path = os.path.join(os.path.dirname(__file__), "styles.css")
   ```

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

6. Open your browser at `http://localhost:8501`

---

### Key Dependencies

| Library | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `pandas` | Data table management |
| `reportlab` | PDF generation with Thai font support |
| `fpdf2` | FPDF-style PDF generation |
| `weasyprint` | HTML-to-PDF conversion |
| `xhtml2pdf` | HTML/CSS-to-PDF conversion |

---

### Known Issues

- The CSS file path in `components.py` is currently hardcoded to a local Windows path and must be updated before running on any other machine.
- The `fonts/` directory and Thai font files are not included in the repository and must be added manually for PDF export to function correctly.

---

*Developed with ❤️ for Thai taxpayers.*
