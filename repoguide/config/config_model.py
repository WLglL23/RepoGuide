"""
配置数据模型。

v2.3 阶段使用 dataclass 定义配置结构，保持轻量，不引入 Pydantic。

当前配置主要服务于：
1. Scanner 的忽略目录规则。
2. 隐藏模板文件白名单，例如 .env.example。
3. 后续 TestRunner 的测试命令白名单。

注意：
    当前配置模型只负责结构化数据，不负责读写文件。
    文件定位、YAML 解析、默认配置合并由 ConfigLoader 负责。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _as_list(value: Any) -> List[str]:
    """
    将配置中的值安全转换为 list[str]。

    为什么需要这个函数：
        YAML 中用户可能误写成：
            ignore_dirs: node_modules

        而不是：
            ignore_dirs:
              - node_modules

        为了避免程序直接崩溃，这里做保守转换：
        - None -> []
        - list -> 过滤后转为字符串列表
        - 其他类型 -> [str(value)]
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item) for item in value if item is not None]

    return [str(value)]


@dataclass
class ScanConfig:
    """扫描相关配置。"""

    ignore_dirs: List[str] = field(default_factory=list)
    """扫描时需要忽略的目录名。"""

    include_hidden_templates: List[str] = field(default_factory=list)
    """允许被扫描的隐藏模板文件，例如 .env.example。"""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScanConfig":
        """从 dict 构造 ScanConfig，并忽略未知字段。"""
        data = data or {}

        return cls(
            ignore_dirs=_as_list(data.get("ignore_dirs")),
            include_hidden_templates=_as_list(data.get("include_hidden_templates")),
        )


@dataclass
class TestConfig:
    """测试相关配置。"""

    allowed_commands: List[str] = field(default_factory=list)
    """允许执行的测试命令白名单。后续 TestRunner 会使用。"""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestConfig":
        """从 dict 构造 TestConfig，并忽略未知字段。"""
        data = data or {}

        return cls(
            allowed_commands=_as_list(data.get("allowed_commands")),
        )


@dataclass
class ProjectConfig:
    """项目元信息。"""

    name: Optional[str] = None
    """项目名称。为空时通常使用项目目录名。"""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        """从 dict 构造 ProjectConfig，并忽略未知字段。"""
        data = data or {}

        name = data.get("name")
        return cls(name=str(name) if name is not None else None)


@dataclass
class RepoGuideConfig:
    """RepoGuide 完整配置。"""

    version: int
    project: ProjectConfig
    scan: ScanConfig
    test: TestConfig

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoGuideConfig":
        """
        从字典构建 RepoGuideConfig。

        这里不直接使用 **data 的原因：
        - 用户可能在 config.yml 里添加未来字段。
        - 当前版本应该忽略未知字段，而不是直接 TypeError。
        """
        data = data or {}

        return cls(
            version=int(data.get("version", 1)),
            project=ProjectConfig.from_dict(data.get("project", {})),
            scan=ScanConfig.from_dict(data.get("scan", {})),
            test=TestConfig.from_dict(data.get("test", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转回 dict，便于测试、调试或后续序列化。"""
        return {
            "version": self.version,
            "project": {
                "name": self.project.name,
            },
            "scan": {
                "ignore_dirs": list(self.scan.ignore_dirs),
                "include_hidden_templates": list(self.scan.include_hidden_templates),
            },
            "test": {
                "allowed_commands": list(self.test.allowed_commands),
            },
        }