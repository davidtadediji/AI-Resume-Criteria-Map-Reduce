from src.prompts import MANDATORY_CRITERIA
from src.workflow.nodes import EmbedResumesNode, PrefilterResumesNode, EmbedCriteriaNode
from tests.conftest import DATA_DIR


def test_resume_pre_filtering():
    criteria_encoder = EmbedCriteriaNode()
    resume_encoder = EmbedResumesNode()
    resume_prefilter = PrefilterResumesNode()

    criteria_embedding = criteria_encoder.exec(MANDATORY_CRITERIA)

    filename = "resume_3.txt"
    filepath = DATA_DIR + filename
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    resume_item = (filename, content)
    resume_embedding = resume_encoder.exec(resume_item)

    resume_embedding = {filename: resume_embedding[1]}
    resume_item = {filename: content}
    relevant_resumes = resume_prefilter.exec((criteria_embedding, resume_embedding, resume_item))

    assert content == relevant_resumes[filename]
