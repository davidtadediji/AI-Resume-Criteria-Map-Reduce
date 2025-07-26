from constants import EVALUATIONS, CANDIDATE_NAME, QUALIFIES, FILTER_SUMMARY, REASONS
from src.workflow.flow import create_resume_processing_flow


def main():
    shared = {}

    resume_flow = create_resume_processing_flow()

    resume_flow.run(shared=shared)

    if FILTER_SUMMARY in shared:
        print("\nDetailed evaluation results:")
        for filename, evaluation in shared.get(EVALUATIONS, {}).items():
            qualified = "Yes" if evaluation.get(QUALIFIES, False) else "X"
            name = evaluation.get(CANDIDATE_NAME, "Unknown")
            print(f"{qualified} {name} ({filename}")

            if not evaluation.get(QUALIFIES):
                print(
                    f"\n{evaluation.get(CANDIDATE_NAME, 'Unknown')} did not qualify, {', '.join(evaluation.get(REASONS, []))}")

        print("\nResume processing complete!")


if __name__ == "__main__":
    main()
