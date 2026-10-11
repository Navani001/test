
import os
import json
import time
import base64
import fitz
from openai import OpenAI

PDF_PATH = "your_doc.pdf"
OUTPUT_PATH = "ocr_results.json"
DPI = 300
BATCH_SIZE = 3

client = OpenAI(
    api_key="EMPTY",
    base_url="http://127.0.0.1:10000/v1",
    timeout=1200,
)


def pdf_pages_to_images(pdf_path, start_page, end_page, dpi=300):
    images = []

    with fitz.open(pdf_path) as doc:
        matrix = fitz.Matrix(dpi / 72, dpi / 72)

        for i in range(start_page, end_page):
            pix = doc[i].get_pixmap(matrix=matrix)
            image_bytes = pix.tobytes("png")
            image_base64 = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            images.append({
                "page": i + 1,
                "image_base64": image_base64,
            })

    return images


def build_content(prompt, images):
    content = [{"type": "text", "text": prompt}]

    for image in images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": (
                    "data:image/png;base64,"
                    + image["image_base64"]
                )
            },
        })

    return content


def generate(prompt, images, image_mode, ngram_window):
    messages = [
        {
            "role": "user",
            "content": build_content(prompt, images),
        }
    ]

    start = time.perf_counter()

    response = client.chat.completions.create(
        model="Unlimited-OCR",
        messages=messages,
        temperature=0,
        stream=False,
        extra_body={
            "skip_special_tokens": False,
            "images_config": {
                "image_mode": image_mode,
            },
            "custom_logit_processor": (
                "DeepseekOCRNoRepeatNGramLogitProcessor"
            ),
            "custom_params": {
                "ngram_size": 35,
                "window_size": ngram_window,
            },
        },
        max_tokens=8192,
    )

    elapsed = time.perf_counter() - start

    content = response.choices[0].message.content or ""
    usage = response.usage

    return content, usage, elapsed


def save_json(results, output_path):
    temp_path = output_path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.flush()
        os.fsync(file.fileno())

    os.replace(temp_path, output_path)


def extract_pdf_ocr(
    pdf_path,
    output_path,
    dpi=300,
    batch_size=3,
):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    os.makedirs(
        os.path.dirname(os.path.abspath(output_path)),
        exist_ok=True,
    )

    results = []
    total_inference_time = 0.0
    filename = os.path.basename(pdf_path)

    save_json(results, output_path)

    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)

    for batch_start in range(0, total_pages, batch_size):
        batch_end = min(batch_start + batch_size, total_pages)
        batch_number = batch_start // batch_size + 1

        images = pdf_pages_to_images(
            pdf_path,
            batch_start,
            batch_end,
            dpi,
        )

        try:
            page_numbers = [image["page"] for image in images]

            print(
                f"Processing batch {batch_number}: "
                f"pages {page_numbers[0]}-{page_numbers[-1]}",
                flush=True,
            )

            content, usage, elapsed = generate(
                prompt="Multi page parsing.",
                images=images,
                image_mode="base",
                ngram_window=1024,
            )

            total_inference_time += elapsed

            results.append({
                "filename": filename,
                "pages": page_numbers,
                "content": content,
                "token_usage": {
                    "prompt_tokens": (
                        usage.prompt_tokens if usage else None
                    ),
                    "completion_tokens": (
                        usage.completion_tokens if usage else None
                    ),
                    "total_tokens": (
                        usage.total_tokens if usage else None
                    ),
                },
                "time_seconds": round(elapsed, 3),
            })

            save_json(results, output_path)

            print(
                f"Batch {batch_number} completed | "
                f"Time: {elapsed:.2f}s | "
                f"Tokens: "
                f"{results[-1]['token_usage']['total_tokens']}",
                flush=True,
            )

        finally:
            del images

    print(f"\nTotal pages: {total_pages}")
    print(f"Total batches: {len(results)}")
    print(f"Total inference time: {total_inference_time:.2f}s")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    extract_pdf_ocr(
        pdf_path=PDF_PATH,
        output_path=OUTPUT_PATH,
        dpi=DPI,
        batch_size=BATCH_SIZE,
    )
