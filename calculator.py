def calculate_tax(annual_income, deductions):
    # คำนวณยอดรวมค่าลดหย่อนทั้งหมด
    total_deductions = sum(deductions.values())

    # คำนวณเงินได้สุทธิที่ต้องเสียภาษี โดยเอารายได้ลบค่าลดหย่อน ต้องไม่น้อยกว่า 0
    taxable_income = max(0, annual_income - total_deductions)

    # สร้างลิสต์เพื่อเก็บรายละเอียดการคำนวณภาษีในแต่ละขั้นภาษี
    bracket_details = []

    # ตั้งค่าเริ่มต้นภาษีที่ต้องจ่าย
    tax = 0

    # ขั้นที่ 1: รายได้ 0-150,000 บาท อัตราภาษี 0%
    if taxable_income > 0:
        bracket_income = min(taxable_income, 150000)  # รายได้ในช่วงนี้
        bracket_tax = 0  # ภาษีในช่วงนี้ (0%)
        bracket_details.append({
            'bracket': "0 - 150,000",
            'rate': "0%",
            'income_in_bracket': f"{bracket_income:,.2f}",
            'tax_in_bracket': f"{bracket_tax:,.2f}"
        })

    # ขั้นที่ 2: รายได้ 150,001-500,000 บาท อัตราภาษี 5%
    if taxable_income > 150000:
        bracket_income = min(taxable_income, 500000) - 150000
        bracket_tax = bracket_income * 0.05
        tax += bracket_tax
        bracket_details.append({
            'bracket': "150,001 - 500,000",
            'rate': "5%",
            'income_in_bracket': f"{bracket_income:,.2f}",
            'tax_in_bracket': f"{bracket_tax:,.2f}"
        })

    # กำหนดขั้นภาษีที่เหลือ (ขั้นที่ 3-6)
    tax_brackets_rest = [
        (500001, 1000000, 0.15),  # ขั้นที่ 3: 500,001-1,000,000 บาท อัตรา 15%
        (1000001, 2000000, 0.20),  # ขั้นที่ 4: 1,000,001-2,000,000 บาท อัตรา 20%
        (2000001, 5000000, 0.25),  # ขั้นที่ 5: 2,000,001-5,000,000 บาท อัตรา 25%
        (5000001, float('inf'), 0.35)  # ขั้นที่ 6: 5,000,001 บาทขึ้นไป อัตรา 35%
    ]

    # คำนวณภาษีสำหรับแต่ละขั้นภาษีที่เหลือ
    for min_income, max_income, rate in tax_brackets_rest:
        if taxable_income > min_income:
            # คำนวณรายได้ในขั้นภาษีนี้
            bracket_income = min(taxable_income, max_income) - min_income
            # คำนวณภาษีในขั้นภาษีนี้
            bracket_tax = bracket_income * rate
            # บวกภาษีในขั้นนี้เข้ากับยอดรวม
            tax += bracket_tax
            # เก็บรายละเอียดการคำนวณ
            bracket_details.append({
                'bracket': f"{min_income:,} - {max_income if max_income != float('inf') else 'ขึ้นไป'}",
                'rate': f"{rate * 100:.0f}%",
                'income_in_bracket': f"{bracket_income:,.2f}",
                'tax_in_bracket': f"{bracket_tax:,.2f}"
            })

    # คืนค่าภาษีที่ต้องจ่าย (ปัดเศษ), เงินได้สุทธิ, และรายละเอียดการคำนวณ
    return round(tax), taxable_income, bracket_details