import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
from constants import USER


def call_llm(prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[{"role": USER, "content": prompt}]

    )
    return r.choices[0].message.content


if __name__ == "__main__":
    print(call_llm("Tell me a short joke"))
