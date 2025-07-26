from src.constants import MANDATORY_CRITERIA
from src.utils import call_reranker, call_llm, generate_embedding


def test_reranker_scores_match_length(resume_data):
    filenames, resumes = resume_data
    query = MANDATORY_CRITERIA

    scores = call_reranker(query, resumes)
    scores = scores.tolist()  # convert numpy array to list
    assert isinstance(scores, list)
    assert len(scores) == len(resumes)
    for score in scores:
        assert isinstance(score, (int, float))

    for name, score in zip(filenames, scores):
        print(f"{score:.2f} - {name}")


def test_llm_response_short_joke():
    response = call_llm("Tell me a short joke")
    assert isinstance(response, str)
    assert len(response.strip()) > 0
    print("Joke:", response)


def test_generate_embedding_single_input():
    embedding = generate_embedding(["look at me now"])
    assert isinstance(embedding, list)
    assert all(isinstance(x, (int, float)) for x in embedding)
    print("Embedding length:", len(embedding))
