from pocketflow import Flow

from .nodes import ReadResumesNode, ReduceFilterResultsNode, EmbedCriteriaNode, FilterResumesNode, RankResumeNode, \
    ProcessRankResultsNode


def create_resume_processing_flow():
    """Create a map-reduce flow for processing resumes."""

    embed_criteria_node = EmbedCriteriaNode()
    read_resumes_node = ReadResumesNode()
    filter_resumes_node = FilterResumesNode()
    reduce_filter_results_node = ReduceFilterResultsNode()
    rank_resume_node = RankResumeNode()
    process_rank_results_node = ProcessRankResultsNode()

    read_resumes_node >> filter_resumes_node >> reduce_filter_results_node >> rank_resume_node >> process_rank_results_node

    return Flow(start=read_resumes_node)
