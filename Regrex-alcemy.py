import base64
import requests
import os

API_URL = "http://localhost:5000/v1/chat/completions"
API_KEY = os.getenv("API_KEY")

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

image = encode_image("sample.png")

payload = {
    "model": "qwen",
    "messages": [
        {
            "role": "system",
            "content": "You are an expert document analysis assistant."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
                    Context:
                    This image belongs to a medical record.

                    Task:
                    Analyze the layout, identify tables,
                    headings and paragraphs.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image}"
                    }
                }
            ]
        }
    ],
    "temperature": 0.1
}

response = requests.post(
    API_URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json=payload
)

print(response.json())
