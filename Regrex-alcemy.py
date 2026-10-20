Inference Time and Processing Performance

Evaluated inference time across batch sizes 1–4 by varying "ngram_size", "window_size", "max_tokens", and DPI.

- Batch size 1: Processing time remained stable at approximately 4.64–4.89 seconds per page. DPI 200 reduced it to 4.49 seconds, while increasing "max_tokens" to 16000 or 30000 showed no improvement.
- Batch size 2: Processing time ranged from 3.14 to 7.40 seconds per page. Lower n-gram values and DPI 200 were faster, while larger token limits increased processing time.
- Batch size 3: Processing time ranged from 4.35 to 9.53 seconds per page. DPI 200 reduced it to 5.04 seconds, while higher token limits significantly increased latency.
- Batch size 4: Processing time ranged from 4.73 to 9.64 seconds per page. DPI 200 reduced it to 5.18 seconds, while higher token limits again increased latency.

Conclusion: Batch size 1 provided the most stable performance and extraction reliability. Larger batches did not consistently improve processing efficiency and introduced page-separation failures. Increasing "max_tokens" significantly increased processing time for batch sizes 2–4 without a corresponding improvement in extraction quality.
