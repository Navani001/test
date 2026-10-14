Task 1: Structural Evaluation Research

Overview: Research existing OCR evaluation frameworks to understand structural evaluation metrics and identify suitable approaches for Baidu Unlimited-OCR.

Work Items:

1. Study OmniDocBench metrics and run its evaluation code on sample data.
2. Explore other frameworks such as OCR-D, DocLayNet, and table evaluation benchmarks.
3. Compare metrics for page structure, reading order, repetition, layout, and tables.
4. Analyze ground-truth requirements and the limitations of AWS Textract.
5. Recommend suitable structural evaluation metrics and ground-truth approaches.

Task 2: Baidu Unlimited-OCR Parameter Evaluation

Overview: Evaluate additional inference parameters and prompt templates to improve OCR extraction quality and reduce output errors.

Work Items:

1. Test batch sizes from 1 to 5.
2. Experiment with different prompt templates.
3. Test additional supported inference parameters.
4. Evaluate outputs using existing CER, WER, and bounding-box metrics.
5. Analyze repetition, looping, and page-order errors.
6. Recommend the best-performing configuration.
