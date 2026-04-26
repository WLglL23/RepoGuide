from repoguide.core.models.repo_file import RepoFile


def test_repo_file_guess_language_from_extension():
    file = RepoFile(
        path="src/main.py",
        name="main.py",
        size=100,
        extension=".py",
        modified_time=1.0,
        role="entrypoint_candidate",
    )

    assert file.language == "python"


def test_repo_file_from_dict():
    file = RepoFile.from_dict({
        "path": "README.md",
        "name": "README.md",
        "size": 50,
        "extension": ".md",
        "modified_time": 1.0,
        "role": "readme",
    })

    assert file.path == "README.md"
    assert file.role == "readme"
    assert file.language == "markdown"


def test_repo_file_to_dict():
    file = RepoFile(
        path="src/UserService.java",
        name="UserService.java",
        size=200,
        extension=".java",
        modified_time=1.0,
        role="service_candidate",
    )

    data = file.to_dict()

    assert data["path"] == "src/UserService.java"
    assert data["language"] == "java"
    assert data["role"] == "service_candidate"