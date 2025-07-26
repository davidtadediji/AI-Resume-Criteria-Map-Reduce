import os
from typing import Dict

import numpy as np
import yaml
from pocketflow import Node, BatchNode
from sklearn.metrics.pairwise import cosine_similarity

from src.constants import RESUMES, DATA_DIR_NAME, DEFAULT, EVALUATIONS, QUALIFIES, CANDIDATE_NAME, FILTER_SUMMARY, \
    CRITERIA_EMBEDDING, \
    MANDATORY_CRITERIA, QUALIFIED_RESUMES, FULL_CRITERIA, RANKED_RESUMES, RESUME_EMBEDDINGS, THRESHOLD, RELEVANT_RESUMES
from src.utils import call_llm, generate_embedding, call_reranker


class EmbedCriteriaNode(Node):
    """Embed the criteria for candidate qualification"""

    def prep(self, shared):
        return MANDATORY_CRITERIA

    def exec(self, prep_res):
        criteria_embedding = generate_embedding([prep_res])
        return criteria_embedding

    def post(self, shared, prep_res, exec_res):
        shared[CRITERIA_EMBEDDING] = exec_res
        return DEFAULT


class ReadResumesNode(Node):
    """Map phase: Read all resumes from the directory into shared storage."""

    def exec(self, _):
        resume_files = {}
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                DATA_DIR_NAME)

        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                    resume_files[filename] = file.read()

        return resume_files

    def post(self, shared, prep_res, exec_res):
        shared[RESUMES] = exec_res
        return DEFAULT


class EmbedResumesNode(BatchNode):
    """Embed the criteria for candidate qualification"""

    def prep(self, shared):
        resumes = list(shared[RESUMES].items())
        return resumes

    def exec(self, prep_res):
        filename, content = prep_res
        resume_embedding = generate_embedding([content])
        return filename, resume_embedding

    def post(self, shared, prep_res, exec_res):
        shared[RESUME_EMBEDDINGS] = {filename: result for filename, result in exec_res}
        return DEFAULT


class PrefilterResumesNode(Node):
    def prep(self, shared):
        return shared[CRITERIA_EMBEDDING], shared[RESUME_EMBEDDINGS], shared[RESUMES]

    def exec(self, prep_res):
        criteria_embedding, resume_embeddings, resumes = prep_res
        criteria_vector = np.array(criteria_embedding).reshape(1, -1)  # (1, D)
        resume_similarity_scores = [cosine_similarity(criteria_vector, np.array(embedding).reshape(1, -1)).item() for
                                    _, embedding in resume_embeddings.items()]

        relevant_resumes = {}
        for filename, resume, score in zip(resumes.keys(), resumes.values(), resume_similarity_scores):
            print(score)
            if score > THRESHOLD:
                relevant_resumes[filename] = resume

        return relevant_resumes

    def post(self, shared, prep_res, exec_res):
        shared[RELEVANT_RESUMES] = exec_res
        return DEFAULT


class ScreenResumesNode(BatchNode):
    """Batch processing: Evaluate each resume to determine if the candidate qualifies."""

    def prep(self, shared):
        return list(shared[RELEVANT_RESUMES].items())

    def exec(self, resume_item):
        """Evaluate a single resume."""
        filename, content = resume_item

        prompt = f"""
Evaluate the following resume and determine if the candidate qualifies for an advanced technical role.
{MANDATORY_CRITERIA}

Resume:
{content}

Return your evaluation in YAML format:
```yaml
candidate_name: [Name of the candidate]
qualifies: [true/false]
reasons:
- [First reason for qualification/disqualification]
- [Second reason, if applicable]
```
"""
        response = call_llm(prompt)

        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        result = yaml.safe_load(yaml_content)

        print(result)

        return filename, result

    def post(self, shared, prep_res, exec_res):
        shared[EVALUATIONS] = {filename: result for filename, result in exec_res}
        return DEFAULT


