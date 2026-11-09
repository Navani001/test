### 1\. Work Item

Evaluation of Baidu Unlimited OCR Models for Layout Analysis

Approach

Evaluated Baidu Unlimited OCR and Unlimited OCR 2 on the DMALL 100-page dataset to explore their suitability for layout ground truth generation. Manually analysed the extracted layouts and bounding boxes. Bounding box generation was good, but the model-generated labels were not accurate.

### 2\. Work Item

Layout and Bounding Box Extraction Using LLM

Approach

Explored using an LLM to extract layouts and generate bounding boxes and labels. Analysed the bounding box mismatches and also tested using Heron-generated layouts as the base, with an LLM as a judge to refine labels and bounding boxes. Tested the approach on 2 pages, and the corrections were good, but occasional retries were observed.

### 3\. Work Item

Prompt Optimization for Layout Analysis

Approach

Discussed the LLM-based correction approach and retry issues with Sorna. Received suggestions for prompt updates and shared the generated image with bounding boxes for further analysis. Planned to incorporate the suggested changes to improve the process of generating suitable layout ground truth.
