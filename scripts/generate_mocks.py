import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_prescription(filepath, doctor_name, reg_no, patient_name, date_str, diagnosis, medicines_list):
    """
    Generates a realistic medical prescription layout matching the format in sample_documents_guide.md.
    """
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # 1. Stylized Header Band with a professional medical blue color
    c.setFillColorRGB(0.06, 0.25, 0.49) # Deep blue
    c.rect(0, height - 90, width, 90, fill=True, stroke=False)
    
    # Doctor's Name & Registration Details
    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 40, doctor_name)
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 60, f"Reg. No: {reg_no}")
    c.drawString(50, height - 75, "MBBS, MD (General Medicine)")
    
    # Clinic Details
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 120, "METRO CARE CLINIC & DIAGNOSTICS")
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 135, "Building 4B, Sector 7, Medical District, PIN 560001")
    c.drawString(50, height - 148, "Phone: +91 98765 43210  |  Email: contact@metrocareclinic.com")
    
    # Divider line
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(1)
    c.line(50, height - 160, width - 50, height - 160)
    
    # Patient Details block
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 190, "Patient Name:")
    c.drawString(380, height - 190, "Date:")
    c.drawString(50, height - 210, "Diagnosis:")
    
    c.setFont("Helvetica", 10)
    c.drawString(140, height - 190, patient_name)
    c.drawString(420, height - 190, date_str)
    c.drawString(140, height - 210, diagnosis)
    
    # Second divider line
    c.line(50, height - 225, width - 50, height - 225)
    
    # Rx Symbol
    c.setFillColorRGB(0.06, 0.25, 0.49)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 265, "Rx")
    
    # Medicines List
    c.setFillColorRGB(0.1, 0.1, 0.1)
    y = height - 300
    for idx, med in enumerate(medicines_list, start=1):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(70, y, f"{idx}. {med}")
        # Add realistic dosage details
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(85, y - 13, "Dosage: 1 tablet daily (after meals) | Duration: 5 days")
        c.setFillColorRGB(0.1, 0.1, 0.1)
        y -= 35
        
    # Signature line at bottom right
    sig_y = 120
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.line(width - 220, sig_y, width - 50, sig_y)
    c.setFont("Helvetica", 10)
    c.drawString(width - 220, sig_y - 15, f"{doctor_name}")
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(width - 220, sig_y - 28, "Authorized Signature & Stamp")
    
    c.showPage()
    c.save()


def generate_bill(filepath, hospital_name, patient_name, date_str, items_dict, total_amount):
    """
    Generates a realistic hospital invoice matching the format in sample_documents_guide.md.
    """
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Draw header band
    c.setFillColorRGB(0.06, 0.25, 0.49)
    c.rect(0, height - 90, width, 90, fill=True, stroke=False)
    
    # Hospital Name & GST Number
    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 40, hospital_name.upper())
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 60, "GST No: 29AAAAA1111A1Z1")
    c.drawString(50, height - 75, "INVOICE / BILL OF SUPPLY")
    
    # Address details below header band
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 120, "12 Healthcare Road, Sector 3, Metro City, PIN 560002")
    c.drawString(50, height - 133, "Phone: +91 99887 76655 | Email: billing@hospital.com")
    
    # Divider line
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(1)
    c.line(50, height - 145, width - 50, height - 145)
    
    # Patient & Bill details
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 175, "Patient Name:")
    c.drawString(380, height - 175, "Date:")
    c.drawString(380, height - 195, "Invoice No:")
    
    c.setFont("Helvetica", 10)
    c.drawString(140, height - 175, patient_name)
    c.drawString(450, height - 175, date_str)
    # Generate dummy invoice number based on date and initials
    patient_initials = "".join([part[0] for part in patient_name.split() if part])
    c.drawString(450, height - 195, f"INV-2024-{patient_initials}-001")
    
    # Itemized Table Header
    table_top = height - 235
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(50, table_top - 20, width - 100, 20, fill=True, stroke=False)
    
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, table_top - 14, "PARTICULARS")
    c.drawRightString(width - 60, table_top - 14, "AMOUNT (Rs.)")
    
    # Table rows
    c.setFont("Helvetica", 10)
    y = table_top - 40
    for item, amount in items_dict.items():
        c.drawString(60, y, item)
        c.drawRightString(width - 60, y, f"{amount:.2f}")
        # Draw light gray border between rows
        c.setStrokeColorRGB(0.9, 0.9, 0.9)
        c.line(50, y - 6, width - 50, y - 6)
        y -= 25
        
    # Divider for totals
    y -= 10
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.line(50, y, width - 50, y)
    
    # Total Amount (Bolded)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y - 20, "TOTAL")
    c.drawRightString(width - 60, y - 20, f"Rs. {total_amount:.2f}")
    
    # Stamp / Signature section at bottom
    sig_y = 120
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.line(width - 220, sig_y, width - 50, sig_y)
    c.setFont("Helvetica", 9)
    c.drawString(width - 220, sig_y - 15, "Authorized Signatory")
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(width - 220, sig_y - 28, f"For {hospital_name}")
    
    c.showPage()
    c.save()


