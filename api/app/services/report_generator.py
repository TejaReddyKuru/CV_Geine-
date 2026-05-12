from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os

class MatchReportGenerator:
    @staticmethod
    def generate(analysis_data: dict, match_score: float, filename: str = "match_report.pdf") -> str:
        """Create a professional analysis report PDF."""
        filepath = os.path.join(os.getenv("UPLOADS_DIR", "./backend/uploads"), filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor("#1E293B"), alignment=1, spaceAfter=20)
        score_style = ParagraphStyle('Score', parent=styles['Normal'], fontSize=48, textColor=colors.HexColor("#2563EB"), alignment=1, spaceAfter=10)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor("#334155"), spaceBefore=15, spaceAfter=10)
        text_style = styles['Normal']
        text_style.fontSize = 11

        elements = []

        # Title
        elements.append(Paragraph("ATS MATCH ANALYSIS REPORT", title_style))
        elements.append(Spacer(1, 20))

        # Big Score
        elements.append(Paragraph(f"{match_score}%", score_style))
        elements.append(Paragraph("OVERALL MATCH SCORE", ParagraphStyle('Sub', alignment=1, fontSize=12, textColor=colors.gray)))
        elements.append(Spacer(1, 30))

        # ATS Score breakdown
        ats_score = analysis_data.get("ats_score", 0)
        elements.append(Paragraph(f"ATS Compatibility: {ats_score}/100", section_style))

        # Missing Skills
        elements.append(Paragraph("🚨 MISSING SKILLS", section_style))
        missing_skills = analysis_data.get("missing_skills", [])
        if missing_skills:
            for skill in missing_skills:
                elements.append(Paragraph(f"• {skill}", text_style))
        else:
            elements.append(Paragraph("No critical skills missing!", text_style))

        elements.append(Spacer(1, 10))

        # Suggestions
        elements.append(Paragraph("💡 RECOMMENDATIONS", section_style))
        suggestions = analysis_data.get("suggestions", [])
        for sug in suggestions:
            elements.append(Paragraph(f"• {sug}", text_style))

        elements.append(Spacer(1, 10))

        # Formatting Tips
        elements.append(Paragraph("📝 FORMATTING & ATS TIPS", section_style))
        tips = analysis_data.get("formatting_tips", [])
        for tip in tips:
            elements.append(Paragraph(f"• {tip}", text_style))

        doc.build(elements)
        return filepath
