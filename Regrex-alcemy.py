We can split the work into 3 main tasks, each with a clear overview and smaller work items.

### Task 1: Structural Evaluation Research

Overview: Research existing frameworks to identify suitable metrics for evaluating the structural quality of Baidu Unlimited-OCR output.

Work items:

* Study OmniDocBench metrics and evaluation methodology.

* Run the OmniDocBench evaluation code on sample data.

* Explore other frameworks such as OCR-D, DocLayNet, and table evaluation benchmarks.

* Compare metrics for reading order, page structure, layout, and tables.

* Recommend suitable structural evaluation methods.

### Task 2: Ground-Truth Analysis

Overview: Analyze existing ground-truth data and identify suitable approaches for reliable OCR evaluation.

Work items:

* Analyze the current AWS Textract reference data.

* Identify limitations in text, bounding boxes, and page information.

* Research alternative datasets and ground-truth approaches.

* Compare ground-truth requirements across evaluation frameworks.

* Recommend a suitable reference-data approach.

### Task 3: Baidu Unlimited-OCR Parameter Evaluation

Overview: Evaluate inference parameters and prompt templates to improve OCR extraction quality and reduce output errors.

Work items:

* Test batch sizes from 1 to 5.

* Experiment with different prompt templates.

* Test additional supported inference parameters.

* Evaluate outputs using existing CER, WER, and bounding-box metrics.

* Analyze repetition, looping, and page-order errors.

* Recommend the best-performing configuration.

### Suggested 5-day schedule

| Day   | Focus                                                     |
| ----- | --------------------------------------------------------- |
| Day 1 | OmniDocBench research and batch-size testing              |
| Day 2 | Run the evaluation framework and test prompt templates    |
| Day 3 | Ground-truth analysis and research alternative frameworks |
| Day 4 | Test additional parameters and analyze OCR errors         |
| Day 5 | Compare findings and prepare recommendations              |

Final deliverables: Framework comparison, ground-truth recommendations, parameter experiment results, and recommended OCR configuration.
