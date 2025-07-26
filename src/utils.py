import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

from src.constants import USER

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")
google_api_key = os.environ.get("GOOGLE_API_KEY", "your-api-key")

openai_client = OpenAI(api_key=openai_api_key)


def call_llm(prompt, temperature=0.0):
    r = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=temperature,
        messages=[{"role": USER, "content": prompt}]

    )
    return r.choices[0].message.content


if __name__ == "__main__":
    print(call_llm("Tell me a short joke"))

from google import genai

google_client = genai.Client(api_key=google_api_key)


def generate_embedding(texts: List):
    result = google_client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts)
    return result.embeddings[0]


import warnings
from sentence_transformers import CrossEncoder
from typing import List


def call_reranker(query, items: List):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        scores = reranker.predict([[query, item] for item in items])
    return scores

# import os
# directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_DIR_NAME)
#
# query = MANDATORY_CRITERIA
#
# resumes = []
# filenames = []
#
# for filename in os.listdir(directory_path):
#     if filename.endswith(".txt"):
#         file_path = os.path.join(directory_path, filename)
#         with open(file_path, "r", encoding="utf-8") as file:
#             content = file.read()
#             resumes.append(content)
#             filenames.append(filename)
#
# scores = call_reranker(query, resumes)
# for name, score in zip(filenames, scores):
#     print(f"{score:.2f} - {name}")
