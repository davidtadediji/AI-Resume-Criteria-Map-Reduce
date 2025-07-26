# src/types.py
from typing import TypedDict, List, Dict, Any


class Evaluation(TypedDict):
    candidate_name: str
    qualifies: bool
    reasons: List[str]


class ResumeRecord(TypedDict, total=False):
    # total=False makes everything optional, since not all fields
    # exist until later in the pipeline
    text: str
    embedding: List[float]
    passes_hard_filter: bool
    filter_reasons: List[str]
    score: float
    rank: int
    evaluation: Evaluation


class SharedState(TypedDict, total=False):
    # after ReadResumesNode
    RESUMES: Dict[str, str]
    # after EmbedCriteriaNode
    CRITERIA_EMBEDDING: List[float]
    # after FilterResumesNode
    EVALUATIONS: Dict[str, Evaluation]
    FILTER_SUMMARY: Dict[str, Any]
    QUALIFIED_RESUMES: Dict[str, ResumeRecord]
    # after RankResumeNode
    RANKED_RESUMES: Any
    # after ProcessRankResultsNode
    RANKING_SUMMARY: Dict[str, Any]
    RANKED_FILENAMES: List[str]
    RANKED_SCORES: List[float]


# src/models.py
from pydantic import BaseModel
from typing import Dict, List, Optional


class SharedStateModel(BaseModel):
    # after ReadResumesNode
    RESUMES: Optional[Dict[str, ResumeRecord]]
    # after EmbedCriteriaNode
    CRITERIA_EMBEDDING: Optional[List[float]]
    # after FilterResumesNode
    EVALUATIONS: Optional[Dict[str, Evaluation]]
    FILTER_SUMMARY: Optional[Dict]
    QUALIFIED_RESUMES: Optional[Dict[str, ResumeRecord]]
    # after RankResumeNode
    RANKED_RESUMES: Optional[List]
    # after ProcessRankResultsNode
    RANKING_SUMMARY: Optional[Dict]
    RANKED_FILENAMES: Optional[List[str]]
    RANKED_SCORES: Optional[List[float]]

    class Config:
        extra = "forbid"  # disallow unexpected keys
