from pathlib import Path

from repoguide.core.parser import PythonParser


def test_python_parser_extracts_class_method_and_function(tmp_path: Path):
    source_file = tmp_path / "service.py"
    source_file.write_text(
        "\n".join(
            [
                "class UserService:",
                "    def create_user(self):",
                "        return None",
                "",
                "def main():",
                "    return None",
            ]
        ),
        encoding="utf-8",
    )

    result = PythonParser.parse_file(
        str(source_file),
        relative_path="service.py",
    )

    symbols = result.symbols
    summary = {(symbol.kind, symbol.name, symbol.parent) for symbol in symbols}

    assert ("class", "UserService", "") in summary
    assert ("method", "create_user", "UserService") in summary
    assert ("function", "main", "") in summary


def test_python_parser_extracts_fastapi_endpoint(tmp_path: Path):
    source_file = tmp_path / "api.py"
    source_file.write_text(
        "\n".join(
            [
                "from fastapi import FastAPI",
                "",
                "app = FastAPI()",
                "",
                '@app.get("/users")',
                "def list_users():",
                "    return []",
            ]
        ),
        encoding="utf-8",
    )

    result = PythonParser.parse_file(
        str(source_file),
        relative_path="api.py",
    )

    assert len(result.api_endpoints) == 1

    endpoint = result.api_endpoints[0]
    assert endpoint.method == "GET"
    assert endpoint.path == "/users"
    assert endpoint.handler == "list_users"
    assert endpoint.file_path == "api.py"
    assert endpoint.framework == "fastapi"


def test_python_parser_extracts_async_fastapi_endpoint(tmp_path: Path):
    source_file = tmp_path / "api.py"
    source_file.write_text(
        "\n".join(
            [
                "from fastapi import FastAPI",
                "",
                "app = FastAPI()",
                "",
                '@app.get("/users")',
                "async def list_users():",
                "    return []",
            ]
        ),
        encoding="utf-8",
    )

    result = PythonParser.parse_file(
        str(source_file),
        relative_path="api.py",
    )

    assert len(result.api_endpoints) == 1
    assert result.api_endpoints[0].method == "GET"
    assert result.api_endpoints[0].handler == "list_users"


def test_python_parser_ignores_non_fastapi_get_decorator(tmp_path: Path):
    source_file = tmp_path / "cache.py"
    source_file.write_text(
        "\n".join(
            [
                '@cache.get("/users")',
                "def load_users():",
                "    return []",
            ]
        ),
        encoding="utf-8",
    )

    result = PythonParser.parse_file(
        str(source_file),
        relative_path="cache.py",
    )

    assert result.api_endpoints == []
