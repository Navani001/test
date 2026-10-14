import os
import json
import glob

report_folder = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "batch-inference/report"
)

output_folder = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "evaluation/Formated-inference"
)

os.makedirs(output_folder, exist_ok=True)

result = []

# Find all JSON files in the report folder
json_files = glob.glob(os.path.join(report_folder, "*.json"))

for file_path in json_files:
    file_name = os.path.basename(file_path)

    print(f"Processing: {file_name}")

    with open(file_path, "r", encoding="utf-8") as f:
        datas = json.load(f)

    for data in datas:
        pages_list = data["pages"]
        content_list = data["content"].split("<PAGE>")

        # Remove an empty first element caused by a leading <PAGE>
        if content_list and not content_list[0].strip():
            content_list = content_list[1:]

        # Check whether page count matches content sections
        if len(content_list) != len(pages_list):
            print(
                f"Page mismatch in {file_name}: "
                f"{len(pages_list)} pages, "
                f"{len(content_list)} content sections"
            )

            for page in pages_list:
                result.append({
                    "filename": data["filename"],
                    "time_seconds": (
                        data["time_seconds"] / len(pages_list)
                        if pages_list else 0
                    ),
                    "token_usage": data.get("token_usage"),
                    "content": "failed",
                    "page": page,
                    "failed": True,
                    "source_file": file_name,
                })

            continue

        for idx, page in enumerate(pages_list):
            result.append({
                "filename": data["filename"],
                "time_seconds": (
                    data["time_seconds"] / len(pages_list)
                    if pages_list else 0
                ),
                "token_usage": data.get("token_usage"),
                "content": content_list[idx],
                "page": page,
                "failed": False,
                "source_file": file_name,
            })

    # Save a separate formatted JSON file for each input file
    output_name = os.path.splitext(file_name)[0] + "-formatted.json"
    output_path = os.path.join(output_folder, output_name)

    # Save only the records generated from this input file
    file_results = [
        item for item in result
        if item["source_file"] == file_name
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(file_results, f, indent=4, ensure_ascii=False)

    print(f"Saved: {output_path}")

print(f"Processed {len(json_files)} JSON files.")
