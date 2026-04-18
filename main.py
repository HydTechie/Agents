import os
from config import *
from extractor import extract_text, extract_flows
from puml_generator import to_puml
from renderer import render_puml
from word_builder import build_doc
from utils import ensure_dirs

ensure_dirs(OUTPUT_PUML, OUTPUT_IMG, OUTPUT_DOC_DIR)

for file in os.listdir(INPUT_DIR):
    if not file.endswith(".pdf"):
        continue

    pdf_path = os.path.join(INPUT_DIR, file)
    pdf_name = file.replace(".pdf", "")

    text = extract_text(pdf_path)
    flows = extract_flows(text)

    pdf_flows = []

    for flow in flows:
        puml_text = to_puml(flow)

        puml_file = os.path.join(OUTPUT_PUML, f"{pdf_name}_{flow['name']}.puml")

        with open(puml_file, "w") as f:
            f.write(puml_text)

        render_puml(puml_file, OUTPUT_IMG)

        img_file = os.path.join(
            OUTPUT_IMG,
            f"{pdf_name}_{flow['name']}.png"
        )

        flow["image"] = img_file
        pdf_flows.append(flow)

    out_doc = os.path.join(OUTPUT_DOC_DIR, f"{pdf_name}_final.docx")
    build_doc({pdf_name: pdf_flows}, out_doc)

print("Done")
