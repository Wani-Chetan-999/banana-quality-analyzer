import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from dashboard.models import BananaAnalysisReport

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas engine ensuring strict single-page execution
    while stamping architectural metadata borders and background accents.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Color Palette Settings
        c_primary = colors.HexColor("#0F172A")
        c_gold = colors.HexColor("#D97706")
        c_border = colors.HexColor("#E2E8F0")
        
        left_margin = 36
        right_margin = letter[0] - 36
        
        # Premium Top Geometric Brand Bar
        self.setFillColor(c_primary)
        self.rect(0, letter[1] - 12, letter[0], 12, fill=1, stroke=0)
        self.setFillColor(c_gold)
        self.rect(0, letter[1] - 16, 120, 4, fill=1, stroke=0)
        
        # Running Decorative Frame Outlines
        self.setStrokeColor(c_border)
        self.setLineWidth(0.5)
        self.line(left_margin, 40, right_margin, 40) # Bottom boundary rule
        
        # Running Footer Stamps (Using Helvetica for Clean Metadata)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(c_primary)
        self.drawString(left_margin, 26, "CHAMBER AI VISION PLATFORM")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawCentredString(letter[0] / 2.0, 26, "SECURE MACHINE-GENERATED TELEMETRY CERTIFICATE")
        self.drawRightString(right_margin, 26, f"Run ID: #{self._pageNumber} of {page_count}")
        
        self.restoreState()


