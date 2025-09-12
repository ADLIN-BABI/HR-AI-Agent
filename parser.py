import re
import os
import logging
from typing import Dict, Any
from pdfminer.high_level import extract_text
import docx

# Optional spaCy for entity extraction
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None
    logging.info("spaCy not available. Skipping entity extraction.")

EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+', re.I)
PHONE_RE = re.compile(r'(\+?\d[\d\-\s]{6,}\d)')

def extract_text_from_pdf(path: str) -> str:
    try:
        return extract_text(path)
    except Exception:
        logging.exception(f"PDF read error: {path}")
        return ""

def extract_text_from_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        logging.exception(f"DOCX read error: {path}")
        return ""

def load_resume_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(path)
    else:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            logging.exception(f"Text read error: {path}")
            return ""

def parse_basic_info(text: str, filename: str) -> Dict[str, Any]:
    emails = list(set(EMAIL_RE.findall(text)))
    phones = list(set(PHONE_RE.findall(text)))

    candidate_name = os.path.splitext(filename)[0]
    primary_email = emails[0] if emails else None
    primary_phone = phones[0] if phones else None

    ents = []
    if nlp:
        doc = nlp(text[:5000])
        ents = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ("ORG", "DATE", "PERSON")]
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                candidate_name = ent.text
                break

    return {
        "name": candidate_name,
        "email": primary_email,
        "phone": primary_phone,
        "emails": emails,
        "phones": phones,
        "entities": ents,
        "raw_text": text,
    }

def parse_resume_file(path: str) -> Dict[str, Any]:
    text = load_resume_file(path)
    info = parse_basic_info(text, os.path.basename(path))
    return {**info, "filename": os.path.basename(path), "score": 0.0}
