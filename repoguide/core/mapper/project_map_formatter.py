"""
项目地图格式化器。

将 project_map 字典转换为可读的文本输出。
"""

from typing import Dict, Any, List


def format_project_map(project_map: Dict[str, Any]) -> str:
    """
    把项目地图字典格式化为人类友好的多行文本。

    Args:
        project_map: 由 ProjectMapper.generate_project_map 生成的字典，
                     包含 root_path, project_type, file_count,
                     important_files, entrypoint_candidates,
                     config_candidates, build_files, test_files,
                     possible_run_commands, top_level_tree 等字段。

    Returns:
        格式化后的字符串，适合打印或保存为文档。
    """
    # 用于逐行拼接最终输出文本的列表
    lines = []

    # 标题
    lines.append("RepoGuide v0 Project Map")
    lines.append("")

    # 项目根目录路径
    lines.append("Project Root:")
    lines.append(str(project_map.get("root_path", "")))
    lines.append("")

    # 识别出的项目类型
    lines.append("Detected Project Type:")
    lines.append(str(project_map.get("project_type", "unknown")))
    lines.append("")

    # 文件总数
    lines.append("File Count:")
    lines.append(str(project_map.get("file_count", 0)))
    lines.append("")

    def add_section(title: str, items: List[str]) -> None:
        """
        添加一个带标题的列表段落。

        如果 items 为空，则输出 "- none" 以避免空段落造成困惑；
        否则逐项输出。

        Args:
            title: 段落标题，如 "Important Files:"
            items: 项目路径或命令字符串列表
        """
        lines.append(title)

        if not items:
            # 显式标明没有该类文件
            lines.append("- none")
        else:
            # 每项前面加 "- " 作为列表标记
            for item in items:
                lines.append(f"- {item}")

        # 段落结束插入一个空行
        lines.append("")

    # 六大分类清单：重要文件、候选入口、配置、构建、测试、推荐运行命令
    add_section("Important Files:", project_map.get("important_files", []))
    add_section("Entrypoint Candidates:", project_map.get("entrypoint_candidates", []))
    add_section("Config Candidates:", project_map.get("config_candidates", []))
    add_section("Build Files:", project_map.get("build_files", []))
    add_section("Test Files:", project_map.get("test_files", []))
    add_section("Possible Run Commands:", project_map.get("possible_run_commands", []))

    # 顶层目录结构（通常是预先格式化的多行字符串）
    lines.append("Top-level Structure:")
    lines.append(project_map.get("top_level_tree", ""))

    # 将所有行用换行符连接成最终字符串
    return "\n".join(lines)