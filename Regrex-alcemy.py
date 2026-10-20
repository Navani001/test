6. Batch-Size Evaluation

Evaluated batch sizes 2, 3, 4, and 5 to assess inference speed, extraction accuracy, and page-separation reliability. Batch size 2 provided limited time savings at approximately 4.28 seconds per page, while batch sizes 3 and 4 increased processing time to 5.62 and 5.66 seconds per page, respectively. Larger batches introduced significant page-separation failures and reduced extraction quality compared with the batch-size-1 baseline.

7. Inference Method Comparison

Compared vLLM and Hugging Face Transformers using identical PDFs, prompts, parameters, and logit processors.

Batch size| vLLM page failure| Transformers page failure
2| 64%| 46%
3| 51%| 39%
4| 60%| 28%

Transformers improved page-separation reliability across all three batch sizes. However, it was significantly slower. vLLM achieved better bag-of-words accuracy for batch size 3, while Transformers performed better in numerical accuracy and bounding-box alignment. For batch size 4, Transformers performed better across the evaluated accuracy metrics.

8. Page-Separation Reliability

The expected "<PAGE>" separator was not generated reliably during multi-page batch inference, making it difficult to assign extracted content to the correct pages. Missing or incorrectly generated separators caused substantial page-level failures. The results suggest that the tested inference configuration may not reliably preserve page boundaries when processing multiple pages together.

9. Parameter Validation and Extraction Quality

Additional experiments tested "ngram_size" values of 10, 20, 35, and 50, different window sizes, and DPI settings of 200 and 300.

- N-gram size 10: Reduced inference time in several batch configurations but caused poor extraction accuracy, potential content loss, and reduced bounding-box alignment.
- N-gram size 20: Improved extraction metrics compared with size 10, although page failures persisted.
- N-gram size 35: Provided a balanced baseline for extraction quality and processing time.
- N-gram size 50: Performed similarly to size 35 in some configurations but produced worse results in certain batch-size-4 measurements.
- Window sizes 128, 256, and 512: Provided limited processing-time improvements, while page-separation issues remained.
- DPI 200: For batch size 2, extraction metrics improved and processing time decreased slightly, but page failures remained unchanged. For batch sizes 3 and 4, page failures and processing time decreased, but other extraction metrics declined. Batch size 4 achieved 5.18 seconds per page.

Although the parameters and logit processors were verified across inference approaches, output differences persisted. Potential causes include generation settings, model implementation, numerical precision, or logit-processing behavior. Further investigation using identical decoding settings, stopping conditions, and precision, alongside token-ID and per-step logit comparisons, is required to identify the root cause.

Overall Conclusion

Batch size 1 remains the most reliable baseline among the tested configurations. Larger batches introduced substantial page-separation failures without consistent processing-time benefits. Hugging Face Transformers improved page-separation reliability but was significantly slower than vLLM. Further investigation into separator generation and inference implementation differences is required before adopting batch processing for production use.
