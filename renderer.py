import subprocess
import os

def render_puml(puml_path, output_dir):
    subprocess.run([
        "plantuml",
        "-tpng",
        puml_path,
        "-o",
        os.path.abspath(output_dir)
    ])
