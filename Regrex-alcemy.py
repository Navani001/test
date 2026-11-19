1. LLM-Based OCR Difficulty Category Discovery

After analysing the newly identified difficulty categories, I felt there could be some potential OCR failure cases that were missed. So, I updated the prompt to give the LLM more room to identify additional failure categories and started a new run on the 10,000-page dataset.

2. Hybrid Layout Ground Truth Generation Toolkit

Created a toolkit with the required setup and configurations to run the LLM and Textract-based layout ground truth generation script for layout analysis. Also shared the generation script with Sorna for testing.
