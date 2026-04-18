import pdfplumber
from openai import OpenAI
from config import MODEL, OPENAI_API_KEY
from prompts import PROMPT
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_flows(text):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text}
        ]
    )
    return json.loads(response.choices[0].message.content)
