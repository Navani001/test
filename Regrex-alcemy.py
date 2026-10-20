Summary and Recommendations

Based on the evaluation, batch size 1 is recommended for stable and reliable OCR extraction. Batch sizes 3 and 4 did not improve processing time, while batch size 2 introduced significant page-separation failures.

- N-gram size: Use "ngram_size=35" as the preferred configuration. Values 10 and 20 may cause content omission, while 50 provides similar performance to 35.
- Window size: Use "window_size=128", as larger values showed no meaningful overall improvement.
- Maximum tokens: Use "max_tokens=8192", which was sufficient for the tested documents.
- DPI: Choose 300 for slightly better extraction accuracy and bounding-box coverage, or 200 when faster processing is the priority.

Overall, the recommended configuration is "batch_size=1", "ngram_size=35", "window_size=128", "max_tokens=8192", and "DPI=300". This provides a strong balance of extraction accuracy, structural reliability, and processing performance based on the current evaluation.
