import os
from src.constants import QUALIFIES, DATA_DIR_NAME
from src.workflow.nodes import FilterResumesNode

directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_DIR_NAME)

def test_resume_does_not_qualify():
    filename = directory_path + "/resume_3.txt"
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    resume_item = (filename, content)

    resume_filter = FilterResumesNode()
    _, result = resume_filter.exec(resume_item)

    assert result[QUALIFIES] is False
