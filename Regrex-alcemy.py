def build_content(prompt, image_paths):
    content = [
        {
            "type": "text",
            "text": prompt
        }
    ]

    for image_path in image_paths:
        content.append(
            encode_image(image_path)
        )

    return content


def generate(image_paths):
    start = time.time()

    for i in range(0, len(image_paths), 2):

        batch = image_paths[i:i + 2]

        messages = [
            {
                "role": "user",
                "content": build_content(
                    "Multi page parsing. "
                    "Keep each page's response separate. "
                    "For each page use the format "
                    "<<<PAGE_START>>> and <<<PAGE_END>>>.",
                    batch
                )
            }
        ]

        response = client.chat.completions.create(
            model="baidu/Unlimited-OCR",
            messages=messages,
            max_tokens=8192,
            temperature=0.0,
            extra_body={
                "skip_special_tokens": False,
                "vllm_xargs": {
                    "ngram_size": 35,
                    "window_size": 1024
                }
            }
        )

        result = response.choices[0].message.content

        pages = result.split(
            "<<<PAGE_START>>>"
        )

        for j, page_result in enumerate(pages[1:]):

            page_result = page_result.split(
                "<<<PAGE_END>>>",
                1
            )[0].strip()

            page_number = i + j + 1

            with open(
                f"page_{page_number:04d}.txt",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(page_result)

            print(
                f"Page {page_number} saved"
            )

    print(
        f"Response costs: "
        f"{time.time() - start:.2f}s"
    )
