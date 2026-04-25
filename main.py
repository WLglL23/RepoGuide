import argparse
import sys

from repoguide.core.scanner.repo_scanner import scan_repo
from repoguide.core.classifier.file_classifier import classify_files, identify_project_type
from repoguide.core.mapper.project_mapper import generate_project_map
from repoguide.core.mapper.project_map_formatter import format_project_map


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="repoguide-v0",
        description="RepoGuide v0: scan a local repository and generate a basic project map.",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the local project directory. Defaults to current directory.",
    )

    args = parser.parse_args()
    root_path = args.path

    try:
        files = scan_repo(root_path)
        classified_files = classify_files(files)
        project_type = identify_project_type(classified_files, root_path)

        project_map = generate_project_map(
            files=classified_files,
            root_path=root_path,
            project_type=project_type,
        )

        print(format_project_map(project_map))
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except PermissionError as e:
        print(f"Permission error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())