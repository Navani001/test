import csv
import random
from pathlib import Path
from pypdf import PdfReader, PdfWriter

# ---------------- CONFIGURATION ----------------

INPUT_FOLDER = Path("/path/to/pdf_folder")
OUTPUT_FOLDER = Path("/path/to/output_folder")

TOTAL_PAGES = 100  # Set to 200 if needed
MIN_PDFS = 5       # Minimum number of source PDFs
RANDOM_SEED = None # Set to an integer for repeatable results

# ------------------------------------------------


def extract_random_pages():
    if TOTAL_PAGES not in (100, 200):
        raise ValueError("TOTAL_PAGES must be 100 or 200.")

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RANDOM_SEED)

    pdf_files = [
        p for p in INPUT_FOLDER.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".pdf"
        and p.parent.resolve() != OUTPUT_FOLDER.resolve()
    ]

    if not pdf_files:
        raise ValueError("No PDFs found in the input folder.")

    # Read page counts.
    pdf_info = []

    for path in pdf_files:
        try:
            reader = PdfReader(str(path), strict=False)

            if reader.is_encrypted:
                if not reader.decrypt(""):
                    continue

            count = len(reader.pages)

            if count > 0:
                pdf_info.append({
                    "path": path,
                    "pages": count
                })

        except Exception as exc:
            print(f"Skipping {path.name}: {exc}")

    # Only PDFs that can contribute at least one page.
    if len(pdf_info) < MIN_PDFS:
        raise ValueError(
            f"At least {MIN_PDFS} readable PDFs are required."
        )

    # Randomize source order.
    rng.shuffle(pdf_info)

    # Prefer using many PDFs, while allowing unequal page counts.
    max_sources = min(len(pdf_info), TOTAL_PAGES)
    source_count = rng.randint(
        min(MIN_PDFS, max_sources),
        max_sources
    )

    selected_sources = pdf_info[:source_count]

    # Give each selected PDF at least one page.
    allocations = [1] * source_count
    remaining = TOTAL_PAGES - source_count

    # Distribute remaining pages randomly, respecting PDF sizes.
    capacities = [
        info["pages"] - 1 for info in selected_sources
    ]

    while remaining > 0:
        eligible = [
            i for i, capacity in enumerate(capacities)
            if capacity > 0
        ]

        if not eligible:
            # Add more source PDFs if current ones lack enough pages.
            remaining_sources = [
                info for info in pdf_info
                if info not in selected_sources
            ]

            if not remaining_sources:
                raise ValueError(
                    "Not enough available pages for this selection."
                )

            new_source = remaining_sources[0]
            selected_sources.append(new_source)
            allocations.append(0)
            capacities.append(new_source["pages"])
            source_count += 1
            eligible = [len(capacities) - 1]

        # Randomly choose a PDF and allocate a small consecutive block.
        index = rng.choice(eligible)
        block_size = rng.randint(
            1, min(remaining, capacities[index], 20)
        )

        allocations[index] += block_size
        capacities[index] -= block_size
        remaining -= block_size

    # Extract randomly positioned continuous sections.
    writer = PdfWriter()
    manifest = []
    output_page = 1

    for info, count in zip(selected_sources, allocations):
        if count == 0:
            continue

        reader = PdfReader(str(info["path"]), strict=False)
        start = rng.randint(0, len(reader.pages) - count)

        for page_index in range(start, start + count):
            writer.add_page(reader.pages[page_index])

            manifest.append({
                "source_pdf": info["path"].name,
                "source_page": page_index + 1,
                "output_page": output_page
            })

            output_page += 1

    output_pdf = OUTPUT_FOLDER / f"random_{TOTAL_PAGES}_pages.pdf"
    manifest_csv = OUTPUT_FOLDER / "selection_manifest.csv"

    with output_pdf.open("wb") as f:
        writer.write(f)

    with manifest_csv.open(
        "w", newline="", encoding="utf-8"
    ) as f:
        csv_writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_pdf",
                "source_page",
                "output_page"
            ]
        )
        csv_writer.writeheader()
        csv_writer.writerows(manifest)

    print(f"Total pages extracted: {len(manifest)}")
    print(f"Unique source PDFs: {len(set(x['source_pdf'] for x in manifest))}")
    print(f"Output PDF: {output_pdf}")
    print(f"Manifest: {manifest_csv}")

    print("\nPages selected per PDF:")
    for info in selected_sources:
        rows = [
            x for x in manifest
            if x["source_pdf"] == info["path"].name
        ]
        if rows:
            print(
                f"{info['path'].name}: "
                f"pages {rows[0]['source_page']}-"
                f"{rows[-1]['source_page']} "
                f"({len(rows)} pages)"
            )


if __name__ == "__main__":
    extract_random_pages()
