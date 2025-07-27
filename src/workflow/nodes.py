import os
from typing import Dict

import numpy as np
import yaml
from pocketflow import Node, BatchNode
from sklearn.metrics.pairwise import cosine_similarity

from src.config import THRESHOLD, SCREENING_TOP_N, DATA_DIR_NAME
from src.constants import RESUMES, DEFAULT, EVALUATIONS, QUALIFIES, CANDIDATE_NAME, FILTER_SUMMARY, \
    CRITERIA_EMBEDDING, \
     QUALIFIED_RESUMES, RANKED_RESUMES, RESUME_EMBEDDINGS, \
    RELEVANT_RESUMES
from src.prompts import MANDATORY_CRITERIA, EVALUATION_RESULT_FORMAT, FULL_CRITERIA
from src.utils.logger import configured_logger
from src.utils.models import call_llm, generate_embedding, call_reranker


class EmbedCriteriaNode(Node):
    """Embed the criteria for candidate qualification"""

    def prep(self, shared):
        return MANDATORY_CRITERIA

    def exec(self, prep_res):
        try:
            criteria_embedding = generate_embedding([prep_res])
            return criteria_embedding
        except Exception as e:
            configured_logger.error(f"Error in EmbedCriteriaNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
            shared[CRITERIA_EMBEDDING] = exec_res
            return DEFAULT
        except Exception as e:
            configured_logger.error(f"Error in EmbedCriteriaNode.post: {str(e)}")
            raise


class ReadResumesNode(Node):
    """Map phase: Read all resumes from the directory into shared storage."""

    def exec(self, _):
        try:
            resume_files = {}
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                    DATA_DIR_NAME)

            for filename in os.listdir(data_dir):
                if filename.endswith(".txt"):
                    file_path = os.path.join(data_dir, filename)
                    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                        resume_files[filename] = file.read()

            return resume_files
        except Exception as e:
            configured_logger.error(f"Error in ReadResumesNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
            shared[RESUMES] = exec_res
            return DEFAULT
        except Exception as e:
            configured_logger.error(f"Error in ReadResumesNode.post: {str(e)}")
            raise


class EmbedResumesNode(BatchNode):
    """Embed the criteria for candidate qualification"""

    def prep(self, shared):
        try:
            resumes = list(shared[RESUMES].items())
            return resumes
        except Exception as e:
            configured_logger.error(f"Error in EmbedResumesNode.prep: {str(e)}")
            raise

    def exec(self, prep_res):
        try:
            filename, content = prep_res
            resume_embedding = generate_embedding([content])
            return filename, resume_embedding
        except Exception as e:
            configured_logger.error(f"Error in EmbedResumesNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
            shared[RESUME_EMBEDDINGS] = {filename: result for filename, result in exec_res}
            return DEFAULT
        except Exception as e:
            configured_logger.error(f"Error in EmbedResumesNode.post: {str(e)}")
            raise


class PrefilterResumesNode(Node):
    def prep(self, shared):
        try:
            return shared[CRITERIA_EMBEDDING], shared[RESUME_EMBEDDINGS], shared[RESUMES]
        except Exception as e:
            configured_logger.error(f"Error in PrefilterResumesNode.prep: {str(e)}")
            raise

    def exec(self, prep_res):
        try:
            criteria_embedding, resume_embeddings, resumes = prep_res
            criteria_vector = np.array(criteria_embedding).reshape(1, -1)  # (1, D)
            resume_similarity_scores = [cosine_similarity(criteria_vector, np.array(embedding).reshape(1, -1)).item()
                                        for
                                        _, embedding in resume_embeddings.items()]

            relevant_resumes = {}
            for filename, resume, score in zip(resumes.keys(), resumes.values(), resume_similarity_scores):
                configured_logger.info(score)
                if score > THRESHOLD:
                    relevant_resumes[filename] = resume

            return relevant_resumes
        except Exception as e:
            configured_logger.error(f"Error in PrefilterResumesNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
            shared[RELEVANT_RESUMES] = exec_res
            return DEFAULT
        except Exception as e:
            configured_logger.error(f"Error in PrefilterResumesNode.post: {str(e)}")
            raise


class ScreenResumesNode(BatchNode):
    """Batch processing: Evaluate each resume to determine if the candidate qualifies."""

    def prep(self, shared):
        try:
            return list(shared[RELEVANT_RESUMES].items())
        except Exception as e:
            configured_logger.error(f"Error in ScreenResumesNode.prep: {str(e)}")
            raise

    def exec(self, resume_item):
        """Evaluate a single resume."""
        try:
            filename, content = resume_item

            prompt = f"""
Evaluate the following resume and determine if the candidate qualifies for an advanced technical role.
{MANDATORY_CRITERIA}

Resume:
{content}

{EVALUATION_RESULT_FORMAT}
"""
            response = call_llm(prompt)

            yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
            result = yaml.safe_load(yaml_content)

            # configured_logger.debug(result)

            return filename, result
        except Exception as e:
            configured_logger.error(f"Error in ScreenResumesNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
            shared[EVALUATIONS] = {filename: result for filename, result in exec_res}
            return DEFAULT
        except Exception as e:
            configured_logger.error(f"Error in ScreenResumesNode.post: {str(e)}")
            raise


class ReduceFilterResultsNode(Node):
    """Reduce node: Count and print out how many candidates qualify."""

    def prep(self, shared):
        try:
            return shared[EVALUATIONS]
        except Exception as e:
            configured_logger.error(f"Error in ReduceFilterResultsNode.prep: {str(e)}")
            raise

    def exec(self, evaluations: Dict[str, Dict]):
        try:
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
        except Exception as e:
            configured_logger.error(f"Error in ReduceFilterResultsNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
            filter_summary, qualified_resume_files = exec_res
            shared[FILTER_SUMMARY] = filter_summary

            configured_logger.info("\n==== Resume Hard Filtering Summary ====")
            configured_logger.info(f"Total candidates evaluation: {filter_summary['total_candidates']} ")
            configured_logger.info(
                f"Qualified candidates: {filter_summary['qualified_count']} ({filter_summary['qualified_percentage']}%")

            if filter_summary["qualified_names"]:
                configured_logger.info("\nQualified Candidates:")
                for name in filter_summary['qualified_names']:
                    configured_logger.info(f"- {name}")

            shared[QUALIFIED_RESUMES] = {filename: shared[RELEVANT_RESUMES][filename] for filename in
                                         qualified_resume_files}

            return DEFAULT
        except Exception as e:
            print(f"Error in ReduceFilterResultsNode.post: {str(e)}")
            raise


class RankResumesNode(Node):
    def prep(self, shared):
        try:
            return shared[QUALIFIED_RESUMES]
        except Exception as e:
            configured_logger.error(f"Error in RankResumesNode.prep: {str(e)}")
            raise

    def exec(self, prep_res: Dict):
        """ Remember: exec should be isolated from shared environment"""
        try:
            filenames = []
            resumes = []

            for filename, resume in prep_res.items():
                filenames.append(filename)
                resumes.append(resume)

            scores = call_reranker(FULL_CRITERIA, resumes)

            resume_scores = zip(zip(filenames, resumes), scores)

            ranked_resumes = sorted(resume_scores, key=lambda x: x[1], reverse=True)

            configured_logger.info(ranked_resumes)

            return ranked_resumes
        except Exception as e:
            print(f"Error in RankResumesNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
            shared[RANKED_RESUMES] = exec_res
            return DEFAULT
        except Exception as e:
            print(f"Error in RankResumesNode.post: {str(e)}")
            raise


class ProcessRankResultsNode(Node):
    """Reduce node: Process and summarize ranked resume results."""

    def prep(self, shared):
        try:
            return shared[RANKED_RESUMES]
        except Exception as e:
            print(f"Error in ProcessRankResultsNode.prep: {str(e)}")
            raise

    def exec(self, ranked_results):
        """
        ranked_results: List of tuples like [ ((filename, resume), score), ... ]
        """
        try:
            total_ranked = len(ranked_results)
            top_n = SCREENING_TOP_N

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
        except Exception as e:
            print(f"Error in ProcessRankResultsNode.exec: {str(e)}")
            raise

    def post(self, shared, prep_res, exec_res):
        try:
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
        except Exception as e:
            print(f"Error in ProcessRankResultsNode.post: {str(e)}")
            raise
