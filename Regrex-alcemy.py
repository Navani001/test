import json
from pathlib import Path

# Input and output directories
formatted_inference_path = Path(
    "/home/nlpdevintern1/ocrResearch/baidu/baidu_data/formatted-data/batch1/run2/"
)

page_analysis_path = Path(
    "/home/nlpdevintern1/ocrResearch/baidu/baidu_data/page-wise/batch1/run2/"
)

summary_path = Path(
    "/home/nlpdevintern1/ocrResearch/baidu/baidu_data/summary/batch1/run2/"
)

# Create output directories if they don't exist
page_analysis_path.mkdir(parents=True, exist_ok=True)
summary_path.mkdir(parents=True, exist_ok=True)

# Process all JSON files in the input folder
for input_file in formatted_inference_path.glob("*.json"):

    print(f"Processing: {input_file.name}")

    try:
        with input_file.open("r", encoding="utf-8") as f:
            datas = json.load(f)

        # Evaluate pages
        page_evaluate_result = evaluate_pages(datas)

        # Generate document summary
        summary_result = generate_summary(page_evaluate_result)

        # Save page-wise evaluation
        page_output_file = page_analysis_path / input_file.name
        with page_output_file.open("w", encoding="utf-8") as fw:
            json.dump(page_evaluate_result, fw, indent=4, ensure_ascii=False)

        # Save summary
        summary_output_file = summary_path / input_file.name
        with summary_output_file.open("w", encoding="utf-8") as fw:
            json.dump(summary_result, fw, indent=4, ensure_ascii=False)

        print(f"Completed: {input_file.name}")
        print(f"Summary: {summary_result}")

    except Exception as e:
        print(f"Failed to process {input_file.name}: {e}")

print("All files processed.")
