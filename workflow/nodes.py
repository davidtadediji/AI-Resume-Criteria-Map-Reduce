import os

import yaml
from pocketflow import Node, BatchNode

from constants import RESUME, DIR_NAME, DEFAULT, EVALUATIONS, QUALIFIES, CANDIDATE_NAME, SUMMARY
from utils import call_llm


class ReadResumesNode(Node):
    """Map phase: Read all resumes from the directory into shared storage."""

    def exec(self, _):
        resume_files = {}
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DIR_NAME)

        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    resume_files[filename] = file.read()

        return resume_files

    def post(self, shared, prep_res, exec_res):
        shared[RESUME] = exec_res
        return DEFAULT


class EvaluateResumesNode(BatchNode):
    """Batch processing: Evaluate each resume to determine if the candidate qualifies."""

    def prep(self, shared):
        return list(shared[RESUME].items())

    def exec(self, resume_item):
        """Evaluate a singe resume."""
        filename, content = resume_item

        prompt = f"""
Evaluate the following resume and determine if the candidate qualifies for an advanced technical role.
Criteria for qualification.
- At least a bachelor's degree in a relevant field
- At least 3 years of relevant work experience
- Strong technical skills in software development, data analysis, or related areas

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

        return filename, result

    def post(self, shared, prep_res, exec_res_list):
        shared[EVALUATIONS] = {filename: result for filename, result in exec_res_list}
        return DEFAULT


class ReduceResultsNode(Node):
    """Reduce node: Count and print out how many candidates qualify."""

    def prep(self, shared):
        return shared[EVALUATIONS]

    def exec(self, evaluations):
        qualified_count = 0
        total_count = len(evaluations)
        qualified_candidates = []

        for filename, evaluation in evaluations.items():
            if evaluation.get(QUALIFIES, False):
                qualified_count += 1
                qualified_candidates.append(evaluation.get(CANDIDATE_NAME, "Unknown"))

        summary = {
            "total_candidates": total_count,
            "qualified_count": qualified_count,
            "qualified_percentage": round(qualified_count / total_count * 100, 1) if total_count > 0 else 0,
            "qualified_names": qualified_candidates
        }

        return summary

    def post(self, shared, prep_res, exec_res):
        shared[SUMMARY] = exec_res

        print("\n==== Resume Qualification Summary ====")
        print(f"Total candidates evaluation: {exec_res['total_candidates']} ")
        print(f"Qualified candidates: {exec_res['qualified_count']} ({exec_res['qualified_percentage']}%")

        if exec_res["qualified_names"]:
            print("\nQualified Candidates:")
            for name in exec_res['qualified_names']:
                print(f"- {name}")

        return "default"
