import re
from pypdf import PdfReader

def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return re.sub(r"\s+", " ", text).strip()
