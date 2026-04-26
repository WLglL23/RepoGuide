"""
RepoFile 数据模型。

表示仓库中的单个文件，整合 scanner、classifier、language detector 的基础结果。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from repoguide.core.language.language_detector import LanguageDetector


@dataclass
class RepoFile:
    """
    仓库文件模型。

    当前 v1 只保存静态元信息，不读取文件内容，不做 AST 解析。
    """

    path: str
    name: str
    size: int
    extension: str
    modified_time: float
    role: str = "unknown"
    language: str = "unknown"

    def __post_init__(self) -> None:
        """规范化字段，并在 language 缺省时自动推断语言。"""
        self.path = self.path.replace("\\", "/")
        self.name = self.name or Path(self.path).name
        self.extension = self.extension.lower()

        if self.extension and not self.extension.startswith("."):
            self.extension = f".{self.extension}"

        if self.language == "unknown":
            self.language = LanguageDetector.detect_by_extension(self.extension)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoFile":
        """
        从 scanner / classifier 产生的 dict 构造 RepoFile。

        兼容当前 v0 数据结构：
        {
            "path": "...",
            "name": "...",
            "size": ...,
            "extension": "...",
            "modified_time": ...,
            "role": "..."
        }
        """
        path = data.get("path", "")
        name = data.get("name") or Path(path).name
        extension = data.get("extension") or Path(path).suffix

        return cls(
            path=path,
            name=name,
            size=int(data.get("size", 0)),
            extension=extension,
            modified_time=float(data.get("modified_time", 0.0)),
            role=data.get("role", "unknown"),
            language=data.get("language", "unknown"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为 dict，便于旧 mapper / formatter 兼容。"""
        return {
            "path": self.path,
            "name": self.name,
            "size": self.size,
            "extension": self.extension,
            "modified_time": self.modified_time,
            "role": self.role,
            "language": self.language,
        }