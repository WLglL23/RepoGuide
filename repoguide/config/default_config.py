"""
默认配置文件内容。

DEFAULT_CONFIG_YAML 是 RepoGuide 默认配置的唯一文本来源。

用途：
1. ConfigLoader 在没有用户配置时使用它。
2. CLI init 命令写入 .repoguide/config.yml 时使用它。
3. 测试中可用它验证默认配置字段是否完整。
"""

DEFAULT_CONFIG_YAML = """\
version: 1

project:
  name: null

scan:
  ignore_dirs:
    - .git
    - node_modules
    - target
    - dist
    - build
    - out
    - venv
    - .venv
    - __pycache__
    - .idea
    - .vscode
    - .mypy_cache
    - .pytest_cache
  include_hidden_templates:
    - .env.example
    - .env.sample
    - .env.template

test:
  allowed_commands:
    - pytest
    - python -m pytest
    - mvn test
    - npm test
"""