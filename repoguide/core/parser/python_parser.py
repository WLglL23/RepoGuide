import ast
from pathlib import Path
from typing import Any, Dict

from repoguide.core.models.api_endpoint import ApiEndpoint
from repoguide.core.models.code_symbol import CodeSymbol
from repoguide.core.parser.python_parse_result import PythonParseResult


class PythonParser:
    @staticmethod
    def parse_file(
        file_path: str,
        relative_path: str | None = None,
    ) -> PythonParseResult:
        path = Path(file_path)
        symbol_path = relative_path or str(path)

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, SyntaxError, UnicodeDecodeError):
            return PythonParseResult()

        symbols: list[CodeSymbol] = []

        api_endpoints: list[ApiEndpoint] = []

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

                api_endpoints.extend(
                    PythonParser._extract_fastapi_endpoints_from_function(
                        node=node,
                        file_path=symbol_path,
                    )
                )

        return PythonParseResult(symbols=symbols, api_endpoints=api_endpoints)

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

    @staticmethod
    def _extract_fastapi_endpoint(
        decorator: ast.expr,
        handler: str,
        file_path: str,
        line_number: int,
    ) -> ApiEndpoint | None:
        http_methods = {"get", "post", "put", "delete", "patch"}

        if not isinstance(decorator, ast.Call):
            return None

        func = decorator.func
        if not isinstance(func, ast.Attribute):
            return None

        method = func.attr.lower()
        if method not in http_methods:
            return None

        if not decorator.args:
            return None

        first_arg = decorator.args[0]
        if not isinstance(first_arg, ast.Constant):
            return None

        if not isinstance(first_arg.value, str):
            return None

        return PythonParser._build_api_endpoint(
            method=method.upper(),
            path=first_arg.value,
            handler=handler,
            file_path=file_path,
            line_number=line_number,
        )

    @staticmethod
    def _build_api_endpoint(
        method: str,
        path: str,
        handler: str,
        file_path: str,
        line_number: int,
        framework: str = "fastapi",
        summary: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> ApiEndpoint:
        return ApiEndpoint(
            method=method,
            path=path,
            handler=handler,
            file_path=file_path,
            line_number=line_number,
            framework=framework,
            summary=summary,
            metadata=metadata or {},
        )

    @staticmethod
    def _extract_fastapi_endpoints_from_function(
        node: ast.FunctionDef,
        file_path: str,
    ) -> list[ApiEndpoint]:
        endpoints: list[ApiEndpoint] = []

        for decorator in node.decorator_list:
            endpoint = PythonParser._extract_fastapi_endpoint(
                decorator=decorator,
                handler=node.name,
                file_path=file_path,
                line_number=getattr(node, "lineno", 0),
            )
            if endpoint is not None:
                endpoints.append(endpoint)

        return endpoints
