import pdfplumber
import docx
import io
import os

class TextExtractor:
    @staticmethod
    def from_pdf(file_content: bytes) -> str:
        """Extract text from PDF using pdfplumber."""
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text.strip()

    @staticmethod
    def from_docx(file_content: bytes) -> str:
        """Extract text from DOCX using python-docx."""
        doc = docx.Document(io.BytesIO(file_content))
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    @staticmethod
    def extract(file_content: bytes, filename: str) -> str:
        """General extraction method based on file extension."""
        ext = filename.lower().split(".")[-1]
        try:
            if ext == "pdf":
                return TextExtractor.from_pdf(file_content)
            elif ext == "docx":
                return TextExtractor.from_docx(file_content)
            elif ext in ["txt", "md"]:
                return file_content.decode("utf-8")
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
             raise Exception(f"Failed to extract text from {filename}: {str(e)}")
