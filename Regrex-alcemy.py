import subprocess
from pathlib import Path

SCRIPT = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "batch-inference/batch-wise.py"
)

OUTPUT_DIR = Path(
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "batch-inference/report/experiments"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

batch_sizes = [2, 3, 4]
ngram_sizes = [10, 20, 35, 50]
window_sizes = [128, 512, 1024, 2048]
image_sizes = [512, 1024]
max_tokens_list = [4096, 8192, 16384]
dpi_values = [150, 200, 300]

baseline = {
    "ngram": 35,
    "window_size": 1024,
    "image_size": 1024,
    "max_tokens": 8192,
    "dpi": 300,
}

experiments = []

for batch_size in batch_sizes:
    # N-gram size
    for value in ngram_sizes:
        e = baseline.copy()
        e.update(batch_size=batch_size, ngram=value)
        experiments.append(e)

    # Window size
    for value in window_sizes:
        e = baseline.copy()
        e.update(batch_size=batch_size, window_size=value)
        experiments.append(e)

    # Image size
    for value in image_sizes:
        e = baseline.copy()
        e.update(batch_size=batch_size, image_size=value)
        experiments.append(e)

    # Maximum output tokens
    for value in max_tokens_list:
        e = baseline.copy()
        e.update(batch_size=batch_size, max_tokens=value)
        experiments.append(e)

    # PDF rendering DPI
    for value in dpi_values:
        e = baseline.copy()
        e.update(batch_size=batch_size, dpi=value)
        experiments.append(e)

# Remove duplicate configurations
experiments = list({
    (
        e["batch_size"],
        e["ngram"],
        e["window_size"],
        e["image_size"],
        e["max_tokens"],
        e["dpi"],
    ): e
    for e in experiments
}.values())

for i, exp in enumerate(experiments, start=1):
    name = (
        f"run-{i:03d}"
        f"-batch-{exp['batch_size']}"
        f"-ngram-{exp['ngram']}"
        f"-window-{exp['window_size']}"
        f"-image-{exp['image_size']}"
        f"-tokens-{exp['max_tokens']}"
        f"-dpi-{exp['dpi']}"
    )

    output_file = OUTPUT_DIR / f"{name}.json"

    cmd = [
        "uv", "run", "python", SCRIPT,
        "--batch-size", str(exp["batch_size"]),
        "--output-path", str(output_file),
        "--dpi", str(exp["dpi"]),
        "--image-size", str(exp["image_size"]),
        "--max-token", str(exp["max_tokens"]),
        "--ngram", str(exp["ngram"]),
        "--window-size", str(exp["window_size"]),
    ]

    print(f"\nRunning {i}/{len(experiments)}: {name}")

    completed = subprocess.run(cmd, check=False)

    if completed.returncode != 0:
        print(f"FAILED: {name}")
    else:
        print(f"COMPLETED: {name}")

print(f"Finished {len(experiments)} experiments.")
