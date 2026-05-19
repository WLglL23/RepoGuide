from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CodeSymbol:
    """Structured symbol extracted from a source file."""

    name: str
    kind: str
    path: str
    line_start: int
    line_end: int
    language: str
    parent: str = ""
    signature: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "path": self.path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "language": self.language,
            "parent": self.parent,
            "signature": self.signature,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeSymbol":
        return cls(
            name=data["name"],
            kind=data["kind"],
            path=data["path"],
            line_start=int(data["line_start"]),
            line_end=int(data["line_end"]),
            language=data["language"],
            parent=data.get("parent", ""),
            signature=data.get("signature", ""),
            metadata=data.get("metadata", {}),
        )
