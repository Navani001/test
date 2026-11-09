 Work Item
Evaluation of Baidu Unlimited OCR Models for Layout Analysis
Approach
Evaluated Baidu Unlimited OCR and Unlimited OCR 2 on the DMALL 100-page dataset to explore their suitability for layout ground truth generation. Manually analysed the extracted layouts and bounding boxes. Bounding box generation was good, but the model-generated labels were not accurate.
2. Work Item
Layout and Bounding Box Extraction Using LLM
Approach
Explored using an LLM to extract layouts and generate bounding boxes and labels. Analysed the bounding box mismatches and also tested using Heron-generated layouts as the base, with an LLM as a judge to refine labels and bounding boxes. Tested the approach on 2 pages, and the corrections were good, but occasional retries were observed.
