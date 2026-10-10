from collections import defaultdict

easy_count = 10
hard_count = 10

template_pdf_list_formatted = defaultdict(
    lambda: {
        "easy": [0, {}],
        "hard": [0, {}]
    }
)

template_pdf_list = (
    df.groupby(["template", "difficulty"])["file_name"]
      .apply(set)
)

for (template, difficulty), filenames in template_pdf_list.items():
    if difficulty not in ("easy", "hard"):
        continue

    pdf_data = path_to_pdf_list(list(filenames))

    template_pdf_list_formatted[template][difficulty] = [
        sum(pdf_data.values()),
        pdf_data
    ]

# Calculate missing pages per template
default_missing_count = 0

for template, data in template_pdf_list_formatted.items():
    easy_available = data["easy"][0]
    hard_available = data["hard"][0]

    # Select up to 10 pages from each difficulty
    easy_selected = min(easy_available, easy_count)
    hard_selected = min(hard_available, hard_count)

    # Fill easy shortage using extra hard pages
    extra_hard = min(
        easy_count - easy_selected,
        hard_available - hard_selected
    )
    hard_selected += extra_hard

    # Fill hard shortage using extra easy pages
    extra_easy = min(
        hard_count - hard_selected,
        easy_available - easy_selected
    )
    easy_selected += extra_easy

    missing = max(
        0,
        easy_count + hard_count - easy_selected - hard_selected
    )

    data["selected_easy"] = easy_selected
    data["selected_hard"] = hard_selected
    data["missing"] = missing

    default_missing_count += missing

print("Default template needs additional pages:", default_missing_count)