if __name__ == "__main__":
    # Ensure target directory exists
    mocks_dir = os.path.join("backend", "data", "mocks")
    os.makedirs(mocks_dir, exist_ok=True)
    
    # Generate files for TC001
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc001_prescription.pdf"),
        doctor_name="Dr. Sharma",
        reg_no="KA/45678/2015",
        patient_name="Rajesh Kumar",
        date_str="2024-11-01",
        diagnosis="Viral fever",
        medicines_list=["Paracetamol 650mg", "Vitamin C"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc001_bill.pdf"),
        hospital_name="Local Clinic",
        patient_name="Rajesh Kumar",
        date_str="2024-11-01",
        items_dict={"Consultation Fee": 1000.0, "Diagnostic Tests": 500.0},
        total_amount=1500.0
    )
    
    # Generate files for TC002
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc002_prescription.pdf"),
        doctor_name="Dr. Patel",
        reg_no="MH/23456/2018",
        patient_name="Priya Singh",
        date_str="2024-10-15",
        diagnosis="Tooth decay requiring root canal",
        medicines_list=["Root canal treatment", "Teeth whitening"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc002_bill.pdf"),
        hospital_name="Smile Dental",
        patient_name="Priya Singh",
        date_str="2024-10-15",
        items_dict={"Root canal": 8000.0, "Teeth whitening": 4000.0},
        total_amount=12000.0
    )
    
    # Generate files for TC003
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc003_prescription.pdf"),
        doctor_name="Dr. Gupta",
        reg_no="DL/34567/2016",
        patient_name="Amit Verma",
        date_str="2024-10-20",
        diagnosis="Gastroenteritis",
        medicines_list=["Antibiotics", "Probiotics"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc003_bill.pdf"),
        hospital_name="City Gastro Center",
        patient_name="Amit Verma",
        date_str="2024-10-20",
        items_dict={"Consultation Fee": 2000.0, "Medicines": 5500.0},
        total_amount=7500.0
    )
    
    # Generate files for TC004 (Missing Documents - prescription is missing)
    # Only bill should be generated.
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc004_bill.pdf"),
        hospital_name="General Care Clinic",
        patient_name="Sneha Reddy",
        date_str="2024-10-25",
        items_dict={"Consultation Fee": 1500.0, "Medicines": 500.0},
        total_amount=2000.0
    )
    
    # Generate files for TC005
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc005_prescription.pdf"),
        doctor_name="Dr. Mehta",
        reg_no="GJ/56789/2014",
        patient_name="Vikram Joshi",
        date_str="2024-10-15",
        diagnosis="Type 2 Diabetes",
        medicines_list=["Metformin", "Glimepiride"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc005_bill.pdf"),
        hospital_name="City Hospital",
        patient_name="Vikram Joshi",
        date_str="2024-10-15",
        items_dict={"Consultation Fee": 1000.0, "Medicines": 2000.0},
        total_amount=3000.0
    )
    
    # Generate files for TC006
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc006_prescription.pdf"),
        doctor_name="Vaidya Krishnan",
        reg_no="AYUR/KL/2345/2019",
        patient_name="Kavita Nair",
        date_str="2024-10-28",
        diagnosis="Chronic joint pain",
        medicines_list=["Panchakarma therapy"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc006_bill.pdf"),
        hospital_name="Kerala Ayurveda Bhavan",
        patient_name="Kavita Nair",
        date_str="2024-10-28",
        items_dict={"Consultation Fee": 1000.0, "Therapy Charges": 3000.0},
        total_amount=4000.0
    )
    
    # Generate files for TC007
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc007_prescription.pdf"),
        doctor_name="Dr. Rao",
        reg_no="AP/67890/2017",
        patient_name="Suresh Patil",
        date_str="2024-11-02",
        diagnosis="Suspected lumbar disc herniation",
        medicines_list=["MRI Lumbar Spine"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc007_bill.pdf"),
        hospital_name="Metro Diagnostics & Scan",
        patient_name="Suresh Patil",
        date_str="2024-11-02",
        items_dict={"MRI Scan": 15000.0},
        total_amount=15000.0
    )
    
    # Generate files for TC008
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc008_prescription.pdf"),
        doctor_name="Dr. Khan",
        reg_no="UP/45678/2016",
        patient_name="Ravi Menon",
        date_str="2024-10-30",
        diagnosis="Migraine",
        medicines_list=["Sumatriptan", "Propranolol"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc008_bill.pdf"),
        hospital_name="Neuro Headache Clinic",
        patient_name="Ravi Menon",
        date_str="2024-10-30",
        items_dict={"Consultation Fee": 2000.0, "Medicines": 2800.0},
        total_amount=4800.0
    )
    
    # Generate files for TC009
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc009_prescription.pdf"),
        doctor_name="Dr. Banerjee",
        reg_no="WB/34567/2015",
        patient_name="Anita Desai",
        date_str="2024-10-18",
        diagnosis="Obesity - BMI 35",
        medicines_list=["Bariatric consultation and diet plan"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc009_bill.pdf"),
        hospital_name="Wellness Obesity Center",
        patient_name="Anita Desai",
        date_str="2024-10-18",
        items_dict={"Consultation Fee": 3000.0, "Diet Plan": 5000.0},
        total_amount=8000.0
    )
    
    # Generate files for TC010
    generate_prescription(
        filepath=os.path.join(mocks_dir, "tc010_prescription.pdf"),
        doctor_name="Dr. Iyer",
        reg_no="TN/56789/2013",
        patient_name="Deepak Shah",
        date_str="2024-11-03",
        diagnosis="Acute bronchitis",
        medicines_list=["Antibiotics", "Bronchodilators"]
    )
    generate_bill(
        filepath=os.path.join(mocks_dir, "tc010_bill.pdf"),
        hospital_name="Apollo Hospitals",
        patient_name="Deepak Shah",
        date_str="2024-11-03",
        items_dict={"Consultation Fee": 1500.0, "Medicines": 3000.0},
        total_amount=4500.0
    )
    
    print("Successfully generated all mock PDFs in backend/data/mocks/")
