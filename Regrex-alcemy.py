1. Baseline Evaluation – Recommended Configuration

The initial evaluation was performed using the configuration recommended by the Baidu community, with batch size 1, "ngram_size=35", "window_size=128", DPI 300, and "max_tokens=8192".

- Text extraction: The extracted text matched AWS Textract ground truth well. Baidu OCR also identified some text missed by Textract.
- Bag-of-words accuracy: Precision 0.97, recall 0.94, and F1-score 0.96.
- CER/WER: 0.179 and 0.21, respectively. Reading-order differences may contribute to these values.
- Numerical accuracy: Precision 0.98, recall 0.94, and F1-score 0.96.
- Looping: The evaluation script detected low levels of repetitive text generation.
- Processing time: Average of 4.65 seconds per page.
- Bounding-box coverage: Approximately 97% of Textract reference boxes were covered by Baidu OCR output. The remaining 3% may be due to differences in word or character segmentation.

Conclusion: The baseline demonstrated good text and numerical extraction, strong bounding-box coverage, and limited looping. Reading-order differences and segmentation mismatches remain areas for further investigation.
