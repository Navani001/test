1. Baseline Evaluation

Evaluated Baidu Unlimited-OCR using the Baidu community-recommended configuration: batch size 1, "ngram_size=35", "window_size=128", DPI 300, and "max_tokens=8192".

- Bag-of-words: Precision 0.97, recall 0.94, F1-score 0.96.
- CER/WER: 0.179 / 0.21.
- Numerical accuracy: Precision 0.98, recall 0.94, F1-score 0.96.
- Processing time: 4.65 seconds per page.
- Looping: Low repetitive text generation.
- Bounding boxes: Approximately 97% coverage of Textract reference boxes.

Overall, extraction quality was good, and Baidu OCR recovered some text missed by Textract. Reading-order and bounding-box segmentation differences require further investigation.
