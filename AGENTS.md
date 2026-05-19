# RepoGuide Agent Notes

This file is the project memory for AI-assisted work on RepoGuide. At the start of each future session in this repository, read this file first, then read `docs/current-status.md` if the task touches project direction, architecture, or progress.

## Project Intent

RepoGuide is a local-first repository understanding tool for learning, project handoff, and developer onboarding.

The owner's current goal is to regain control of the project after too much AI-generated material accumulated. Prefer small, understandable steps over broad generated architecture.

## Current Stage

Current practical stage: v3 preparation.

Completed foundation:

- Local scanning and file metadata collection.
- Rule-based file role classification.
- Simple project type detection.
- Extension-based language detection.
- `RepoFile`, `RepoSnapshot`, and `ProjectMap` core models.
- `RepoGuide.map()`, `RepoGuide.index()`, `RepoGuide.build_snapshot()`, and `RepoGuide.build_project_map()`.
- Local JSON index persistence in `.repoguide/indexes/`.
- Project-level config loading from `.repoguide/config.yml`.
- Initial v3 model files:
  - `CodeSymbol`
  - `ApiEndpoint`
  - `RepoIndex`

Not implemented yet:
- Java/Spring parser.
- RepoIndex storage integration.
- Call graph.
- LLM Q&A.
- git diff diagnosis.
- Patch generation.
- API Server.
- Web UI.

## Working Rules

- Keep changes small and reviewable.
- Preserve the existing v2 behavior unless the user explicitly asks to change it.
- Do not add broad abstractions just because the roadmap mentions them.
- Prefer standard library parsing first. For the first v3 slice, use Python `ast` before considering Tree-sitter.
- For this learning project, tests should be small guardrails, not a second project. Prefer one focused smoke test per new capability.
- Avoid reviving old generated docs as source of truth. Treat `docs/current-status.md` as the status source.
- When editing docs, keep them short and current.

## Local Commands

In this environment, use the project virtualenv explicitly:

```powershell
E:\Project\My\RepoGuide\.venv\Scripts\python.exe -m compileall repoguide main.py
E:\Project\My\RepoGuide\.venv\Scripts\python.exe -m pytest -q
```

Current verified result on 2026-05-19:

```text
45 passed
```

## Documentation Policy

Keep only useful project-control docs:

- `AGENTS.md`: agent memory and collaboration rules.
- `docs/current-status.md`: current technical status and next steps.
- `docs/v0.2.3.md`: concise historical summary for v2.1-v2.3.

Avoid adding large speculative design documents. If a design is needed, add a compact implementation plan to `docs/current-status.md` or a focused new doc.

## Current Parser Status

The Python parser has two parser-only slices implemented:

- `repoguide/core/parser/python_parser.py`
- Uses Python standard library `ast`.
- Extracts top-level functions, classes, and class methods into `CodeSymbol`.
- Extracts simple FastAPI route decorators into `ApiEndpoint`, such as `@app.get("/path")` and `@router.post("/path")`.
- `RepoIndexBuilder` can aggregate `RepoSnapshot`, `ProjectMap`, parser symbols, and API endpoints into `RepoIndex`.
- Does not yet save `RepoIndex` to local storage.

## Next Suggested Step

Wire RepoIndex into storage:

- Add `repo_index.json` support to `LocalIndexStore`.
- Add `save_repo_index()`, `load_repo_index()`, and `has_repo_index()`.
- Keep CLI integration for a later step.
