import os

import pytest

from src.constants import DATA_DIR_NAME

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DATA_DIR_NAME)


@pytest.fixture
def resume_data():
    directory_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        DATA_DIR_NAME
    )
    resumes = []
    filenames = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                resumes.append(content)
                filenames.append(filename)

    return filenames, resumes