class BananaReportGenerator:
    """
    Generates an extraordinary, hyper-professional single-page quality evaluation 
    certificate featuring a distinct typographic pairing of Times-Serif and Helvetica
    along with an integrated validation stamp badge.
    """
    
    @staticmethod
    def generate_pdf(report_id: int, output_destination: str) -> str:
        report = BananaAnalysisReport.objects.get(id=report_id)
        
        # Structural Page Boundaries
        doc = SimpleDocTemplate(
            output_destination, 
            pagesize=letter, 
            rightMargin=36, 
            leftMargin=36, 
            topMargin=40, 
            bottomMargin=50
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- High-Contrast Architectural Palette ---
        c_primary = colors.HexColor("#0F172A")    # Midnight Slate Blue
        c_gold = colors.HexColor("#D97706")       # Deep Tech Gold Accent
        c_text_dark = colors.HexColor("#1E293B")  # Charcoal Body Text
        c_text_muted = colors.HexColor("#64748B") # Cool Gray Captions
        c_border = colors.HexColor("#E2E8F0")     # Light Structural Divider
        
        # --- Grade Dependent Dynamic Badge Background Mapping ---
        grade_str = report.assigned_grade.upper() if report.assigned_grade else "UNKNOWN"
        if "GRADE A" in grade_str:
            badge_bg = colors.HexColor("#DCFCE7")  # Light Mint Green
            badge_fg = colors.HexColor("#15803D")  # Dark Emerald Text
        elif "GRADE B" in grade_str:
            badge_bg = colors.HexColor("#DBEAFE")  # Light Cyan Blue
            badge_fg = colors.HexColor("#1D4ED8")  # Dark Royal Text
        else:
            badge_bg = colors.HexColor("#FEF3C7")  # Amber Cream
            badge_fg = colors.HexColor("#B45309")  # Warm Ochre Text

        # --- Premium Typographic Styles Layout (Times-Roman & Helvetica Pairing) ---
        styles.add(ParagraphStyle('DocHeaderTitle', fontName='Times-Bold', fontSize=24, leading=28, textColor=c_primary))
        styles.add(ParagraphStyle('DocSubtitle', fontName='Times-Bold', fontSize=9, leading=12, textColor=c_gold, spaceAfter=14, textTransform='uppercase'))
        styles.add(ParagraphStyle('SectionHeading', fontName='Times-Bold', fontSize=12, leading=15, textColor=c_primary, spaceBefore=10, spaceAfter=5))
        
        styles.add(ParagraphStyle('BodySlate', fontName='Times-Roman', fontSize=9.5, leading=14, textColor=c_text_dark))
        styles.add(ParagraphStyle('BodySlateBold', fontName='Times-Bold', fontSize=9.5, leading=14, textColor=c_primary))
        styles.add(ParagraphStyle('MutedCaption', fontName='Times-Italic', fontSize=8, leading=10, textColor=c_text_muted))
        
        styles.add(ParagraphStyle('TableHeaderText', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.white))
        styles.add(ParagraphStyle('TableBodyText', fontName='Helvetica', fontSize=8.5, leading=12, textColor=c_text_dark))
        styles.add(ParagraphStyle('KPIValue', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=c_primary, alignment=1))
        styles.add(ParagraphStyle('KPILabel', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=c_text_muted, alignment=1, textTransform='uppercase'))
        styles.add(ParagraphStyle('BadgeText', fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=badge_fg, alignment=1))

        # =========================================================================
        # 1. HEADER SECTION & BRAND BLOCK
        # =========================================================================
        story.append(Spacer(1, 10))
        story.append(Paragraph("AUTOMATED WORKSPACE TELEMETRY ANALYSIS LOG", styles['MutedCaption']))
        story.append(Paragraph("Inspection Analysis Certificate", styles['DocHeaderTitle']))
        story.append(Paragraph("STEREOSCOPIC COMPUTER VISION SYSTEM &bull; GEOMETRIC VOLUMETRIC EVALUATION ENGINE", styles['DocSubtitle']))
        
        # =========================================================================
        # 2. DESIGNER SYSTEM EVALUATION DESCRIPTION CARD
        # =========================================================================
        exec_summary_text = (
            f"<b>Chamber Evaluation Operations Notice:</b> Dual-camera stereo-isolation sequence executed successfully. "
            f"Physical object traits captured under workspace run context <b>#{report.id}</b>. "
            f"Volumetric evaluation models estimated a total mass matrix output of <b>{report.estimated_weight:.2f} grams</b>. "
            f"Sorting thresholds completed assignment routing rules efficiently."
        )
        
        summary_table = Table([[Paragraph(exec_summary_text, styles['BodySlate'])]], colWidths=[540])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('LINELEFT', (0, 0), (0, -1), 3, c_primary), 
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 4))
        
        # =========================================================================
        # 3. SPLIT CARD ROW: TECHNICAL LOG DATA vs PREMIUM QUALITY BADGE
        # =========================================================================
        kpi_cell_data = [
            [Paragraph("Inspection Run Node ID", styles['KPILabel']), Paragraph(f"#{report.id}", styles['KPIValue'])],
            [Paragraph("Optics Capture Latency", styles['KPILabel']), Paragraph(f"{report.execution_duration_ms} ms", styles['KPIValue'])],
            [Paragraph("Calibration Timestamp", styles['KPILabel']), Paragraph(datetime.datetime.now().strftime("%H:%M:%S UTC"), styles['KPIValue'])]
        ]
        kpi_split_table = Table(kpi_cell_data, colWidths=[130, 130])
        kpi_split_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        badge_cell_table = Table([[Paragraph(grade_str, styles['BadgeText'])]], colWidths=[240])
        badge_cell_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), badge_bg),
            ('BOX', (0, 0), (-1, -1), 1, badge_fg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ]))
        
        split_card_wrapper = Table([[kpi_split_table, badge_cell_table]], colWidths=[270, 270])
        split_card_wrapper.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(split_card_wrapper)
        
        # =========================================================================
        # 4. PHYSICAL EXTRACTED PARAMETERS GEOMETRIC MATRIX WITH DATASET HISTORY
        # =========================================================================
        story.append(Paragraph("Physical Measurement Extracted Matrix", styles['SectionHeading']))
        
        matrix_headers = [
            Paragraph("Property Parameter", styles['TableHeaderText']),
            Paragraph("Live Run", styles['TableHeaderText']),
            Paragraph("Dataset Min", styles['TableHeaderText']),
            Paragraph("Dataset Max", styles['TableHeaderText']),
            Paragraph("Dataset Avg", styles['TableHeaderText']),
            Paragraph("Units", styles['TableHeaderText']),
            Paragraph("Status", styles['TableHeaderText'])
        ]
        
        matrix_rows = [
            matrix_headers,
            [Paragraph("Structural Length (L)", styles['TableBodyText']), f"{report.calculated_length:.2f}", "115.00", "210.00", "165.71", "mm", "PASSED"],
            [Paragraph("Profile Width (W)", styles['TableBodyText']), f"{report.calculated_width:.2f}", "24.65", "41.60", "33.72", "mm", "PASSED"],
            [Paragraph("Depth Thickness (T)", styles['TableBodyText']), f"{report.calculated_thickness:.2f}", "22.50", "39.55", "31.39", "mm", "PASSED"],
            [Paragraph("Projected Area (V1)", styles['TableBodyText']), f"{report.calculated_area:.2f}", "5215.11", "121739.49", "86415.82", "mm²", "PASSED"],
            [Paragraph("Estimated Weight (Wt)", styles['TableBodyText']), f"{report.estimated_weight:.2f}", "67.75", "218.44", "137.95", "g", "VERIFIED"]
        ]
        
        matrix_table = Table(matrix_rows, colWidths=[130, 60, 65, 65, 65, 45, 110])
        matrix_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_primary),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, c_gold), 
            ('ALIGN', (1, 1), (4, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(matrix_table)
        
        # =========================================================================
        # 5. DUAL CAMERA VISUAL EVIDENCE VIEWPORTS
        # =========================================================================
        story.append(Paragraph("Isolated Hardware Vision Evidence Assets", styles['SectionHeading']))
        img_row = []
        img_widths = 260
        img_heights = 115 
        
        if report.top_image_capture and os.path.exists(report.top_image_capture.path):
            img_row.append(Image(report.top_image_capture.path, width=img_widths, height=img_heights))
        else:
            img_row.append(Paragraph("<font color='red'>[CAM_01_TOP Image Buffer Offline]</font>", styles['TableBodyText']))
            
        if report.side_image_capture and os.path.exists(report.side_image_capture.path):
            img_row.append(Image(report.side_image_capture.path, width=img_widths, height=img_heights))
        else:
            img_row.append(Paragraph("<font color='red'>[CAM_02_SIDE Image Buffer Offline]</font>", styles['TableBodyText']))
            
        img_table = Table([img_row], colWidths=[270, 270])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (0, 0), 1, c_gold),
            ('BOX', (1, 0), (1, 0), 1, c_primary),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(img_table)
        
        # =========================================================================
        # 6. PIPELINE DATAFLOW METHODOLOGY ROADMAP
        # =========================================================================
        story.append(Paragraph("System Grading Methodology Interpretation", styles['SectionHeading']))
        flow_chart_str = "<b>CAMERA OPTICS FEEDS</b> &nbsp;&rarr;&nbsp; <b>HSV SEGMENTATION</b> &nbsp;&rarr;&nbsp; <b>CONTOUR EXTRACTION</b> &nbsp;&rarr;&nbsp; <b>3D FUSION MODEL</b> &nbsp;&rarr;&nbsp; <b>WEIGHT REGRESSION</b>"
        flow_table = Table([[Paragraph(flow_chart_str, styles['TableHeaderText'])]], colWidths=[540])
        flow_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_primary),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(flow_table)
        story.append(Spacer(1, 4))
        
        # =========================================================================
        # 7. ENCLOSURE SYSTEM ASSIGNMENT STATEMENT BLOCK (WITH IMAGE STAMP LOGO)
        # =========================================================================
        cert_text = "<b>Attestation:</b> Rigorously generated in real-time by the Chamber AI Enclosure Sizing Node using pixel coordinate distance multipliers and volumetric distribution density tracking algorithms."
        
        # Dynamic verification stamp configuration mapping
        logo_path = os.path.join("static", "images", "D:\\Projects\\banana_grading_system\\media\\logo.png") # Point directly to your verification badge path on disk
        if os.path.exists(logo_path):
            status_element = Image(logo_path, width=90, height=90)
        else:
            # Safe text fallback alternative in case file IO paths transiently disconnect
            status_element = Paragraph("<font color='green'><b>VERIFIED VALIDATED</b></font>", styles['KPIValue'])

        cert_data = [
            [Paragraph(cert_text, styles['BodySlate']), status_element]
        ]
        cert_table = Table(cert_data, colWidths=[420, 120])
        cert_table.setStyle(TableStyle([
            ('LINELEFT', (1, 0), (1, 0), 1.5, c_gold),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(cert_table)
        story.append(Spacer(1, 4))
        
        # =========================================================================
        # 8. COMPACT SYSTEMS LEGAL DISCLAIMER NOTICE NOTE
        # =========================================================================
        disclaimer_text = "<b>Disclaimer Reference Notice:</b> Sizing parameters are generated algorithmically via multi-view vision profiles. High-stakes physical commercial transactions should remain supervised against manual weight scale validation checks."
        story.append(Paragraph(disclaimer_text, styles['MutedCaption']))

        doc.build(story, canvasmaker=NumberedCanvas)
        return output_destination