3. Parameter Evaluation and Optimization

Evaluated "ngram_size" values of 10, 20, 35, and 50 to identify a suitable configuration for extraction accuracy and processing performance.

- N-gram 10: Produced the weakest results, with randomly generated page separators, possible content omission, bag-of-words F1 of approximately 0.92, numerical F1 of 0.90, and processing time of 4.89 seconds per page.
- N-gram 20: Improved over size 10 but still showed page-separation failures and a slight reduction in accuracy, with processing time of 4.64 seconds per page.
- N-gram 35: Achieved a bag-of-words F1-score of 0.9627, numerical F1-score of 0.9661, 97.88% bounding-box coverage, and 4.65 seconds per page.
- N-gram 50: Produced results similar to size 35, with marginal accuracy improvements and processing time of 4.66 seconds per page.

4. Window Size Evaluation

Compared "window_size" values of 128, 512, and 1024.

Metric| 128| 512| 1024
Bag-of-words F1| 0.9627| 0.9611| 0.9611
Numerical F1| 0.9661| 0.9635| 0.9636
Bounding-box coverage| 97.88%| 97.77%| 97.78%
CER| 0.1790| 0.1804| 0.1804
WER| 0.2114| 0.2136| 0.2139
Average time/page| 4.65 s| 4.65 s| 4.66 s

Larger window sizes slightly reduced detected repetitive output, but did not improve extraction accuracy or processing time. The baseline "window_size=128" provided the best overall balance among the tested configurations.

5. DPI and Maximum Token Evaluation

DPI evaluation

Metric| DPI 300 (Baseline)| DPI 200
Bag-of-words F1| 0.9627| 0.9601
Numerical F1| 0.9661| 0.9608
Bounding-box coverage| 97.88%| 97.49%
CER| 0.1790| 0.1738
WER| 0.2114| 0.2065
Average time/page| 4.65 s| 4.49 s

DPI 200 reduced processing time by approximately 3.4%, with slightly lower bag-of-words and numerical accuracy. CER and WER also decreased, indicating fewer sequence-level errors under the current evaluation method. DPI 300 provided better bag-of-words and numerical scores and bounding-box coverage, while DPI 200 offered faster processing.

Maximum token evaluation

Metric| 8192| 16000| 30000
Bag-of-words F1| 0.9627| 0.9627| 0.9627
Numerical F1| 0.9661| 0.9661| 0.9661
Bounding-box coverage| 97.88%| 97.88%| 97.88%
Average time/page| 4.65 s| 4.65 s| 4.65 s

Increasing "max_tokens" did not produce measurable improvements in the evaluated metrics or processing time. Therefore, 8192 tokens was sufficient for the tested dataset.

Overall Conclusion

Among the tested configurations, "ngram_size=35", "window_size=128", DPI 300, and "max_tokens=8192" provided a strong balance of extraction accuracy, bounding-box coverage, and processing time. Lower n-gram values introduced page-separation issues, while larger window sizes and token limits offered no meaningful overall improvement. Repetitive output was monitored during evaluation, but it was not treated as a failure by itself because repetition may be legitimate document content.
