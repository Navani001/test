### Work Item 1: OCR Failure Category Discovery

Approach:

After analysing the categories found in the previous run, I thought some OCR failure cases might have been missed. So, I updated the prompt to identify more potential failure categories and ran it again on the large dataset. The results showed no major new categories, but double-orientation was identified as one noteworthy failure case. The other categories were already covered in our previous analysis.

### Work Item 2: OCR Failure Category Classification Script

Approach:

Based on the OCR failure discovery results, I created a two-phase category classification script. In Phase A, the script takes an image and identifies the categories that the page may belong to, along with their severity and scores. In Phase B, it checks each identified subcategory separately by sending the image and subcategory to the model, which returns a yes/no result to confirm whether that category is present.

### Work Item 3: Hybrid LLM and Textract-Based Layout Ground Truth Generation

Approach:

We first tried using Heron predictions as a reference and asking the LLM to correct the bounding boxes, but it sometimes produced mismatches. We then tried a pure LLM-based approach, but the bounding boxes were still not accurate enough. So, we introduced Textract coordinates as a reference to help the LLM predict layout regions more accurately. The initial results look promising. I created and shared the generation toolkit with Sorna for testing, and we are planning to run it over the weekend.
