from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable, Table, TableStyle
import io
import os

class resumePDFGenerator:
    @staticmethod
    def generate(resume_data: dict, filename: str = "improved_resume.pdf") -> str:
        """Create a professional resume PDF from structured JSON data."""
        filepath = os.path.join(os.getenv("UPLOADS_DIR", "./backend/uploads"), filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        # Define Custom Styles for better aesthetics
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor("#2C3E50"),
            alignment=1, # Center
            spaceAfter=12
        )
        
        section_heading_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=6,
            spaceBefore=12,
            borderPadding=2,
            borderWidth=0,
            borderStyle=None,
            borderColor=colors.HexColor("#E5E7EB"),
            backColor=colors.HexColor("#f8f9fa")
        )

        body_style = styles['Normal']
        body_style.fontSize = 10
        body_style.leading = 14
        body_style.textColor = colors.HexColor("#334155")

        elements = []

        # Header (Assuming identity info from resume_data or placeholders if not provided)
        # For simplicity, we assume we have placeholders for identity if not in rewrite_data
        # Note: In a production app, you'd merge the original identity into this data.
        name = resume_data.get("name", "Candidate Name")
        elements.append(Paragraph(name, title_style))
        elements.append(Spacer(1, 12))

        # Summary
        if "summary" in resume_data:
            elements.append(Paragraph("PROFESSIONAL SUMMARY", section_heading_style))
            elements.append(Paragraph(resume_data["summary"], body_style))

        # Skills
        if "skills" in resume_data:
            elements.append(Paragraph("TECHNICAL SKILLS", section_heading_style))
            skills_text = ", ".join(resume_data["skills"])
            elements.append(Paragraph(skills_text, body_style))

        # Experience
        if "experience" in resume_data:
            elements.append(Paragraph("WORK EXPERIENCE", section_heading_style))
            for exp in resume_data["experience"]:
                # Job Header (Bold Role, Italic Company)
                role_line = f"<b>{exp.get('role', 'N/A')}</b> | <i>{exp.get('company', 'N/A')}</i>"
                elements.append(Paragraph(role_line, body_style))
                
                # Bullets
                bullet_items = [ListItem(Paragraph(b, body_style), leftIndent=20) for b in exp.get('bullets', [])]
                elements.append(ListFlowable(bullet_items, bulletType='bullet'))
                elements.append(Spacer(1, 6))

        # Projects
        if "projects" in resume_data:
            elements.append(Paragraph("PROJECTS", section_heading_style))
            for proj in resume_data["projects"]:
                proj_line = f"<b>{proj.get('name', 'Project')}</b>"
                elements.append(Paragraph(proj_line, body_style))
                if "description" in proj:
                    elements.append(Paragraph(f"<i>{proj['description']}</i>", body_style))
                
                bullet_items = [ListItem(Paragraph(b, body_style), leftIndent=20) for b in proj.get('bullets', [])]
                elements.append(ListFlowable(bullet_items, bulletType='bullet'))
                elements.append(Spacer(1, 6))

        doc.build(elements)
        return filepath
