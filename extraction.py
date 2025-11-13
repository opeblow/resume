import os
import re
import string
import PyPDF2
from docx import Document


def extract_text_from_resume(file_path:str)->str:
    """Extracts text from resume,either a pdf or docx"""
    if file_path.lower().endswith('.pdf'):
        try:
            with open(file_path,'rb')as file:
                pdf_reader=PyPDF2.PdfReader(file)
                text=""
                for page in pdf_reader.pages:
                    text+=page.extract_text()
                return text.strip()
        except Exception as e:
            raise RuntimeError(f"Error extracting PDF:{e}")
        
    elif file_path.lower().endswith('.docx'):
        try:
            doc=Document(file_path)
            text="\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        
        except Exception as e:
            raise RuntimeError(f"Error extracting DOCX :{e}")
        
    else:
        raise ValueError("Unsupported file format.Pleasr upload a PDF or DOCX file")



def clean_text(text:str)->str:
    """Clean texts by removing punctuation,symbols,and extra whitespace """
    text=text.translate(str.maketrans("","",string.punctuation))
    text=re.sub(r"[^a-zA-Z0-9\s]"," ",text)
    text=re.sub(r"\s+"," ",text)
    text=text.lower().strip()
 
    return text




