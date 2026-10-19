1. Evaluated Baidu Unlimited-OCR inference using a sample PDF with the recommended parameters and batch size 1.
2. Tested different prompt templates to evaluate their impact on extraction quality and page separation.
3. Evaluated the "ngram_size" parameter with values 10, 20, 35, and 50 for batch size 1.
4. Evaluated DPI settings of 200 and 300 to analyze their impact on extraction quality.
5. Evaluated the "ngram_size" and "ngram_window" parameters during batch processing.
6. Evaluated the "max_tokens" and "image_size" parameters during batch processing.
7. Tested Baidu Unlimited-OCR inference with batch sizes of 2, 3, 4, and 5.
8. Compared the inference performance of the vLLM OpenAI-compatible API and Hugging Face Transformers pipeline using the same PDF, prompt, and parameter configuration.
9. Evaluated text extraction accuracy using bag-of-words matching against AWS Textract ground truth.
10. Evaluated numerical extraction accuracy by comparing extracted numbers against AWS Textract ground truth.
11. Evaluated bounding-box alignment and text correspondence between Baidu Unlimited-OCR and AWS Textract.
12. Evaluated page separation reliability in the extracted output for batch sizes of 2, 3, 4, and 5.
13. Analyzed page-marker mismatches, missing page separators, duplicate separators, and incorrect page identification in multi-page extraction.
14. Evaluated repetitive text generation, looping behavior, and page-order inconsistencies in the extracted output.
15. Investigated whether page separation issues persisted when using alternative inference approaches.
16. Compared inference time and processing performance across different batch sizes to identify potential performance improvements.
17. Analyzed extraction failures and documented the limitations of Baidu Unlimited-OCR during multi-page batch inference.
18. Consolidated evaluation results to identify suitable parameter configurations and provide recommendations for improving extraction reliability.
