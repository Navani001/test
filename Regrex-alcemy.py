import re


def clean_ocr_text(text: str) -> str:
    # Remove OCR special tokens and page markers
    text = re.sub(r"<\|.*?\|>", " ", text)

    # Remove Markdown code blocks and formatting
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`+", "", text)
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    text = re.sub(r"\*\*|__|~~|\*|_", "", text)

    # Keep visible link text, remove URL formatting
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove HTML/XML tags
    text = re.sub(r"</?[^>]+>", " ", text)

    # Remove escaped and actual newline/tab separators
    text = re.sub(r"\\[nrt]", " ", text)
    text = re.sub(r"[\r\n\t]+", " ", text)

    # Normalize whitespace
    return re.sub(r"\s+", " ", text).strip()


def parse_textract_record(content, line_coord, word_coord):
    lines = str(content).split("\n")
    line_boxes = str(line_coord).split("|") if line_coord else []
    word_boxes = str(word_coord).split("|") if word_coord else []

    result = []
    word_index = 0

    for line_index, line in enumerate(lines):
        words = [word.strip() for word in line.split("\t") if word.strip()]
        parsed_words = []

        for word in words:
            box = (
                word_boxes[word_index].strip()
                if word_index < len(word_boxes)
                else None
            )

            parsed_words.append({
                "word": word,
                "word_coord": box
            })
            word_index += 1

        result.append({
            "line": line,
            "line_coord": (
                line_boxes[line_index].strip()
                if line_index < len(line_boxes)
                else None
            ),
            "words": parsed_words
        })

    return result
