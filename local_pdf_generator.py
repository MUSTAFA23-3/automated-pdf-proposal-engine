import csv
import os
from datetime import datetime
import pymupdf
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Light-Mode Palette
HEX_SLATE = colors.HexColor("#0F172A")
HEX_SLATE_MUTED = colors.HexColor("#475569")
HEX_COBALT = colors.HexColor("#2563EB")
HEX_COBALT_LIGHT = colors.HexColor("#EFF6FF")
HEX_BG_LIGHT = colors.HexColor("#F8FAFC")
HEX_BORDER = colors.HexColor("#E2E8F0")
HEX_EMERALD = colors.HexColor("#059669")

def generate_proposal_pdf(row, out_pdf_path):
    doc = SimpleDocTemplate(
        out_pdf_path,
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()
    style_brand = ParagraphStyle(
        "BrandTitle", parent=styles["Heading1"],
        fontName="Helvetica-Bold", fontSize=18, textColor=HEX_SLATE, spaceAfter=2
    )
    style_sub = ParagraphStyle(
        "BrandSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9.5, textColor=HEX_SLATE_MUTED, spaceAfter=12
    )
    style_section = ParagraphStyle(
        "SectionHdr", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=11, textColor=HEX_COBALT, spaceBefore=14, spaceAfter=6
    )
    style_body = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, textColor=HEX_SLATE, leading=14
    )
    style_muted = ParagraphStyle(
        "Muted", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, textColor=HEX_SLATE_MUTED, leading=13
    )

    issue_date = datetime.now().strftime("%B %d, %Y")
    setup_fee = float(row["setup_fee_usd"])
    retainer = float(row["monthly_retainer_usd"])
    total_due = setup_fee + retainer

    story = []

    # Top Cobalt Accent Bar
    top_bar = Table([[""]], colWidths=[7.0 * inch], rowHeights=[0.08 * inch])
    top_bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), HEX_COBALT)]))
    story.append(top_bar)
    story.append(Spacer(1, 14))

    # Header Row: Brand & Reference Badge
    hdr_table = Table([
        [
            Paragraph("MMT Digital &amp; Automation Studio", style_brand),
            Paragraph(f"<b>PROPOSAL #{row['ref_id']}</b><br/><font size=8.5 color='#64748B'>Issued: {issue_date}</font>",
                      ParagraphStyle("RightHdr", parent=style_body, alignment=2))
        ],
        [
            Paragraph("Mustafa Mahmoud Tawfik &bull; Web Development &amp; Google Workspace Systems", style_sub),
            ""
        ]
    ], colWidths=[4.5 * inch, 2.5 * inch])
    hdr_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(hdr_table)
    story.append(HRFlowable(width="100%", thickness=1, color=HEX_BORDER, spaceAfter=14))

    # Client Metadata Box
    client_box = Table([
        [
            Paragraph(
                f"<font size=8 color='#64748B'><b>PREPARED FOR</b></font><br/>"
                f"<b>{row['client_name']}</b> &mdash; {row['company']}<br/>"
                f"<font size=9 color='#475569'>{row['email']}</font>",
                style_body
            ),
            Paragraph(
                f"<font size=8 color='#64748B'><b>ESTIMATED DELIVERY SLA</b></font><br/>"
                f"<b>{row['timeline_days']} Business Days</b><br/>"
                f"<font size=9 color='#059669'><b>Status: Ready for Kickoff</b></font>",
                style_body
            )
        ]
    ], colWidths=[4.3 * inch, 2.7 * inch])
    client_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HEX_BG_LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, HEX_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(client_box)

    # Scope & Deliverables
    story.append(Paragraph("PROJECT SCOPE &amp; DELIVERABLES", style_section))
    story.append(Paragraph(f"<b>Selected Package:</b> {row['service_package']}", style_body))
    story.append(Spacer(1, 6))

    for item in row["deliverables"].split(";"):
        clean = item.strip()
        if clean:
            story.append(Paragraph(f"&bull;  {clean}", style_muted))

    story.append(Spacer(1, 16))

    # Investment Summary Table
    story.append(Paragraph("INVESTMENT &amp; PAYMENT SCHEDULE", style_section))
    inv_rows = [
        ["Line Item Description", "Billing Type", "Amount (USD)"],
        [row["service_package"], "One-Time Implementation", f"${setup_fee:,.2f}"],
    ]
    if retainer > 0:
        inv_rows.append(["Managed Monitoring, Triggers & SLA Support", "Monthly Retainer", f"${retainer:,.2f}/mo"])
    inv_rows.append(["Total Initial Investment Due at Kickoff", "", f"${total_due:,.2f}"])

    inv_table = Table(inv_rows, colWidths=[3.8 * inch, 1.8 * inch, 1.4 * inch])
    inv_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEX_SLATE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.5, HEX_BORDER),
        ("BACKGROUND", (0, -1), (-1, -1), HEX_COBALT_LIGHT),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (2, -1), (2, -1), HEX_COBALT),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(inv_table)
    story.append(Spacer(1, 22))

    # Terms Footer
    story.append(HRFlowable(width="100%", thickness=1, color=HEX_BORDER, spaceAfter=10))
    story.append(Paragraph(
        "<b>Terms &amp; Acceptance:</b> All code, spreadsheets, and automation assets become 100% client-owned upon final milestone completion. "
        "This demonstration proposal was generated programmatically via <i>local_pdf_generator.py</i>.",
        style_muted
    ))

    doc.build(story)

def render_preview_png(pdf_path, png_path):
    doc = pymupdf.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # 2x crisp DPI
    pix.save(png_path)
    doc.close()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "sample_clients.csv")
    out_dir = os.path.join(base_dir, "output_proposals")
    screenshot_dir = os.path.join(base_dir, "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)

    generated_pdfs = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_company = row["company"].replace(" ", "_")
            pdf_name = f"{row['ref_id']}_{safe_company}.pdf"
            pdf_path = os.path.join(out_dir, pdf_name)
            generate_proposal_pdf(row, pdf_path)
            generated_pdfs.append(pdf_path)
            print(f"Generated PDF: {pdf_path}")

    if generated_pdfs:
        preview_png = os.path.join(screenshot_dir, "proposal_preview.png")
        render_preview_png(generated_pdfs[0], preview_png)
        print(f"Rendered preview PNG: {preview_png}")

if __name__ == "__main__":
    main()
