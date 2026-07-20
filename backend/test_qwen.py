from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_BASE_URL"),
)

try:
    response = client.chat.completions.create(
        model=os.getenv("QWEN_MODEL"),
        messages=[
            {"role": "user", "content": "Hello! Reply with one sentence."}
        ],
    )

    print("SUCCESS")
    print(response.choices[0].message.content)

except Exception as e:
    print("ERROR:")
    print(e)