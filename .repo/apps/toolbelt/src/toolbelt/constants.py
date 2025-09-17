from pathlib import Path


__all__ = ["REPO_ROOT", "TOOLS_JSON"]

## Absolute path to this script's directory
THIS_DIR = Path(__file__).resolve().parent

## Path to repository root
REPO_ROOT = THIS_DIR.parent.parent.parent.parent.parent
## Path to tools.json
TOOLS_JSON = REPO_ROOT / ".repo" / "tools.json"
