import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
MODEL = "gpt-4o-mini"

INPUT_DIR = "input_pdfs"
OUTPUT_PUML = "output/puml"
OUTPUT_IMG = "output/images"
OUTPUT_DOC_DIR = "output/docs"
