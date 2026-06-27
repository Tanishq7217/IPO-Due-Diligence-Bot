from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import io
from datetime import datetime


def generate_pdf_report(analysis):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Custom styles ──────────────────────────────────────
    title_style = ParagraphStyle('Title',
        parent=styles['Normal'],
        fontSize=20,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0C447C'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle('Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#5F5E5A'),
        spaceAfter=2
    )
    h2_style = ParagraphStyle('H2',
        parent=styles['Normal'],
        fontSize=13,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2C2C2A'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle('Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#3d3d3a'),
        leading=15,
        spaceAfter=4
    )
    small_style = ParagraphStyle('Small',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#5F5E5A'),
        leading=13
    )

    # ── Shortcut variables ─────────────────────────────────
    company = analysis.get("company", {})
    score = analysis.get("dd_score", {})
    fin = analysis.get("financials", {})

    # ── Header ─────────────────────────────────────────────
    story.append(Paragraph("IPO Due Diligence Report", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0C447C')))
    story.append(Spacer(1, 10))
    story.append(Paragraph(company.get("name", "Company"), title_style))
    story.append(Paragraph(
        f"{company.get('industry', '—')}  |  IPO Size: Rs {company.get('ipo_size_cr', 0):,} Cr  |  Price Band: {company.get('price_band', '—')}",
        subtitle_style
    ))
    story.append(Paragraph(
        f"Report generated: {datetime.now().strftime('%d %B %Y')}  |  Confidential",
        small_style
    ))
    story.append(Spacer(1, 16))

    # ── DD Score Table ─────────────────────────────────────
    score_data = [
        ['DD Score', 'Financials', 'Governance', 'Business Quality', 'Risk Level', 'Verdict'],
        [
            f"{score.get('overall', 0)}/100",
            f"{score.get('financials', 0)}/100",
            f"{score.get('governance', 0)}/100",
            f"{score.get('business_quality', 0)}/100",
            score.get('risk_level', '—').upper(),
            score.get('investment_verdict', '—')
        ]
    ]
    score_table = Table(score_data, colWidths=[2.5*cm] * 6)
    score_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), colors.HexColor('#0C447C')),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.white),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND',  (0, 1), (-1, 1), colors.HexColor('#E6F1FB')),
        ('FONTNAME',    (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (0, 1), (-1, 1), colors.HexColor('#0C447C')),
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.HexColor('#B5D4F4')),
        ('PADDING',     (0, 0), (-1, -1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # ── Analyst Summary ────────────────────────────────────
    story.append(Paragraph("Executive Summary", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D3D1C7')))
    story.append(Spacer(1, 6))
    story.append(Paragraph(analysis.get("analyst_summary", "—"), body_style))
    story.append(Spacer(1, 10))

    # ── Financials ─────────────────────────────────────────
    story.append(Paragraph("Financial Highlights", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D3D1C7')))
    story.append(Spacer(1, 6))

    revenue = fin.get("revenue", [])
    pat = fin.get("pat", [])

    if revenue and pat:
        years = [r["year"] for r in revenue]
        fin_data = [
            ["Metric"] + years,
            ["Revenue (Rs Cr)"] + [f"{r.get('value_cr', 0):,.0f}" for r in revenue],
            ["PAT (Rs Cr)"]     + [f"{p.get('value_cr', 0):,.0f}" for p in pat],
        ]
        fin_table = Table(fin_data, colWidths=[4*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1EFE8')),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, -1), 9),
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#D3D1C7')),
            ('ALIGN',      (1, 0), (-1, -1), 'RIGHT'),
            ('PADDING',    (0, 0), (-1, -1), 6),
        ]))
        story.append(fin_table)
        story.append(Spacer(1, 6))

    story.append(Paragraph(f"EBITDA Margin: {fin.get('ebitda_margin_pct', 0):.1f}%", body_style))
    story.append(Paragraph(f"Debt/Equity Ratio: {fin.get('debt_equity_ratio', 0):.2f}x", body_style))
    story.append(Paragraph(f"ROCE: {fin.get('roce_pct', 0):.1f}%", body_style))

    # ── Red Flags ──────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("Red Flags", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D3D1C7')))
    story.append(Spacer(1, 6))
    for flag in analysis.get("red_flags", []):
        story.append(Paragraph(
            f"<b>{flag.get('type', '—')}</b>: {flag.get('description', '—')}",
            body_style
        ))

    # ── Risk Factors ───────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("Risk Factors", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D3D1C7')))
    story.append(Spacer(1, 6))
    for risk in analysis.get("risk_factors", []):
        story.append(Paragraph(
            f"[{risk.get('severity', '—').upper()}] {risk.get('category', '—').title()}: {risk.get('description', '—')}",
            body_style
        ))

    # ── FPI Notes ──────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("Cross-Border Investor Notes", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D3D1C7')))
    story.append(Spacer(1, 6))
    for note in analysis.get("fpi_notes", []):
        story.append(Paragraph(
            f"[{note.get('type', '—').upper()}] {note.get('text', '—')}",
            body_style
        ))

    # ── Footer ─────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D3D1C7')))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "AI-generated report. For informational purposes only. Not investment advice.",
        small_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()