from pathlib import Path


__all__ = [
    "REPO_ROOT",
    "TOOLS_JSON",
    "README_FILE",
    "MARKER_START_STR",
    "MARKER_END_STR",
]

## Absolute path to this script's directory
THIS_DIR = Path(__file__).resolve().parent

## Path to repository root
REPO_ROOT = THIS_DIR.parent.parent.parent.parent.parent
## Path to tools.json
TOOLS_JSON = REPO_ROOT / ".repo" / "tools.json"
## Path to main README.md
README_FILE = REPO_ROOT / "README.md"

MARKER_START_STR = "<!-- MARKER-TOOLS:START -->"
MARKER_END_STR = "<!-- MARKER-TOOLS:END -->"
