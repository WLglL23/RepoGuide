"""
storage 层：本地索引持久化读写。

当前 v2.2 阶段只实现 JSON 文件存储：

    .repoguide/
      indexes/
        repo_snapshot.json
        project_map.json

后续如果进入真正 RepoIndex 阶段，可以在这里继续扩展：
- SQLiteIndexStore
- DuckDBIndexStore
- VectorIndexStore
"""

from repoguide.storage.local_index_store import LocalIndexStore

__all__ = [
    "LocalIndexStore",
]