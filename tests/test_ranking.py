from src.constants import RANKED_RESUMES, DEFAULT
from src.utils.logger import configured_logger
from src.workflow.nodes import RankResumesNode, ProcessRankResultsNode


# Set this to your actual test data directory


from src.constants import RANKED_RESUMES, DEFAULT
from src.workflow.nodes import RankResumesNode


def test_rank_resumes_node(qualified_resumes):
    rank_node = RankResumesNode()

    # PREP
    prep_res = rank_node.prep(qualified_resumes)
    assert isinstance(prep_res, dict)
    assert all(isinstance(v, str) for v in prep_res.values())

    # EXEC
    ranked = rank_node.exec(prep_res)

    # Optional: Print ranking for manual inspection
    configured_logger.debug("RANKED: %s", ranked)

    assert isinstance(ranked, list)
    assert all(isinstance(item, tuple) and isinstance(item[1], float) for item in ranked)


    # ASSERT ORDER: e.g., check that resume_4.txt scores higher than resume_48.txt
    ranks = {filename: score for filename, score in ranked}
    assert "resume_4.txt" in ranks and "resume_48.txt" in ranks
    assert ranks["resume_4.txt"] > ranks["resume_48.txt"], "Expected resume_4 to rank higher than resume_48"

    # POST
    result = rank_node.post(qualified_resumes, prep_res, ranked)
    assert result == DEFAULT
    assert RANKED_RESUMES in qualified_resumes
    assert isinstance(qualified_resumes[RANKED_RESUMES], list)



def test_process_rank_results_node(qualified_resumes):
    # Run ranking first to generate input
    rank_node = RankResumesNode()
    ranked = rank_node.exec(rank_node.prep(qualified_resumes))
    qualified_resumes[RANKED_RESUMES] = ranked

    process_node = ProcessRankResultsNode()

    # PREP
    prep_res = process_node.prep(qualified_resumes)
    assert isinstance(prep_res, list)

    # EXEC
    exec_res = process_node.exec(prep_res)
    summary, ranked_filenames, ranked_scores = exec_res

    # Basic checks
    assert "top_candidates" in summary
    assert isinstance(ranked_filenames, list)
    assert isinstance(ranked_scores, list)
    assert len(ranked_filenames) == len(ranked_scores)

    # POST
    result = process_node.post(qualified_resumes, prep_res, exec_res)
    assert result == DEFAULT
    assert "RANKING_SUMMARY" in qualified_resumes
    assert "RANKED_FILENAMES" in qualified_resumes
    assert "RANKED_SCORES" in qualified_resumes

    # ✅ Actual order checks
    # 1. Ensure ranking is in descending order of score
    assert ranked_scores == sorted(ranked_scores, reverse=True), "Scores are not in descending order"

    # 2. (Optional) Assert top candidate is expected one (based on manual inspection or ground truth)
    expected_top_filename = "resume_4.txt"  # or resume_48.txt depending on what you expect
    actual_top_filename = ranked_filenames[0]
    assert actual_top_filename == expected_top_filename, f"Expected top candidate: {expected_top_filename}, got: {actual_top_filename}"
