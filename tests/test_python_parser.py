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

    symbols = PythonParser.parse_file(
        str(source_file),
        relative_path="service.py",
    )

    summary = {(symbol.kind, symbol.name, symbol.parent) for symbol in symbols}

    assert ("class", "UserService", "") in summary
    assert ("method", "create_user", "UserService") in summary
    assert ("function", "main", "") in summary
