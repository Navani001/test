
import random
import boto3
from pathlib import Path
from botocore.exceptions import ClientError

# Configuration
BUCKET_NAME = "your-bucket-name"
S3_PREFIX = ""  # Example: "reports/"
DOWNLOAD_DIR = Path("random_pdfs")
SAMPLE_SIZE = 100

# AWS credentials are loaded from your AWS profile,
# environment variables, or IAM role.
s3 = boto3.client("s3")


def download_random_pdfs():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Get all PDF keys from S3, including nested folders
    pdf_keys = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(
        Bucket=BUCKET_NAME,
        Prefix=S3_PREFIX
    ):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if key.lower().endswith(".pdf"):
                pdf_keys.append(key)

    print(f"Total PDFs found: {len(pdf_keys)}")

    if len(pdf_keys) < SAMPLE_SIZE:
        raise ValueError(
            f"Only {len(pdf_keys)} PDFs found; "
            f"{SAMPLE_SIZE} required."
        )

    # Randomly select 100 unique PDFs
    selected_keys = random.sample(pdf_keys, SAMPLE_SIZE)

    # Download selected PDFs
    for index, key in enumerate(selected_keys, start=1):
        filename = Path(key).name
        local_path = DOWNLOAD_DIR / f"{index:03d}_{filename}"

        try:
            s3.download_file(BUCKET_NAME, key, str(local_path))
            print(f"[{index}/{SAMPLE_SIZE}] Downloaded: {key}")

        except ClientError as error:
            print(f"Failed to download {key}: {error}")

    print(f"\nDownloads saved to: {DOWNLOAD_DIR.resolve()}")


if __name__ == "__main__":
    download_random_pdfs()
