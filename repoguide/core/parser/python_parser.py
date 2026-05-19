import ast
from pathlib import Path

from repoguide.core.models.code_symbol import CodeSymbol


class PythonParser:
    @staticmethod
    def parse_file(
        file_path: str,
        relative_path: str | None = None,
    ) -> list[CodeSymbol]:
        path = Path(file_path)
        symbol_path = relative_path or str(path)

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, SyntaxError, UnicodeDecodeError):
            return []

        symbols: list[CodeSymbol] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    PythonParser._build_symbol(
                        node=node,
                        kind="class",
                        path=symbol_path,
                        signature=node.name,
                    )
                )

                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        symbols.append(
                            PythonParser._build_symbol(
                                node=child,
                                kind="method",
                                path=symbol_path,
                                parent=node.name,
                                signature=f"{child.name}()",
                            )
                        )

            elif isinstance(node, ast.FunctionDef):
                symbols.append(
                    PythonParser._build_symbol(
                        node=node,
                        kind="function",
                        path=symbol_path,
                        signature=f"{node.name}()",
                    )
                )

        return symbols

    @staticmethod
    def _build_symbol(
        node: ast.AST,
        kind: str,
        path: str,
        signature: str,
        parent: str = "",
    ) -> CodeSymbol:
        line_start = getattr(node, "lineno", 0)
        line_end = getattr(node, "end_lineno", line_start)

        return CodeSymbol(
            name=getattr(node, "name", ""),
            kind=kind,
            path=path,
            line_start=line_start,
            line_end=line_end,
            language="python",
            parent=parent,
            signature=signature,
        )
