import os
import json
import torch
import tempfile
import fitz

from transformers import AutoModel, AutoTokenizer


model_name = "/models/Unlimited-OCR"

tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    trust_remote_code=True
)

model = AutoModel.from_pretrained(
    model_name,
    trust_remote_code=True,
    use_safetensors=True,
    torch_dtype=torch.bfloat16,
)

model = model.eval().cuda()


def pdf_to_images(pdf_path, dpi=300):
    doc = fitz.open(pdf_path)

    tmp_dir = tempfile.mkdtemp(prefix="pdf_ocr_")

    paths = []

    mat = fitz.Matrix(dpi / 72, dpi / 72)

    for i, page in enumerate(doc):
        out = os.path.join(
            tmp_dir,
            f"page_{i + 1:04d}.png"
        )

        page.get_pixmap(matrix=mat).save(out)

        paths.append(out)

    doc.close()

    return paths


def process_pdfs(pdf_paths, output_file, batch_size=2):

    all_results = []

    for pdf_path in pdf_paths:

        if not os.path.isfile(pdf_path):
            print(f"Skipping missing PDF: {pdf_path}")
            continue

        print(f"\nProcessing: {pdf_path}")

        image_files = pdf_to_images(pdf_path)

        total_pages = len(image_files)

        for start in range(0, total_pages, batch_size):

            end = min(
                start + batch_size,
                total_pages
            )

            batch_images = image_files[start:end]

            print(
                f"Processing pages "
                f"{start + 1}-{end}"
            )

            result = model.infer_multi(
                tokenizer,
                prompt="<image>Multi page parsing.",
                image_files=batch_images,
                output_path=os.path.dirname(output_file),
                image_size=1024,
                max_length=32768,
                no_repeat_ngram_size=35,
                ngram_window=1024,
                save_results=True,
            )

            for item in result:

                all_results.append({
                    "content": item.get("content"),
                    "time": item.get("time"),
                    "page": item.get("page"),
                    "path": item.get("path"),
                    "output_tokens": item.get("output_tokens")
                })

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_results,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"\nAll results saved to: {output_file}")


pdf_paths = [
    "/home/nlpdevintern1/ocrResearch/sample-test-pdf/sample1.pdf",
    "/home/nlpdevintern1/ocrResearch/sample-test-pdf/sample2.pdf",
    "/home/nlpdevintern1/ocrResearch/sample-test-pdf/sample3.pdf",
    "/home/nlpdevintern1/ocrResearch/sample-test-pdf/sample4.pdf",
    "/home/nlpdevintern1/ocrResearch/sample-test-pdf/sample5.pdf",
]

batch_size = 2

output_file = (
    "/home/nlpdevintern1/ocrResearch/"
    "baidu-hugging-face/all_results.json"
)

process_pdfs(
    pdf_paths,
    output_file,
    batch_size
)
