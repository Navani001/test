Task 1: Structural Evaluation Research

Overview:
Research existing OCR evaluation frameworks to identify suitable metrics for evaluating the structural quality of Baidu Unlimited-OCR output.

Work Items:

1. Study OmniDocBench metrics and evaluation methodology.
2. Run the OmniDocBench evaluation code on sample data.
3. Explore other frameworks such as OCR-D, DocLayNet, and table evaluation benchmarks.
4. Compare metrics for reading order, page structure, layout, and tables.
5. Recommend suitable structural evaluation methods.

Task 2: Ground-Truth Analysis

Overview:
Analyze existing ground-truth data and identify suitable approaches for reliable OCR evaluation.

Work Items:

1. Analyze the current AWS Textract reference data.
2. Identify limitations in text, bounding boxes, and page information.
3. Research alternative datasets and ground-truth approaches.
4. Compare ground-truth requirements across evaluation frameworks.
5. Recommend a suitable reference-data approach.

Task 3: Baidu Unlimited-OCR Parameter Evaluation

Overview:
Evaluate different inference parameters and prompt templates to improve OCR extraction quality and reduce output errors.

Work Items:

1. Test batch sizes from 1 to 5.
2. Experiment with different prompt templates to reduce repetition, looping, and page-order errors.
3. Test additional supported inference parameters.
4. Evaluate outputs using existing CER, WER, and bounding-box metrics.
5. Analyze and compare experimental results.
6. Recommend the best-performing configuration.
