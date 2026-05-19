from dataclasses import dataclass, field

from repoguide.core.models.api_endpoint import ApiEndpoint
from repoguide.core.models.code_symbol import CodeSymbol


@dataclass
class PythonParseResult:
    symbols: list[CodeSymbol] = field(default_factory=list)
    api_endpoints: list[ApiEndpoint] = field(default_factory=list)
