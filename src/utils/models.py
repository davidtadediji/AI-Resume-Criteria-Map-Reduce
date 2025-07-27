import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

from src.constants import USER
from src.utils.logger import configured_logger

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")
google_api_key = os.environ.get("GOOGLE_API_KEY", "your-api-key")

openai_client = OpenAI(api_key=openai_api_key)


def call_llm(prompt, temperature=0.0):
    try:
        r = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=temperature,
            messages=[{"role": USER, "content": prompt}]
        )
        return r.choices[0].message.content
    except Exception as e:
        configured_logger.error(f"Error calling LLM: {e}")
        return None


import openai
from typing import List


def generate_embedding(texts: List[str], model="text-embedding-3-small") -> List[float]:
    try:
        response = openai.embeddings.create(
            input=texts,
            model=model
        )
        # If batch input, response.data is a list of embeddings
        return response.data[0].embedding  # returns embedding for first input
    except Exception as e:
        configured_logger.error(f"Error generating embedding: {e}")
        return []


# from google import genai
# from google.genai import types
# google_client = genai.Client(api_key=google_api_key)
#
# def generate_embedding(texts: List, task_type="SEMANTIC_SIMILARITY"):
#     try:
#         result = google_client.models.embed_content(
#             model="gemini-embedding-001",
#             contents=texts,
#             config=types.EmbedContentConfig(task_type=task_type))
#
#         return result.embeddings[0].values
#     except Exception as e:
#         configured_logger.error(f"Error generating Google embedding: {e}")
#         return []


import warnings
from sentence_transformers import CrossEncoder
from typing import List


def call_reranker(query, items: List):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            scores = reranker.predict([[query, item] for item in items])
        return scores
    except Exception as e:
        configured_logger.error(f"Error calling reranker: {e}")
        return []
