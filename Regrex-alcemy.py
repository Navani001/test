Work Item
Identification and Categorization of Difficult Pages for Hybrid OCR
Description
Identify and categorize difficult pages to establish a reliable approach for separating normal and difficult pages. This will support a potential hybrid OCR workflow, where Indra OCR processes normal pages and an alternative OCR solution handles difficult pages.
Task 1: LLM-Based Difficult Category Detection
Develop an LLM-based script to iterate through document pages and identify the presence of predefined difficult-page categories. The script should analyze each page, detect applicable difficulty types, and support identifying multiple categories within a single page.
Task 2: Page-to-Category Mapping
Develop a separate script to map document pages with their corresponding difficult categories based on the detection results. Organize the mapping in a structured format to identify which pages belong to each difficulty category.
