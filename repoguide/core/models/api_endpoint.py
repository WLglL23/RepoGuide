from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ApiEndpoint:
    """HTTP endpoint extracted from framework-specific source code."""

    method: str
    path: str
    handler: str
    file_path: str
    line_number: int
    framework: str
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "path": self.path,
            "handler": self.handler,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "framework": self.framework,
            "summary": self.summary,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiEndpoint":
        return cls(
            method=data["method"],
            path=data["path"],
            handler=data["handler"],
            file_path=data["file_path"],
            line_number=int(data["line_number"]),
            framework=data["framework"],
            summary=data.get("summary", ""),
            metadata=data.get("metadata", {}),
        )
