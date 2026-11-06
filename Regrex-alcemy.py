### 5.2 Single-Core and Multi-Core Processing Comparison

Inference performance was evaluated under single-core and multi-core processing configurations using the 100-page dataset to understand the impact of CPU parallelization on Indra OCR processing time.

The same Indra OCR configuration was maintained across all experiments to ensure a consistent comparison.

The following parameters were recorded:

* Total inference time: Time taken to process all 100 pages.

* Average inference time: Average time taken to process a single page, calculated by dividing the total inference time by the number of pages processed.

Evaluation Results:

| Dataset          | CPU cores used  | Total inference time (seconds) | Average inference time (ms/page) |
| ---------------- | --------------- | ------------------------------ | -------------------------------- |
| 100-page dataset | 1 (Single-core) |                                |                                  |
| 100-page dataset | 2               |                                |                                  |
| 100-page dataset | 4               |                                |                                  |

Observations:

* The text extraction accuracy results were almost identical across all core configurations.

* No significant changes were observed in the evaluation metrics when processing documents using single-core and multi-core configurations.

* The primary difference between the configurations was observed in inference performance.

* Total and average inference times were compared to understand the impact of increasing the number of CPU cores on processing performance.

The results help assess whether multi-core processing provides a performance improvement over single-core inference without affecting text extraction accuracy.
