"""Reversible Git transport encoding for a maintainer's project-root prefix.

The three tokens are reserved path markers, not URLs or editable source facts.
Only configure this filter for the two district Markdown authoring files. It
does not locate the project, inspect other files, or change source fingerprints.
"""

import argparse
import sys


# LJ-PLACES-PATH-TRANSPORT-20261102: preserve exact local evidence bytes.
def transform(data: bytes, mode: str, project_root: str) -> bytes:
    """Translate known root prefixes while preserving every other input byte."""
    if mode not in {"clean", "smudge"}:
        raise ValueError("mode must be clean or smudge")
    if not project_root or not project_root.strip():
        raise ValueError("project_root is required")

    root = project_root.rstrip("\\/")
    if not root:
        raise ValueError("project_root must name a project directory")
    windows = (root.replace("/", "\\") + "\\").encode("utf-8")
    posix = (root.replace("\\", "/") + "/").encode("utf-8")
    mappings = [
        (windows.replace(b"\\", b"\\\\"), b"__LJ_PROJECT_ROOT_JSON_WIN__\\\\"),
        (windows, b"__LJ_PROJECT_ROOT_WIN__\\"),
        (posix, b"__LJ_PROJECT_ROOT_POSIX__/"),
    ]
    if mode == "smudge":
        mappings = [(marker, prefix) for prefix, marker in mappings]
    for source, target in sorted(mappings, key=lambda pair: len(pair[0]), reverse=True):
        data = data.replace(source, target)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("clean", "smudge"))
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()
    try:
        # Validate arguments before consuming input or emitting any content.
        transform(b"", args.mode, args.project_root)
        result = transform(sys.stdin.buffer.read(), args.mode, args.project_root)
    except ValueError as error:
        parser.error(str(error))
    sys.stdout.buffer.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
