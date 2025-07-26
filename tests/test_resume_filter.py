from src.constants import QUALIFIES
from src.workflow.nodes import EvaluateResumesNode
from tests.conftest import data_dir


def test_resume_does_not_qualify():
    filename = data_dir + "/resume_3.txt"
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    resume_item = (filename, content)

    resume_filter = EvaluateResumesNode()
    _, result = resume_filter.exec(resume_item)

    assert result[QUALIFIES] is False
