import os
import glob
from pathlib import Path

input_dir = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "evaluation/page-wise-analysis"
)

json_files = glob.glob(os.path.join(input_dir, "*.json"))

for file_path in json_files:
    file_name = Path(file_path).stem

    print(f"Analyzing: {file_name}")

    analyze_ocr_results(
        file_path,
        file_name
    )

print(f"Completed analysis for {len(json_files)} files.")