class ReduceFilterResultsNode(Node):
    """Reduce node: Count and print out how many candidates qualify."""

    def prep(self, shared):
        return shared[EVALUATIONS]

    def exec(self, evaluations: Dict[str, Dict]):
        qualified_count = 0
        total_count = len(evaluations)
        qualified_resumes = []
        qualified_candidates_names = []

        for filename, evaluation in evaluations.items():
            if evaluation.get(QUALIFIES, False):
                qualified_count += 1
                qualified_candidates_names.append(evaluation.get(CANDIDATE_NAME, "Unknown"))
                qualified_resumes.append(filename)

        summary = {
            "total_candidates": total_count,
            "qualified_count": qualified_count,
            "qualified_percentage": round(qualified_count / total_count * 100, 1) if total_count > 0 else 0,
            "qualified_names": [qualified_candidate for qualified_candidate in qualified_candidates_names]
        }

        return summary, qualified_resumes

    def post(self, shared, prep_res, exec_res):
        filter_summary, qualified_resume_files = exec_res
        shared[FILTER_SUMMARY] = filter_summary

        print("\n==== Resume Hard Filtering Summary ====")
        print(f"Total candidates evaluation: {filter_summary['total_candidates']} ")
        print(f"Qualified candidates: {filter_summary['qualified_count']} ({filter_summary['qualified_percentage']}%")

        if filter_summary["qualified_names"]:
            print("\nQualified Candidates:")
            for name in filter_summary['qualified_names']:
                print(f"- {name}")

        shared[QUALIFIED_RESUMES] = {filename: shared[RELEVANT_RESUMES][filename] for filename in
                                     qualified_resume_files}

        return DEFAULT


class RankResumesNode(Node):
    def prep(self, shared):
        return shared[QUALIFIED_RESUMES]

    def exec(self, prep_res: Dict):
        """ Remember: exec should be isolated from shared environment"""
        filenames = []
        resumes = []

        for filename, resume in prep_res.items():
            filenames.append(filename)
            resumes.append(resume)

        scores = call_reranker(FULL_CRITERIA, resumes)

        resume_scores = zip(zip(filenames, resumes), scores)

        ranked_resumes = sorted(resume_scores, key=lambda x: x[1], reverse=True)

        print(ranked_resumes)

        return ranked_resumes

    def post(self, shared, prep_res, exec_res):
        shared[RANKED_RESUMES] = exec_res
        return DEFAULT


class ProcessRankResultsNode(Node):
    """Reduce node: Process and summarize ranked resume results."""

    def prep(self, shared):
        return shared[RANKED_RESUMES]

    def exec(self, ranked_results):
        """
        ranked_results: List of tuples like [ ((filename, resume), score), ... ]
        """
        total_ranked = len(ranked_results)
        top_n = 10  # You can adjust or make dynamic

        # Extract filenames and scores
        ranked_filenames = [item[0][0] for item in ranked_results]
        ranked_scores = [item[1] for item in ranked_results]

        # Build summary dict
        summary = {
            "total_ranked": total_ranked,
            "top_n": min(top_n, total_ranked),
            "top_candidates": [
                {"filename": ranked_results[i][0][0], "score": ranked_results[i][1]}
                for i in range(min(top_n, total_ranked))
            ],
        }

        return summary, ranked_filenames, ranked_scores

    def post(self, shared, prep_res, exec_res):
        summary, ranked_filenames, ranked_scores = exec_res
        shared["RANKING_SUMMARY"] = summary
        shared["RANKED_FILENAMES"] = ranked_filenames
        shared["RANKED_SCORES"] = ranked_scores

        print("\n==== Resume Ranking Summary ====")
        print(f"Total ranked resumes: {summary['total_ranked']}")
        print(f"Top {summary['top_n']} candidates:")

        for candidate in summary["top_candidates"]:
            print(f"- {candidate['filename']} (score: {candidate['score']:.4f})")

        return DEFAULT
