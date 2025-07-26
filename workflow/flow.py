from pocketflow import Flow

from .nodes import ReadResumesNode, EvaluateResumesNode, ReduceResultsNode


def create_resume_processing_flow():
    """Create a map-reduce flow for processing resumes."""

    read_resumes_node = ReadResumesNode()
    evaluate_resumes_node = EvaluateResumesNode()
    reduce_results_node = ReduceResultsNode()

    read_resumes_node >> evaluate_resumes_node >> reduce_results_node

    return Flow(start=read_resumes_node)
