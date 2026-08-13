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


# ─────────────────────────────────────────────────────────────────────────────
# 4. PDF — SaaS License Agreement (CloudSecure GmbH) — Tier 1, expect AUTO_APPROVE
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf_cloudsecure():
    filepath = os.path.join(OUTPUT_DIR, "cloudsecure_saas.pdf")
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
    story.append(Paragraph("SAAS LICENSE AGREEMENT", h1))
    story.append(Paragraph("Contract Reference: SAAS-2026-CS-017", body))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("PARTIES", h2))
    story.append(Paragraph(
        "This SaaS License Agreement ('Agreement') is entered into as of <b>1 July 2026</b> "
        "by and between <b>CloudSecure GmbH</b>, registered in Germany (Reg. No. <b>DE-55443322</b>), "
        "Hauptstrasse 42, 80331 Munich, Germany ('Vendor'), and <b>Acme Corporation Ltd</b> ('Client').", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("1. SERVICES", h2))
    story.append(Paragraph(
        "Vendor provides cloud-based cybersecurity platform services including threat intelligence, "
        "endpoint detection & response (EDR), SIEM integration, automated incident response, and "
        "24/7 Security Operations Centre (SOC) monitoring.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2. CONTRACT TERM & VALUE", h2))
    data = [
        ["Field", "Value"],
        ["Contract Type", "SaaS License Agreement"],
        ["Annual License Fee", "EUR 75,000"],
        ["Total Contract Value", "EUR 75,000 (1-year initial term)"],
        ["Start Date", "2026-07-01"],
        ["End Date", "2027-06-30"],
        ["Auto-Renewal", "Yes — annual, with 60-day opt-out notice"],
        ["Payment Terms", "Net-30 — invoiced quarterly in advance"],
    ]
    t = Table(data, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eaf4fb")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3. SERVICE LEVEL AGREEMENT", h2))
    sla_data = [
        ["SLA Parameter", "Commitment"],
        ["Platform Uptime", "99.99% monthly (Four Nines — Tier 1 Critical)"],
        ["Critical Alert Response", "Within 15 minutes"],
        ["Standard Incident Response", "Within 1 hour"],
        ["Scheduled Maintenance", "72-hour advance notice"],
        ["SLA Penalty", "10% monthly fee credit per 0.1% uptime breach"],
    ]
    t2 = Table(sla_data, colWidths=[7*cm, 9*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e8449")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eafaf1")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4. LIABILITY & INDEMNIFICATION", h2))
    story.append(Paragraph(
        "Each party's total liability shall not exceed <b>EUR 150,000</b> (2x annual contract value). "
        "Vendor provides full IP indemnification. Mutual indemnification for negligence. "
        "Consequential damages excluded except for data breaches.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5. DATA PROTECTION", h2))
    story.append(Paragraph(
        "GDPR compliant. Data Processing Agreement (DPA) attached as Annex A. "
        "All EU personal data processed within EU/EEA. SOC 2 Type II certified (cert. no. CS-SOC2-2026). "
        "ISO 27001 certified. Data breach notification within 24 hours. "
        "Client retains full data ownership and portability rights.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("6. INTELLECTUAL PROPERTY", h2))
    story.append(Paragraph(
        "Vendor retains ownership of the platform. Client retains ownership of all Client data, "
        "configurations, and any custom integrations developed specifically for Client.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("7. TERMINATION", h2))
    story.append(Paragraph(
        "Either party may terminate for convenience with <b>60 days</b> written notice. "
        "Immediate termination for cause (material breach, insolvency). "
        "Pro-rated refund of pre-paid fees on termination for convenience.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("8. GOVERNING LAW", h2))
    story.append(Paragraph(
        "Governed by <b>German law</b>. Disputes resolved by Munich Commercial Court. "
        "English translation of this Agreement prevails in case of conflict.", body))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("SIGNATORIES", h2))
    story.append(Paragraph(
        "Vendor: Klaus Weber, CEO — k.weber@cloudsecure.de | Signed: 2026-06-25", body))
    story.append(Paragraph(
        "Client: Sarah Thompson, CPO — s.thompson@acmecorp.com | Signed: 2026-06-28", body))

    doc.build(story)
    print(f"Generated: {filepath}")
    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# 5. PDF — High-Risk Dev Contract (FutureTech Systems) — Tier 3 Pending, expect REJECT
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf_futuretech():
    filepath = os.path.join(OUTPUT_DIR, "futuretech_development.pdf")
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
    story.append(Paragraph("SOFTWARE DEVELOPMENT AGREEMENT", h1))
    story.append(Paragraph("Contract Reference: DEV-2026-FT-099", body))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("PARTIES", h2))
    story.append(Paragraph(
        "This Agreement is entered into as of <b>1 October 2026</b> between "
        "<b>FutureTech Systems Ltd</b>, incorporated in the Cayman Islands (Reg. No. <b>XX-00000000</b>), "
        "PO Box 1234, George Town, Grand Cayman ('Vendor'), and Acme Corporation Ltd ('Client').", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("1. SERVICES", h2))
    story.append(Paragraph(
        "Vendor shall develop a bespoke trading algorithm and high-frequency data processing platform "
        "for Client. All source code, algorithms, models, and derivative works shall remain the "
        "<b>sole and exclusive intellectual property of Vendor</b> at all times.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2. CONTRACT TERMS", h2))
    data = [
        ["Field", "Value"],
        ["Contract Type", "Software Development Agreement"],
        ["Total Contract Value", "USD 500,000"],
        ["Payment Terms", "Net-7 days — full payment within 7 days of invoice"],
        ["Start Date", "2026-10-01"],
        ["End Date", "2027-09-30"],
        ["Auto-Renewal", "Yes — automatically renews annually unless terminated"],
        ["Notice Period", "7 days written notice required to terminate"],
        ["Governing Law", "Cayman Islands — Grand Cayman"],
        ["Dispute Resolution", "Private arbitration, venue at Vendor's sole discretion"],
    ]
    t = Table(data, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7b241c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fdedec")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3. LIABILITY", h2))
    story.append(Paragraph(
        "Vendor's total liability under this Agreement is capped at <b>USD 1,000</b> (one thousand dollars). "
        "Client waives all rights to consequential, indirect, or punitive damages. "
        "No indemnification is provided for third-party claims.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4. DATA & COMPLIANCE", h2))
    story.append(Paragraph(
        "GDPR compliance: <b>Not applicable — Vendor is not a data processor</b>. "
        "No Data Processing Agreement. No SLA commitments provided. "
        "Vendor may use Client data for its own product development and model training.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5. TERMINATION", h2))
    story.append(Paragraph(
        "<b>Client may NOT terminate for convenience.</b> "
        "Early termination by Client triggers a penalty equal to the full remaining contract value. "
        "Vendor may terminate with 7 days notice and retain all fees paid.", body))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("SIGNATORIES", h2))
    story.append(Paragraph(
        "Vendor: J. Smith, Director — futuretech@offshore-email.ky | Signed: 2026-09-28", body))
    story.append(Paragraph(
        "Client: Sarah Thompson, CPO — s.thompson@acmecorp.com | Signed: 2026-09-30", body))

    doc.build(story)
    print(f"Generated: {filepath}")
    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# 6. CSV — DataBridge Integration Contract — Tier 1, clean terms, expect AUTO_APPROVE
# ─────────────────────────────────────────────────────────────────────────────
def generate_csv_databridge():
    filepath = os.path.join(OUTPUT_DIR, "databridge_integration.csv")
    rows = [
        ("contract_id", "INT-2026-DB-022"),
        ("contract_title", "Data Integration Services Agreement"),
        ("vendor_name", "DataBridge Inc"),
        ("vendor_registration_number", "US-98765432"),
        ("vendor_address", "200 Data Way, Austin, TX 78701, USA"),
        ("vendor_contact_email", "contracts@databridgeinc.com"),
        ("vendor_contact_phone", "+1 512 555 0200"),
        ("contract_type", "Integration Services"),
        ("contract_value_total", "48000"),
        ("contract_value_currency", "USD"),
        ("payment_terms", "Net-30"),
        ("payment_schedule", "Monthly invoicing in arrears"),
        ("start_date", "2026-08-15"),
        ("end_date", "2027-08-14"),
        ("auto_renewal", "No"),
        ("notice_period_days", "30"),
        ("governing_law", "Texas - United States"),
        ("dispute_resolution", "AAA Arbitration - Austin TX"),
        ("liability_cap", "96000"),
        ("liability_cap_currency", "USD"),
        ("indemnification_clause", "Yes"),
        ("ip_ownership", "Client owns all deliverables and integrations"),
        ("data_processing_agreement", "Yes"),
        ("gdpr_compliant", "Yes"),
        ("sla_uptime_percentage", "99.5"),
        ("sla_response_time_hours", "4"),
        ("sla_penalty_clause", "Yes"),
        ("termination_for_convenience", "Yes"),
        ("termination_for_cause", "Yes"),
        ("services_description", "ETL pipeline development, API integration with client ERP and CRM systems, data quality monitoring"),
        ("key_deliverable_1", "ETL pipeline from 3 source systems to data warehouse"),
        ("key_deliverable_2", "ERP/CRM API connectors with real-time sync"),
        ("key_deliverable_3", "Data quality dashboard and alerting"),
        ("key_deliverable_4", "Technical documentation and runbooks"),
        ("signatory_vendor", "Marcus Nguyen - VP Engineering"),
        ("signatory_client", "Sarah Thompson - Chief Procurement Officer"),
        ("execution_date", "2026-08-10"),
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["field", "value"])
        writer.writerows(rows)
    print(f"Generated: {filepath}")
    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# 7. PDF — Clean SaaS contract designed to satisfy all policy checks (AUTO_APPROVE)
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf_nexus_clean():
    filepath = os.path.join(OUTPUT_DIR, "nexus_saas_clean.pdf")
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
    story.append(Paragraph("SAAS PLATFORM LICENSE AGREEMENT", h1))
    story.append(Paragraph("Contract Reference: SAAS-2026-CS-AUTO-001", body))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("PARTIES", h2))
    story.append(Paragraph(
        "This SaaS Platform License Agreement ('Agreement') is entered into as of <b>1 September 2026</b> "
        "by and between <b>CloudSecure GmbH</b>, a company incorporated in Germany "
        "(Registration No. <b>DE-55443322</b>), with its principal office at "
        "Hauptstrasse 42, 80331 Munich, Germany ('Vendor'), "
        "and <b>Flat Rock Technology Ltd</b>, a company registered in England and Wales ('Client').", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("VENDOR REGISTRY STATUS", h2))
    story.append(Paragraph(
        "CloudSecure GmbH is registered as a <b>Tier 1 Approved Vendor</b> in the Client's "
        "Approved Vendors Registry (Registry ID: CS-T1-2023-007, valid through 2026-12-31). "
        "All due diligence checks, including financial stability review, security audit, and "
        "reference checks, were completed and passed with no adverse findings. "
        "Vendor contact: Klaus Weber, CEO (k.weber@cloudsecure.de, +49 89 555 0100).", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("1. SERVICES", h2))
    story.append(Paragraph(
        "Vendor shall provide cloud-hosted data analytics SaaS platform services, including: "
        "(a) real-time business intelligence dashboards; (b) automated reporting and data exports; "
        "(c) REST API access for third-party integrations; (d) dedicated customer success management; "
        "and (e) standard 9-to-5 technical support with emergency out-of-hours coverage for P1 incidents. "
        "No custom software development is involved — this is a standard SaaS subscription. "
        "No source code escrow is required or applicable under this Agreement.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2. CONTRACT TERM &amp; FINANCIAL TERMS", h2))
    data = [
        ["Field", "Value"],
        ["Contract Type", "SaaS Platform License Agreement"],
        ["Annual License Fee", "USD 45,000"],
        ["Total Contract Value", "USD 45,000 (12-month initial term)"],
        ["Contract Start Date", "2026-09-01"],
        ["Contract End Date", "2027-08-31"],
        ["Auto-Renewal", "No — manual renewal required"],
        ["Payment Terms", "Net-30 — invoiced quarterly in arrears"],
        ["Payment Schedule", "Quarterly in arrears: USD 11,250 per quarter"],
        ["Notice Period", "60 days written notice for termination for convenience"],
    ]
    t = Table(data, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c5e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        "<b>Modern Slavery Act 2015 compliance note:</b> The annual contract value is USD 45,000, "
        "which is below the USD 100,000 threshold requiring a formal Modern Slavery Act statement. "
        "Accordingly, no Modern Slavery attestation is required for this Agreement. "
        "Vendor voluntarily confirms that its supply chain practices comply with the Act.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3. SERVICE LEVEL AGREEMENT", h2))
    sla_data = [
        ["SLA Parameter", "Commitment"],
        ["Platform Uptime", "99.9% monthly (Nines SLA)"],
        ["P1 Incident Response", "Within 1 hour (24/7)"],
        ["P2 Incident Response", "Within 4 hours (business hours)"],
        ["Scheduled Maintenance", "48-hour advance notice; max 4 hours/month"],
        ["SLA Penalty", "5% monthly fee credit per 0.1% uptime shortfall"],
        ["SLA Reporting", "Monthly uptime report delivered by 5th of following month"],
    ]
    t2 = Table(sla_data, colWidths=[7*cm, 9*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e6b3a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#edf7f0")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4. LIABILITY &amp; INDEMNIFICATION", h2))
    story.append(Paragraph(
        "Each party's total aggregate liability under this Agreement shall not exceed "
        "<b>USD 90,000</b> (equivalent to 2x annual contract value), except for: "
        "(i) death or personal injury caused by negligence; (ii) fraud or fraudulent misrepresentation; "
        "and (iii) breaches of data protection obligations. "
        "Vendor provides intellectual property indemnification. Mutual indemnification for negligence. "
        "Consequential, indirect, or punitive damages are excluded. "
        "Vendor maintains professional indemnity insurance of <b>USD 5,000,000</b> and public liability "
        "insurance of <b>USD 2,000,000</b> — certificates provided to Client prior to execution.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5. DATA PROTECTION &amp; SECURITY", h2))
    story.append(Paragraph(
        "5.1 <b>GDPR Compliance:</b> Vendor processes all personal data in accordance with the UK GDPR "
        "and Data Protection Act 2018. A Data Processing Agreement (DPA) is attached as Annexure A "
        "and forms part of this Agreement. All processing occurs within the UK and EEA.", body))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "5.2 <b>Security Certifications:</b> Vendor holds current SOC 2 Type II certification "
        "(Certificate No. CS-SOC2-2025-007, issued by PwC GmbH, valid through 2026-12-31) "
        "and ISO/IEC 27001:2022 certification (Certificate No. CS-ISO27001-2024-012, "
        "issued by TÜV Rheinland, valid through 2027-06-30). Copies of current certificates have been "
        "provided to Client's information security team and are maintained in the Vendor Registry.", body))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "5.3 <b>Penetration Testing:</b> Vendor conducts annual third-party penetration testing of "
        "all platform components. Most recent test completed February 2026 by NCC Group "
        "(Report Ref: NCCG-2026-CS-031). No critical or high-severity findings. Summary report "
        "shared with Client information security team on 2026-03-05. Next test scheduled Q1 2027.", body))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "5.4 <b>Security Breach Notification:</b> In the event of a confirmed personal data breach, "
        "Vendor shall notify Client within <b>72 hours</b> of becoming aware, in accordance with "
        "UK GDPR Article 33. Notification shall include details of the breach, categories of data "
        "affected, likely consequences, and remediation measures taken.", body))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "5.5 <b>Audit Rights:</b> Client may audit Vendor's relevant security controls with "
        "30 days' written notice, limited to once per calendar year and at Client's cost. "
        "Vendor will provide reasonable access and documentation to support such audit.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("6. INTELLECTUAL PROPERTY", h2))
    story.append(Paragraph(
        "Vendor retains all intellectual property rights in and to the platform, software, and "
        "documentation. Client retains full ownership of: (a) all Client data uploaded to or "
        "generated through the platform; (b) all outputs, reports, and exports produced; and "
        "(c) any Client-specific configurations. Source code escrow is not applicable to this "
        "Agreement as no custom software development is provided.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("7. TERMINATION", h2))
    story.append(Paragraph(
        "7.1 <b>Termination for Convenience:</b> Either party may terminate this Agreement without cause "
        "by providing <b>60 days</b> prior written notice. Client shall receive a pro-rated refund of "
        "any pre-paid fees for the unused portion of the notice period. "
        "7.2 <b>Termination for Cause:</b> Either party may terminate immediately upon written notice "
        "if the other party commits a material breach that remains uncured for 30 days after notice, "
        "or upon insolvency, liquidation, or cessation of business.", body))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("8. GOVERNING LAW &amp; DISPUTE RESOLUTION", h2))
    story.append(Paragraph(
        "This Agreement is governed by and construed in accordance with the laws of "
        "<b>England and Wales</b>. Any dispute shall first be referred to senior management of both "
        "parties for good-faith resolution (mediation, 30 days). Failing resolution, disputes shall "
        "be submitted to final and binding arbitration under the Rules of the "
        "<b>London Court of International Arbitration (LCIA)</b>, seated in London, England.", body))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("SIGNATORIES", h2))
    story.append(Paragraph(
        "For and on behalf of <b>CloudSecure GmbH</b>: "
        "Klaus Weber, Chief Executive Officer — k.weber@cloudsecure.de | Date: 2026-08-15", body))
    story.append(Paragraph(
        "For and on behalf of <b>Flat Rock Technology Ltd</b>: "
        "Sarah Thompson, Chief Procurement Officer — s.thompson@flatrocktech.com | Date: 2026-08-18", body))

    doc.build(story)
    print(f"Generated: {filepath}")
    return filepath


if __name__ == "__main__":
    print("Generating sample documents...")
    generate_pdf_msa()
    generate_image_sow()
    generate_csv_batch()
    generate_pdf_cloudsecure()
    generate_pdf_futuretech()
    generate_csv_databridge()
    generate_pdf_nexus_clean()
    print("\nAll sample documents generated in sample_docs/")
