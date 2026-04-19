# One-time fixed runtime config (no .env lookup).
# If needed later, edit these values directly here.
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.2:latest"
# Seconds to wait for one /api/chat response.
OLLAMA_TIMEOUT = 300
# Max characters of PDF text sent per request.
OLLAMA_MAX_INPUT_CHARS = 8000

INPUT_DIR = "input_pdfs"
OUTPUT_PUML = "output/puml"
OUTPUT_IMG = "output/images"
OUTPUT_DOC_DIR = "output/docs"
