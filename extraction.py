
import re
from docling.document_converter import DocumentConverter


def extract_text_from_resume(file_path:str)->str:
    """Extracts text from resume,be it a pdf or docx"""
    supported_format=(".pdf",".docx")

    if not file_path.lower().endswith(supported_format):
        raise ValueError("Unsupported file format.Please upload a PDF OR DOCX file as resume.")
    try:
        converter=DocumentConverter()
        result=converter.convert(file_path)
        text=result.document.export_to_text().strip()

    except Exception as e:
        raise RuntimeError(f"Error extrcting text with Docling:{e}")
    

    return text


def clean_text(text:str)->str:
    """Clean texts by removing punctuation,symbols,and extra whitespace """
    text=re.sub(r"\r\n|\r|\n","",text)
    text=re.sub(r"\s+","",text)
    text=text.lower().strip()

    return text




