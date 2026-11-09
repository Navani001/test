Hi Team,

I am sharing the findings from our evaluation of Indra OCR to assess its suitability as an alternative OCR solution, benchmarked against our current reference system, AWS Textract.

Report link: Indra OCR Evaluation Report

1. Objective

To assess Indra OCR, a lightweight, CPU-based model developed by Datalab, on text extraction accuracy, numerical recognition, and inference performance, and to determine its viability as an alternative or complement to AWS Textract.

2. Evaluation Setup

- Datasets: Small, medium, and large collections of medical records spanning the IBR, MAR, and Smart Record services, including challenging categories such as complex tables, blurry, rotated, and handwritten pages.
- Selected configuration: OCR mode with an optimized rendering resolution, furniture retention enabled, math extraction disabled, and no additional preprocessing.
- Reference: AWS Textract outputs were used as the comparison baseline.

3. Principal Findings

- Strengths: Indra OCR demonstrated strong extraction accuracy on commonly encountered medical record pages, with reliable numerical recognition and fast CPU-only inference. Extraction accuracy remained consistent across single-core and multi-core processing configurations.

- Limitations identified through failure analysis:
  
  - Oriented pages: Inconsistent rotation handling.
  - Handwritten pages: Lower recognition accuracy compared to AWS Textract.
  - Blurry pages: Reduced text recognition accuracy.
  - Image pages: Non-text elements occasionally misrecognized as text.
  - Unusual fonts: Incorrect word splitting in certain cases.
  - Complex pages: Both Indra OCR and AWS Textract struggled with pages containing multiple challenging characteristics.

4. Recommendation and Further Work

Indra OCR is well-suited as a primary engine for regular medical record pages, while conflict pages with challenging characteristics require an alternative OCR engine. To enable this hybrid approach, further investigation is needed to separate conflict pages from non-conflict pages. A reliable page-level classification mechanism will be the focus of the next phase of this work.

Detailed metrics, category-wise results, and the full experimental methodology are provided in the report.

I would also like to thank Sorna N.A. and Abhinand N.A. for their valuable guidance and support throughout this evaluation.

Please feel free to ping me if you need any additional details or clarification regarding the evaluation and its findings.

Best regards,
