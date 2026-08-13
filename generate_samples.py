"""
Generates 3 sample documents for the demo:
  1. sample_docs/techsolutions_msa.pdf   — standard MSA (high confidence → auto-approve)
  2. sample_docs/globalsoft_sow.png      — SOW as scanned image (medium confidence → review)
  3. sample_docs/vendors_data.csv        — CSV with vendor/contract metadata (batch)
"""
import os
import csv
import io
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. PDF — Master Service Agreement (TechSolutions Ltd)
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf_msa():
    filepath = os.path.join(OUTPUT_DIR, "techsolutions_msa.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, spaceAfter=12)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceAfter=8)
    body = styles["BodyText"]
    body.fontSize = 10
    body.leading = 14

    story = []

    story.append(Paragraph("MASTER SERVICE AGREEMENT", h1))
    story.append(Paragraph("Contract Reference: MSA-2026-TechSol-0042", body))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("PARTIES", h2))
    story.append(Paragraph(
        "This Master Service Agreement ('Agreement') is entered into as of <b>1 September 2026</b> "
        "by and between <b>TechSolutions Ltd</b>, a company incorporated in England and Wales "
        "(Registration No. <b>GB-12345678</b>), with its registered office at "
        "100 Tech Park, London, EC2A 4NE, United Kingdom "
        "('Vendor'), and <b>Acme Corporation Ltd</b>, a company registered in Ireland "
        "('Client').",
        body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("1. SERVICES", h2))
    story.append(Paragraph(
        "Vendor shall provide cloud-based SaaS platform services, including data integration, "
        "analytics dashboard, API access, and 24/7 technical support as described in Schedule A.",
        body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2. CONTRACT TERM & VALUE", h2))
    data = [
        ["Field", "Value"],
        ["Contract Type", "Master Service Agreement (MSA)"],
        ["Total Contract Value", "USD 180,000"],
        ["Annual Value", "USD 60,000"],
        ["Contract Start Date", "2026-09-01"],
        ["Contract End Date", "2029-08-31"],
        ["Contract Duration", "3 years"],
        ["Auto-Renewal", "Yes — 1 year, with 60-day opt-out notice"],
    ]
    t = Table(data, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3. PAYMENT TERMS", h2))
    story.append(Paragraph(
        "Client shall pay invoices within <b>Net-30 days</b> of receipt. Payments shall be made "
        "in USD by bank transfer. Late payments accrue interest at 2% per annum above base rate. "
        "Annual license fees are invoiced quarterly in advance.",
        body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4. SERVICE LEVEL AGREEMENT", h2))
    sla_data = [
        ["SLA Parameter", "Commitment"],
        ["Platform Uptime", "99.9% monthly (Tier 2 Business Critical)"],
        ["Critical Incident Response", "Within 1 hour"],
        ["Standard Incident Response", "Within 4 hours"],
        ["Scheduled Maintenance", "48-hour notice required"],
        ["SLA Penalty", "5% monthly fee credit per breach"],
    ]
    t2 = Table(sla_data, colWidths=[7*cm, 9*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fff4")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5. LIABILITY & INDEMNIFICATION", h2))
    story.append(Paragraph(
        "Each party's total aggregate liability shall not exceed <b>USD 180,000</b> (1x annual contract value). "
        "Vendor indemnifies Client against third-party IP infringement claims. "
        "Mutual indemnification applies for negligence and willful misconduct. "
        "Consequential damages are excluded for ordinary service disruptions.",
        body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("6. DATA PROTECTION & GDPR", h2))
    story.append(Paragraph(
        "Vendor confirms GDPR compliance. A separate Data Processing Agreement (DPA) is incorporated "
        "by reference. All EU personal data remains within the EU/UK/EEA. "
        "Vendor holds SOC2 Type II certification. Data breach notification within 72 hours.",
        body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("7. TERMINATION", h2))
    story.append(Paragraph(
        "Either party may terminate for convenience with <b>60 days</b> written notice. "
        "Either party may terminate for cause (material breach, insolvency) with 30 days notice "
        "to cure. No early termination penalty applies for termination for convenience.",
        body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("8. GOVERNING LAW & DISPUTE RESOLUTION", h2))
    story.append(Paragraph(
        "This Agreement is governed by the laws of <b>England and Wales</b>. "
        "Disputes shall be resolved by mediation, failing which by arbitration under LCIA rules "
        "in London.",
        body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("9. KEY DELIVERABLES", h2))
    story.append(Paragraph("• SaaS platform access (multi-tenant, SSO-enabled)", body))
    story.append(Paragraph("• REST API with documentation and sandbox environment", body))
    story.append(Paragraph("• Monthly usage reports and quarterly business reviews", body))
    story.append(Paragraph("• Dedicated customer success manager", body))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("SIGNATORIES", h2))
    story.append(Paragraph(
        "Signed on behalf of TechSolutions Ltd: James Thornton, CEO | j.thornton@techsolutions-ltd.com | +44 20 7946 0391",
        body))
    story.append(Paragraph(
        "Signed on behalf of Acme Corporation Ltd: Sarah Chen, CPO | s.chen@acmecorp.com",
        body))

    doc.build(story)
    print(f"Generated: {filepath}")
    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# 2. PNG image — Scanned Statement of Work (GlobalSoft Solutions)
# ─────────────────────────────────────────────────────────────────────────────
def generate_image_sow():
    filepath = os.path.join(OUTPUT_DIR, "globalsoft_sow.png")

    width, height = 1240, 1754  # A4 at 150dpi
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 52)
        font_h2 = ImageFont.truetype("arial.ttf", 36)
        font_body = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font_title = font_h2 = font_body = font_small = ImageFont.load_default()

    # Header bar
    draw.rectangle([0, 0, width, 100], fill=(44, 62, 80))
    draw.text((60, 28), "STATEMENT OF WORK", fill=(255, 255, 255), font=font_title)
    draw.text((width - 400, 38), "SOW-2026-GS-008", fill=(200, 220, 240), font=font_body)

    y = 130
    draw.text((60, y), "VENDOR DETAILS", fill=(39, 174, 96), font=font_h2)
    y += 50
    lines = [
        "Vendor:  GlobalSoft Solutions",
        "Reg No:  IN-33445566",
        "Address: 500 Tech Hub, Bangalore, India 560001",
        "Contact: procurement@globalsoft.in | +91 80 4567 8900",
    ]
    for line in lines:
        draw.text((60, y), line, fill=(30, 30, 30), font=font_body)
        y += 40

    y += 20
    draw.text((60, y), "CONTRACT DETAILS", fill=(39, 174, 96), font=font_h2)
    y += 50
    details = [
        ("Contract Type", "Statement of Work (SOW)"),
        ("Contract ID", "SOW-2026-GS-008"),
        ("Total Value", "EUR 95,000"),
        ("Payment Terms", "Net-45 (milestone-based)"),
        ("Start Date", "2026-10-01"),
        ("End Date", "2027-03-31"),
        ("Governing Law", "England and Wales"),
        ("Auto-Renewal", "No"),
        ("Notice Period", "30 days"),
    ]
    for label, value in details:
        draw.text((60, y), f"{label}:", fill=(80, 80, 80), font=font_small)
        draw.text((320, y), value, fill=(20, 20, 20), font=font_body)
        y += 42

    y += 20
    draw.text((60, y), "SERVICES & DELIVERABLES", fill=(39, 174, 96), font=font_h2)
    y += 50
    deliverables = [
        "* Custom data pipeline development (Phase 1: ETL)",
        "* API integration with client ERP system",
        "* Quality assurance testing & documentation",
        "* Deployment support & knowledge transfer",
        "* 3-month post-launch support package",
    ]
    for d in deliverables:
        draw.text((60, y), d, fill=(30, 30, 30), font=font_body)
        y += 38

    y += 20
    draw.text((60, y), "SLA COMMITMENTS", fill=(39, 174, 96), font=font_h2)
    y += 50
    slas = [
        ("Uptime Guarantee", "99.5%"),
        ("Critical Bug Response", "4 hours"),
        ("Standard Response", "24 hours"),
        ("SLA Penalty", "5% monthly fee per breach"),
    ]
    for label, value in slas:
        draw.text((60, y), f"{label}: {value}", fill=(30, 30, 30), font=font_body)
        y += 38

    y += 20
    draw.text((60, y), "COMPLIANCE", fill=(39, 174, 96), font=font_h2)
    y += 50
    compliance = [
        "GDPR Compliant: Yes  |  DPA: Attached",
        "Liability Cap: EUR 95,000 (1x contract value)",
        "IP Ownership: Client retains all developed IP",
        "Termination for Convenience: Yes (30 days notice)",
        "Dispute Resolution: ICC Arbitration, London",
    ]
    for line in compliance:
        draw.text((60, y), line, fill=(30, 30, 30), font=font_body)
        y += 38

    y += 30
    draw.line([(60, y), (width - 60, y)], fill=(200, 200, 200), width=2)
    y += 20
    draw.text((60, y), "Authorised by: Priya Sharma, Director of Engineering  |  2026-09-15", fill=(100, 100, 100), font=font_small)
    y += 30
    draw.text((60, y), "NOTE: Vendor on Tier 3 Pending Approval list — manual review required.", fill=(200, 50, 50), font=font_small)

    # Add slight paper texture / noise effect
    import random
    for _ in range(3000):
        x = random.randint(0, width - 1)
        y_n = random.randint(0, height - 1)
        gray = random.randint(200, 245)
        img.putpixel((x, y_n), (gray, gray, gray))

    img.save(filepath, format="PNG", dpi=(150, 150))
    print(f"Generated: {filepath}")
    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# 3. CSV — Vendor contract summary batch data
# ─────────────────────────────────────────────────────────────────────────────
def generate_csv_batch():
    filepath = os.path.join(OUTPUT_DIR, "vendor_contracts_batch.csv")
    rows = [
        {
            "contract_id": "MSA-2025-APX-001",
            "vendor_name": "Apex Consulting Group",
            "vendor_registration": "US-44556677",
            "contract_type": "MSA",
            "contract_value_usd": 320000,
            "payment_terms": "Net-30",
            "start_date": "2025-01-15",
            "end_date": "2027-01-14",
            "governing_law": "New York, USA",
            "sla_uptime_percent": 99.9,
            "sla_response_hours": 1,
            "auto_renewal": "Yes",
            "notice_period_days": 90,
            "gdpr_compliant": "Yes",
            "dpa_signed": "Yes",
            "liability_cap_usd": 640000,
            "termination_for_convenience": "Yes",
            "ip_ownership": "Client",
            "risk_level": "LOW",
            "notes": "Long-standing Tier 1 vendor, renewal from MSA-2023-APX-001",
        },
        {
            "contract_id": "SaaS-2026-CS-017",
            "vendor_name": "CloudSecure GmbH",
            "vendor_registration": "DE-55443322",
            "contract_type": "SaaS License",
            "contract_value_usd": 75000,
            "payment_terms": "Net-30",
            "start_date": "2026-07-01",
            "end_date": "2027-06-30",
            "governing_law": "Germany",
            "sla_uptime_percent": 99.99,
            "sla_response_hours": 0.25,
            "auto_renewal": "Yes",
            "notice_period_days": 60,
            "gdpr_compliant": "Yes",
            "dpa_signed": "Yes",
            "liability_cap_usd": 150000,
            "termination_for_convenience": "Yes",
            "ip_ownership": "Vendor (SaaS)",
            "risk_level": "LOW",
            "notes": "Cybersecurity platform, mission-critical Tier 1 SLA",
        },
        {
            "contract_id": "CONS-2026-MG-005",
            "vendor_name": "Meridian Group",
            "vendor_registration": "CA-87654321",
            "contract_type": "Professional Services",
            "contract_value_usd": 280000,
            "payment_terms": "Net-45",
            "start_date": "2026-09-01",
            "end_date": "2026-12-31",
            "governing_law": "Ontario, Canada",
            "sla_uptime_percent": "",
            "sla_response_hours": 24,
            "auto_renewal": "No",
            "notice_period_days": 60,
            "gdpr_compliant": "Yes",
            "dpa_signed": "No",
            "liability_cap_usd": 280000,
            "termination_for_convenience": "Yes",
            "ip_ownership": "Client",
            "risk_level": "MEDIUM",
            "notes": "Tier 2 vendor — requires VP approval >$250K. DPA outstanding.",
        },
        {
            "contract_id": "INT-2026-DB-022",
            "vendor_name": "DataBridge Inc",
            "vendor_registration": "US-98765432",
            "contract_type": "Integration Services",
            "contract_value_usd": 48000,
            "payment_terms": "Net-30",
            "start_date": "2026-08-15",
            "end_date": "2027-08-14",
            "governing_law": "New York, USA",
            "sla_uptime_percent": 99.5,
            "sla_response_hours": 4,
            "auto_renewal": "No",
            "notice_period_days": 30,
            "gdpr_compliant": "Yes",
            "dpa_signed": "Yes",
            "liability_cap_usd": 96000,
            "termination_for_convenience": "Yes",
            "ip_ownership": "Client",
            "risk_level": "LOW",
            "notes": "Standard data integration contract, all terms within policy",
        },
        {
            "contract_id": "VENDOR-2026-UNKN-099",
            "vendor_name": "FutureTech Systems",
            "vendor_registration": "XX-00000000",
            "contract_type": "Software Development",
            "contract_value_usd": 500000,
            "payment_terms": "Net-7",
            "start_date": "2026-10-01",
            "end_date": "2027-09-30",
            "governing_law": "Cayman Islands",
            "sla_uptime_percent": "",
            "sla_response_hours": "",
            "auto_renewal": "Yes",
            "notice_period_days": 7,
            "gdpr_compliant": "Unknown",
            "dpa_signed": "No",
            "liability_cap_usd": "",
            "termination_for_convenience": "No",
            "ip_ownership": "Vendor",
            "risk_level": "HIGH",
            "notes": "RED FLAGS: Net-7 terms, Cayman Islands jurisdiction, no termination for convenience, vendor owns IP, not in approved registry, under due diligence",
        },
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated: {filepath}")
    return filepath


if __name__ == "__main__":
    print("Generating sample documents...")
    generate_pdf_msa()
    generate_image_sow()
    generate_csv_batch()
    print("\nAll sample documents generated in sample_docs/")
