
import os
import json
import time
import base64
import fitz
from openai import OpenAI

PDF_PATH = "your_doc.pdf"
OUTPUT_PATH = "ocr_results.json"
DPI = 200

client = OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1",
    timeout=3600,
)


def pdf_page_to_base64(page, dpi=200):
    scale = dpi / 72
    pix = page.get_pixmap(
        matrix=fitz.Matrix(scale, scale),
        alpha=False,
    )
    return base64.b64encode(pix.tobytes("png")).decode("utf-8")


def save_json(results, output_path):
    temp_path = output_path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
        file.flush()
        os.fsync(file.fileno())

    os.replace(temp_path, output_path)


def extract_pdf_ocr(pdf_path, output_path, dpi=200):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    results = []
    total_time = 0.0

    # Create an empty JSON array before starting.
    save_json(results, output_path)

    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        filename = os.path.basename(pdf_path)

        for page_index in range(total_pages):
            page_number = page_index + 1
            start = time.perf_counter()

            try:
                image_base64 = pdf_page_to_base64(
                    doc[page_index], dpi=dpi
                )

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "<image>document parsing.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": (
                                        "data:image/png;base64,"
                                        + image_base64
                                    )
                                },
                            },
                        ],
                    }
                ]

                response = client.chat.completions.create(
                    model="baidu/Unlimited-OCR",
                    messages=messages,
                    max_tokens=8192,
                    temperature=0.0,
                    extra_body={
                        "skip_special_tokens": False,
                        "vllm_xargs": {
                            "ngram_size": 35,
                            "window_size": 128,
                        },
                    },
                )

                elapsed = time.perf_counter() - start
                total_time += elapsed

                content = response.choices[0].message.content or ""
                usage = response.usage

                result = {
                    "filename": filename,
                    "page": page_number,
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
                }

                results.append(result)

                # Update the JSON file after every successful page.
                save_json(results, output_path)

                print(
                    f"Page {page_number}/{total_pages} completed | "
                    f"Time: {elapsed:.2f}s | "
                    f"Tokens: "
                    f"{result['token_usage']['total_tokens']}",
                    flush=True,
                )

                del image_base64, messages, response

            except Exception as error:
                print(
                    f"Page {page_number}/{total_pages} failed: {error}",
                    flush=True,
                )
                raise

    print(f"\nCompleted pages: {len(results)}")
    print(f"Total inference time: {total_time:.2f}s")
    if results:
        print(
            f"Average inference time: "
            f"{total_time / len(results):.2f}s"
        )
    print(f"JSON saved to: {output_path}")


if __name__ == "__main__":
    extract_pdf_ocr(
        pdf_path=PDF_PATH,
        output_path=OUTPUT_PATH,
        dpi=DPI,
    )
