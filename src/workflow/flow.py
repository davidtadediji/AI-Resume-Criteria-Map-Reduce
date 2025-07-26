from pocketflow import Flow

from .nodes import ReadResumesNode, ReduceFilterResultsNode, EmbedCriteriaNode, RankResumesNode, \
    ProcessRankResultsNode, PrefilterResumesNode, EmbedResumesNode, ScreenResumesNode


def create_resume_processing_flow():
    """Create a map-reduce flow for processing resumes."""

    embed_criteria_node = EmbedCriteriaNode()
    read_resumes_node = ReadResumesNode()
    embed_resumes_node = EmbedResumesNode()
    prefilter_resumes_node = PrefilterResumesNode()
    screen_resumes_node = ScreenResumesNode()
    reduce_filter_results_node = ReduceFilterResultsNode()
    rank_resumes_node = RankResumesNode()
    process_rank_results_node = ProcessRankResultsNode()

    embed_criteria_node >> read_resumes_node >> embed_resumes_node >> prefilter_resumes_node >> screen_resumes_node >> reduce_filter_results_node >> rank_resumes_node >> process_rank_results_node

    return Flow(start=embed_criteria_node)
