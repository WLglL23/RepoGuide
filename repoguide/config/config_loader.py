"""
配置加载器。

负责：
1. 定位 .repoguide/config.yml
2. 读取 YAML 配置
3. 与默认配置做深度合并
4. 返回 RepoGuideConfig 实例
5. 为 CLI init 提供默认配置写入能力

当前 v2.3 行为：
    - 如果 config.yml 不存在，使用默认配置。
    - 如果 config.yml 损坏，使用默认配置。
    - 用户配置只需要写自己想覆盖的部分，其余字段继承默认配置。
"""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

import yaml

from repoguide.config.config_model import RepoGuideConfig
from repoguide.config.default_config import DEFAULT_CONFIG_YAML


class ConfigLoader:
    """RepoGuide 配置加载器。"""

    CONFIG_RELATIVE_PATH = ".repoguide/config.yml"

    @staticmethod
    def config_path(root_path: str | Path) -> Path:
        """
        获取项目配置文件路径。

        Args:
            root_path: 项目根目录。

        Returns:
            .repoguide/config.yml 的绝对路径。
        """
        return Path(root_path).expanduser().resolve() / ConfigLoader.CONFIG_RELATIVE_PATH

    @staticmethod
    def load(root_path: str | Path) -> RepoGuideConfig:
        """
        加载项目配置。

        优先读取：
            <root_path>/.repoguide/config.yml

        如果文件不存在或解析失败，则使用默认配置。

        合并规则：
            默认配置作为基础，用户配置覆盖其中一部分。
            对嵌套 dict 使用深度合并，而不是浅合并。

        Args:
            root_path: 项目根目录。

        Returns:
            RepoGuideConfig 实例。
        """
        default_data = ConfigLoader._load_default_config_data()
        user_data = ConfigLoader._load_user_config_data(root_path)

        merged = ConfigLoader._deep_merge(default_data, user_data)

        return RepoGuideConfig.from_dict(merged)

    @staticmethod
    def create_default_config(root_path: str | Path, force: bool = False) -> Path:
        """
        在项目中创建默认配置文件 .repoguide/config.yml。

        Args:
            root_path: 项目根目录。
            force: 如果 config.yml 已存在，是否覆盖。

        Returns:
            写入或已存在的 config.yml 路径。
        """
        config_path = ConfigLoader.config_path(root_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if config_path.exists() and not force:
            return config_path

        config_path.write_text(DEFAULT_CONFIG_YAML, encoding="utf-8")
        return config_path

    @staticmethod
    def _load_default_config_data() -> Dict[str, Any]:
        """
        解析默认 YAML 配置。

        默认配置由代码维护，如果这里解析失败，说明开发阶段配置写错了，
        因此直接返回一个最小可用结构，避免运行时崩溃。
        """
        try:
            data = yaml.safe_load(DEFAULT_CONFIG_YAML) or {}
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError:
            return {}

    @staticmethod
    def _load_user_config_data(root_path: str | Path) -> Dict[str, Any]:
        """
        读取用户配置。

        如果配置文件不存在、读取失败或 YAML 损坏，则返回空 dict。
        上层会用默认配置补齐。
        """
        config_path = ConfigLoader.config_path(root_path)

        if not config_path.exists():
            return {}

        try:
            data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            return data if isinstance(data, dict) else {}
        except (OSError, yaml.YAMLError):
            return {}

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        深度合并两个 dict。

        规则：
            - base 是默认配置。
            - override 是用户配置。
            - 如果同一个 key 两边都是 dict，则递归合并。
            - 否则用户配置覆盖默认配置。

        示例：
            base:
                scan:
                  ignore_dirs: [...]
                  include_hidden_templates: [...]

            override:
                scan:
                  ignore_dirs:
                    - custom_ignore

            结果：
                scan:
                  ignore_dirs:
                    - custom_ignore
                  include_hidden_templates: [...]
        """
        result = deepcopy(base)

        for key, value in (override or {}).items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)

        return result