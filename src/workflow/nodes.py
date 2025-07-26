import os
from typing import Dict

import yaml
from pocketflow import Node, BatchNode

from src.constants import RESUMES, DATA_DIR_NAME, DEFAULT, EVALUATIONS, QUALIFIES, CANDIDATE_NAME, FILTER_SUMMARY, \
    CRITERIA, \
    MANDATORY_CRITERIA, QUALIFIED_RESUMES
from src.utils import call_llm, generate_embedding


class EmbedCriteriaNode(Node):
    """Embed the criteria for candidate qualification"""

    def exec(self, prep_res):
        criteria_embedding = generate_embedding([MANDATORY_CRITERIA])
        return criteria_embedding

    def post(self, shared, prep_res, exec_res):
        shared[CRITERIA] = exec_res
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


class FilterResumesNode(BatchNode):
    """Batch processing: Evaluate each resume to determine if the candidate qualifies."""

    def prep(self, shared):
        return list(shared[RESUMES].items())

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
        shared[QUALIFIED_RESUMES] = {filename: shared[RESUMES] for filename in qualified_resume_files}

        print("\n==== Resume Qualification Summary ====")
        print(f"Total candidates evaluation: {exec_res['total_candidates']} ")
        print(f"Qualified candidates: {exec_res['qualified_count']} ({exec_res['qualified_percentage']}%")

        if exec_res["qualified_names"]:
            print("\nQualified Candidates:")
            for name in exec_res['qualified_names']:
                print(f"- {name}")

        return "default"

# class RankResumeNode(Node):
#     def prep(self, shared):
#         return shared[QUALIFIED_RESUMES]
#
#     def exec(self, prep_res: Dict):
#         """ Remember: exec should be isolated from shared environment"""
#         [for filename in prep_res]
#         response = call_llm(prompt)
#
#     def post(self, shared, prep_res, exec_res):
#         pass
