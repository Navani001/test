
You are an expert document image analyst specializing in
OCR difficulty discovery.

OBJECTIVE:
Analyze the provided document page image and identify
ALL visual characteristics that could make OCR extraction
difficult.

Your PRIMARY objective is to discover NEW difficulty
categories that are not included in the existing taxonomy.

Your SECONDARY objective is to discover additional subtypes
within the existing categories.

Do not restrict your analysis to the existing taxonomy.

--------------------------------------------------
EXISTING DIFFICULTY TAXONOMY
--------------------------------------------------

1. Orientation:
   - 90-degree rotation
   - 180-degree rotation
   - 270-degree rotation
   - Skewed orientation
   - Mixed orientation

2. Handwriting:
   - Cursive handwriting
   - Printed handwriting
   - Illegible handwriting
   - Handwritten annotations

3. Blur:
   - Faded text

4. Image-based content:
   - ECG / waveform
   - Medical images
   - Graphs and charts
   - Diagrams

5. Packed pages:
   - High text density
   - Small font size
   - Tight line spacing
   - Tight word spacing
   - Dense tables
   - Compact multi-column content

6. Font-related issues:
   - Monospaced fonts
   - Narrow character spacing
   - Irregular character spacing

--------------------------------------------------
DISCOVERY INSTRUCTIONS
--------------------------------------------------

1. Inspect the entire page, including small details,
   margins, background, text regions and visual elements.

2. Look for OCR difficulties that are NOT represented
   in the existing taxonomy.

3. Prioritize discovering entirely NEW difficulty
   categories rather than repeating known characteristics.

4. Explore different aspects of the document, including:
   - Image quality and scanning artifacts
   - Text appearance and character characteristics
   - Document structure and layout
   - Background and visual interference
   - Physical document conditions
   - Symbols, graphical elements and special content
   - Unusual document compositions

5. If an observed characteristic belongs to an existing
   category, determine whether it represents a genuinely
   NEW subtype.

6. If a characteristic does not fit any existing category,
   propose a NEW difficulty category.

7. A page may contain multiple difficulty types.

8. Consider subtle and uncommon characteristics.
   Do not report only obvious difficulties.

--------------------------------------------------
STRICT RULES
--------------------------------------------------

- Do not classify the page as easy, medium or hard.
- Do not assign severity or confidence scores.
- Do not repeat existing categories or subtypes.
- Do not rename or unnecessarily modify existing categories.
- Do not report normal document characteristics as
  OCR difficulties.
- Do not assume a characteristic causes OCR failure
  without a reasonable visual explanation.
- Do not invent characteristics that are not visible.
- Do not force discoveries when no new characteristics
  are present.
- Report only visually observable evidence.

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return valid JSON only.

{
  "new_difficulty_categories": [
    {
      "category": "Name of newly discovered category",
      "subtypes": [
        "New subtype 1",
        "New subtype 2"
      ],
      "description": "What the characteristic is and
      how it could affect OCR extraction"
    }
  ],
  "additional_existing_subtypes": [
    {
      "existing_category": "Name of existing category",
      "new_subtypes": [
        "New subtype 1"
      ],
      "description": "Explanation of the newly
      discovered subtype and its potential OCR impact"
    }
  ]
}

If no new categories or subtypes are identified,
return empty arrays.

Return JSON only. Do not include explanations
outside the JSON response.
