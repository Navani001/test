import os
import json
import glob
from pathlib import Path

input_dir = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "evaluation/Formated-inference"
)

output_dir = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "evaluation/page-wise-analysis"
)

os.makedirs(output_dir, exist_ok=True)

json_files = glob.glob(os.path.join(input_dir, "*.json"))

for file_path in json_files:
    file_name = os.path.basename(file_path)
    output_file_name = Path(file_name).stem

    print(f"\nProcessing: {file_name}")

    with open(file_path, "r", encoding="utf-8") as f:
        datas = json.load(f)

    output_path = os.path.join(
        output_dir,
        f"{output_file_name}.json",
    )

    for data in datas:
        total = 0
        failures = 0

        total += 1

        print("Page:", data["page"])

        if data.get("failed") is True:
            failures += 1

            result = {
                "filename": data["filename"],
                "page": data["page"],
                "time_seconds": data["time_seconds"],
                "status": "failed",
            }

            append_json_object(output_path, result)
            continue

        page_number = data["page"] + 1

        result = evaluate_page(
            format_textract(
                extract_textract_data_df(page_number)
            ),
            baidu_formator(data),
            generate_textrack_text(
                format_textract(
                    extract_textract_data_df(page_number)
                )
            ),
            generate_ocr_text(
                baidu_formator(data)
            ),
        )

        result["filename"] = data["filename"]
        result["page"] = data["page"]
        result["time_seconds"] = data["time_seconds"]
        result["token_usage"] = data.get("token_usage")
        result["status"] = "success"

        append_json_object(output_path, result)

    print(f"Saved results to: {output_path}")

print(f"\nProcessed {len(json_files)} JSON files.")
