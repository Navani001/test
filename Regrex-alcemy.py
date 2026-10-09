
import os
import re
import shutil
import pandas as pd
from pypdf import PdfReader, PdfWriter

# Configuration
CSV_PATH = "input.csv"
OUTPUT_DIR = "test_dataset"
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "test_dataset.csv")

MAX_PAGES = 100
TARGET_PER_TYPE = 50


def safe_folder_name(name):
    return re.sub(r'[<>:"/\\|?*]', "_", str(name)).strip(". ") or "unknown"


def unique_path(directory, filename):
    path = os.path.join(directory, filename)

    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(filename)
    part = 1

    while True:
        path = os.path.join(directory, f"{base}_part{part}{ext}")
        if not os.path.exists(path):
            return path
        part += 1


def write_pages(reader, output_path, start_page, page_count):
    writer = PdfWriter()

    for page_index in range(start_page, start_page + page_count):
        writer.add_page(reader.pages[page_index])

    with open(output_path, "wb") as output_file:
        writer.write(output_file)


def create_test_dataset():
    df = pd.read_csv(CSV_PATH)

    required = {"pdf_path", "template", "difficulty"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing CSV columns: {missing}")

    os.makedirs(PDF_DIR, exist_ok=True)

    templates = {}
    selected_source_rows = set()

    for row_index, row in df.iterrows():
        pdf_path = str(row["pdf_path"]).strip()
        template = str(row["template"]).strip()
        difficulty = str(row["difficulty"]).strip().lower()

        if not pdf_path or pdf_path.lower() == "nan":
            continue
        if not template or template.lower() == "nan":
            continue
        if difficulty not in ("easy", "hard"):
            print(f"Skipping unknown difficulty: {pdf_path}")
            continue
        if not os.path.isfile(pdf_path):
            print(f"PDF not found: {pdf_path}")
            continue

        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
        except Exception as error:
            print(f"Cannot read PDF {pdf_path}: {error}")
            continue

        if page_count == 0:
            continue

        templates.setdefault(template, {"easy": [], "hard": []})
        templates[template][difficulty].append({
            "path": pdf_path,
            "pages": page_count,
            "row_index": row_index,
        })

    output_rows = []
    summary = []

    for template, categories in templates.items():
        easy_total = sum(x["pages"] for x in categories["easy"])
        hard_total = sum(x["pages"] for x in categories["hard"])

        easy_target = min(TARGET_PER_TYPE, easy_total)
        hard_target = min(TARGET_PER_TYPE, hard_total)

        # Fill shortages using the other difficulty.
        if easy_target < TARGET_PER_TYPE:
            hard_target += min(
                TARGET_PER_TYPE - easy_target,
                hard_total - hard_target,
            )

        if hard_target < TARGET_PER_TYPE:
            easy_target += min(
                TARGET_PER_TYPE - hard_target,
                easy_total - easy_target,
            )

        targets = {
            "easy": easy_target,
            "hard": hard_target,
        }

        template_dir = os.path.join(PDF_DIR, safe_folder_name(template))
        os.makedirs(template_dir, exist_ok=True)

        selected_counts = {"easy": 0, "hard": 0}

        for difficulty in ("easy", "hard"):
            remaining = targets[difficulty]

            for index, source in enumerate(categories[difficulty]):
                if remaining <= 0:
                    break

                take = min(source["pages"], remaining)
                source_path = source["path"]
                original_name = os.path.basename(source_path)

                if take == source["pages"]:
                    # Copy the full PDF with its original filename.
                    destination = unique_path(template_dir, original_name)
                    shutil.copy2(source_path, destination)
                    operation = "copied"
                else:
                    # Create a split PDF; original file remains untouched.
                    base, ext = os.path.splitext(original_name)
                    split_name = f"{base}_part{index + 1}{ext}"
                    destination = unique_path(template_dir, split_name)

                    reader = PdfReader(source_path)
                    write_pages(reader, destination, 0, take)
                    operation = "split"

                selected_source_rows.add(source["row_index"])

                output_rows.append({
                    "template": template,
                    "pdf_path": os.path.abspath(destination),
                    "difficulty": difficulty,
                    "selected": True,
                    "operation": operation,
                    "pages_selected": take,
                })

                selected_counts[difficulty] += take
                remaining -= take

        summary.append({
            "template": template,
            "easy_pages": selected_counts["easy"],
            "hard_pages": selected_counts["hard"],
            "total_pages": sum(selected_counts.values()),
        })

    result_df = pd.DataFrame(
        output_rows,
        columns=[
            "template",
            "pdf_path",
            "difficulty",
            "selected",
            "operation",
            "pages_selected",
        ],
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    result_df.to_csv(OUTPUT_CSV, index=False)

    print("\nSelection summary:")
    if summary:
        print(pd.DataFrame(summary).to_string(index=False))

    print(f"\nOutput CSV: {OUTPUT_CSV}")
    print(f"Selected PDFs folder: {PDF_DIR}")

    return result_df


if __name__ == "__main__":
    result_df = create_test_dataset()
    print("\nResult DataFrame:")
    print(result_df)
