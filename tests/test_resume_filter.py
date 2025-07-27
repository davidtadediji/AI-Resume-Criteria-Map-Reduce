from src.constants import QUALIFIES
from src.workflow.nodes import ScreenResumesNode
from tests.conftest import DATA_DIR


def test_resume_does_not_qualify():
    filename = DATA_DIR + "resume_3.txt"
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    resume_item = (filename, content)

    resume_filter = ScreenResumesNode()
    _, result = resume_filter.exec(resume_item)

    assert result[QUALIFIES] is False
