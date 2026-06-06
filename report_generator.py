"""
report_generator.py — Export summaries as CSV or PDF
Uses the csv stdlib for CSV and ReportLab for styled PDF reports.
"""

import csv
import io
import os
from datetime import datetime
from typing import List, Dict


class ReportGenerator:

    APP_TITLE = "Document Summarizer Report"

    # ────────────────────────────────────────────
    # CSV Export
    # ────────────────────────────────────────────

    def generate_csv(self, results: List[Dict]) -> str:
        """Return a UTF-8 CSV string with BOM for Excel compatibility."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Header row
        writer.writerow([
            "File Name",
            "Status",
            "Word Count",
            "Summary",
            "Google Drive File ID",
        ])

        for r in results:
            writer.writerow([
                r.get("filename", ""),
                r.get("status", "ok").upper(),
                r.get("word_count", 0),
                r.get("summary", ""),
                r.get("file_id", ""),
            ])

        return output.getvalue()

    # ────────────────────────────────────────────
    # PDF Export
    # ────────────────────────────────────────────

    def generate_pdf(self, results: List[Dict]) -> bytes:
        """Return a styled PDF as bytes using ReportLab."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer,
                Table, TableStyle, HRFlowable, PageBreak
            )
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
        except ImportError:
            raise ImportError("Run: pip install reportlab")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2 * cm,
        )

        # ── Colour palette ──────────────────────
        NAVY   = colors.HexColor("#0f172a")
        BLUE   = colors.HexColor("#3b82f6")
        SLATE  = colors.HexColor("#475569")
        LIGHT  = colors.HexColor("#f1f5f9")
        WHITE  = colors.white
        GREEN  = colors.HexColor("#16a34a")
        RED    = colors.HexColor("#dc2626")
        AMBER  = colors.HexColor("#d97706")

        STATUS_COLORS = {"ok": GREEN, "warning": AMBER, "error": RED}

        # ── Styles ──────────────────────────────
        base = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontSize=22,
            textColor=NAVY,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
        meta_style = ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontSize=9,
            textColor=SLATE,
            spaceAfter=16,
        )
        section_style = ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontSize=13,
            textColor=NAVY,
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=4,
        )
        filename_style = ParagraphStyle(
            "Filename",
            parent=base["Normal"],
            fontSize=11,
            textColor=BLUE,
            fontName="Helvetica-Bold",
        )
        body_style = ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            textColor=SLATE,
            leading=15,
            spaceAfter=6,
        )
        label_style = ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontSize=8,
            textColor=SLATE,
            fontName="Helvetica-Bold",
        )

        story = []

        # ── Cover / header ──────────────────────
        story.append(Paragraph(self.APP_TITLE, title_style))
        now = datetime.now().strftime("%B %d, %Y at %H:%M")
        story.append(Paragraph(
            f"Generated: {now}  ·  Total documents: {len(results)}", meta_style
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=12))

        # ── Summary table (overview) ────────────
        story.append(Paragraph("Overview", section_style))
        ok_count      = sum(1 for r in results if r.get("status") == "ok")
        warning_count = sum(1 for r in results if r.get("status") == "warning")
        error_count   = sum(1 for r in results if r.get("status") == "error")

        tdata = [
            ["Total Files", "Summarised", "Warnings", "Errors"],
            [str(len(results)), str(ok_count), str(warning_count), str(error_count)],
        ]
        t = Table(tdata, colWidths=[4 * cm] * 4)
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0), 9),
            ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE",     (0, 1), (-1, 1), 16),
            ("FONTNAME",     (0, 1), (-1, 1), "Helvetica-Bold"),
            ("TEXTCOLOR",    (0, 1), (-1, 1), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, 1), [LIGHT]),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("BOX",          (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ("INNERGRID",    (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROUNDEDCORNERS", [4]),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8))

        # ── Per-document summaries ───────────────
        story.append(Paragraph("Document Summaries", section_style))
        story.append(Spacer(1, 6))

        for idx, r in enumerate(results, 1):
            status = r.get("status", "ok")
            s_color = STATUS_COLORS.get(status, SLATE)

            # File number + name
            story.append(Paragraph(
                f"{idx}. {r.get('filename', 'Untitled')}", filename_style
            ))

            # Meta row: word count + status
            meta_parts = []
            if r.get("word_count"):
                meta_parts.append(f"Words: {r['word_count']:,}")
            meta_parts.append(f"Status: {status.upper()}")
            story.append(Paragraph(" · ".join(meta_parts), label_style))
            story.append(Spacer(1, 4))

            # Summary text
            summary_text = r.get("summary", "No summary available.")
            story.append(Paragraph(summary_text, body_style))

            # Separator
            story.append(Spacer(1, 8))
            if idx < len(results):
                story.append(HRFlowable(
                    width="100%", thickness=0.5,
                    color=colors.HexColor("#e2e8f0"), spaceAfter=8
                ))

        doc.build(story)
        return buffer.getvalue()
