"""
LanguageDetector - 基于文件扩展名的语言检测器

v1 第一版只根据文件扩展名判断语言。
后续可以扩展为基于文件名、shebang、内容特征的检测器。
"""

from pathlib import Path


class LanguageDetector:
    """第一版语言检测器：仅根据文件扩展名做静态映射。"""

    EXTENSION_MAP: dict[str, str] = {
        ".py": "python",
        ".java": "java",
        ".js": "javascript",
        ".ts": "typescript",
        ".xml": "xml",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".json": "json",
        ".sql": "sql",
        ".md": "markdown",
    }

    @staticmethod
    def detect(file_path: str) -> str:
        """
        根据文件路径或文件名推断语言。

        Args:
            file_path: 文件路径，例如 "src/main.py"

        Returns:
            语言名称，例如 "python"；无法识别则返回 "unknown"
        """
        suffix = Path(file_path).suffix.lower()
        return LanguageDetector.detect_by_extension(suffix)

    @staticmethod
    def detect_by_extension(extension: str) -> str:
        """
        根据扩展名推断语言。

        Args:
            extension: 扩展名，例如 ".py"。如果传入 "py"，也会自动修正。

        Returns:
            语言名称，无法识别则返回 "unknown"
        """
        if not extension:
            return "unknown"

        normalized = extension.lower()

        if not normalized.startswith("."):
            normalized = f".{normalized}"

        return LanguageDetector.EXTENSION_MAP.get(normalized, "unknown")

    @staticmethod
    def supported_extensions() -> list[str]:
        """返回当前支持的扩展名列表。"""
        return sorted(LanguageDetector.EXTENSION_MAP.keys())