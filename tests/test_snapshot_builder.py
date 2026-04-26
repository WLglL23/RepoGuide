from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder
from repoguide.core.models.repo_snapshot import RepoSnapshot


def test_snapshot_builder_on_current_repo():
    """
    测试 SnapshotBuilder 能否在当前仓库上成功构建快照。

    验证点：
    - 返回的 snapshot 类型是 RepoSnapshot。
    - 文件数量大于 0，说明扫描成功。
    - 根路径、项目名称、项目类型均非空。
    - files 列表至少有 1 个文件。
    """
    # 在项目根目录（"."）上执行构建
    snapshot = SnapshotBuilder.build(".")

    # 类型检查
    assert isinstance(snapshot, RepoSnapshot)
    # 文件数量必须大于 0（扫描工作正常）
    assert snapshot.file_count > 0
    # 基础字段应被填充
    assert snapshot.root_path
    assert snapshot.project_name
    assert snapshot.project_type
    # files 列表不能为空
    assert len(snapshot.files) > 0


def test_snapshot_contains_repo_files_with_language():
    """
    测试快照中的文件是否都自动检测了语言。

    验证点：
    - 在当前仓库中，应该至少能检测到 Python 文件（因为本项目是 Python 项目）。
    - 所有文件的 language 集合中必须包含 "python"。
    """
    snapshot = SnapshotBuilder.build(".")

    # 收集所有文件的 language 字段值
    languages = {file.language for file in snapshot.files}

    # 由于当前项目是 Python 仓库，至少应该有 Python 语言被识别
    assert "python" in languages


def test_snapshot_has_important_files():
    """
    测试快照的 important_files 列表中是否包含 README.md。

    验证点：
    - README.md 是典型的重要文件，应该出现在 important_files 中。
    - 为了兼容大小写或路径差异，同时检查是否存在任意路径以 readme.md 结尾的文件。
    """
    snapshot = SnapshotBuilder.build(".")

    # 检查 important_files 列表中是否有 README.md
    # 使用 any 进行模糊匹配，避免路径前缀导致断言失败
    assert "README.md" in snapshot.important_files or any(
        path.lower().endswith("readme.md")
        for path in snapshot.important_files
    )


def test_snapshot_files_as_dicts():
    """
    测试 files_as_dicts() 方法的输出格式和内容完整性。

    验证点：
    - 返回的是 list 类型。
    - 列表长度等于 file_count。
    - 每个元素是 dict，且必须包含 "path" 和 "role" 字段。
    - 保证与旧版 ProjectMapper 的兼容性。
    """
    snapshot = SnapshotBuilder.build(".")

    files = snapshot.files_as_dicts()

    # 类型检查
    assert isinstance(files, list)
    # 长度必须与快照中的文件计数一致
    assert len(files) == snapshot.file_count
    # 每个 dict 必须包含基本字段
    assert "path" in files[0]
    assert "role" in files[0]