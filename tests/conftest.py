import os

import pytest

from src.config import DATA_DIR_NAME
from src.constants import QUALIFIED_RESUMES

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    DATA_DIR_NAME
)


@pytest.fixture
def resume_data():
    directory_path = DATA_DIR
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


QUALIFIED_RESUMES_FILES = [
    "resume_0.txt", "resume_4.txt", "resume_8.txt", "resume_12.txt", "resume_16.txt",
    "resume_20.txt", "resume_24.txt", "resume_28.txt", "resume_32.txt", "resume_36.txt",
    "resume_40.txt", "resume_44.txt", "resume_48.txt",
]


@pytest.fixture
def qualified_resumes():
    resumes = {}
    for filename in QUALIFIED_RESUMES_FILES:
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            resumes[filename] = f.read()
    return {QUALIFIED_RESUMES: resumes}
