from __future__ import annotations

import json
from pathlib import Path
from toolbelt.constants import REPO_ROOT, TOOLS_JSON

OLD_TOOLS_FILE = TOOLS_JSON
NEW_TOOLS_FILE = REPO_ROOT / ".repo/tools_migrated.json"

PLATFORM_KEYWORDS = {"linux", "mac", "windows", "android", "ios"}


def migrate_tool(obj: dict) -> dict:
    """Transform old JSON structure to new structure."""
    new_obj = dict(obj)

    # Add missing fields
    new_obj.setdefault("category", "uncategorized")

    # Split platforms and tags
    tags = set(new_obj.get("tags", []))
    platforms = [t for t in tags if t.lower() in PLATFORM_KEYWORDS]
    tags = [t for t in tags if t.lower() not in PLATFORM_KEYWORDS]

    # Update fields
    new_obj["platforms"] = platforms or ["linux", "mac", "windows", "android", "ios"]
    new_obj["tags"] = tags

    return new_obj


def migrate_json_file(src_path: Path, dst_path: Path):
    data = json.loads(src_path.read_text(encoding="utf-8"))
    migrated = [migrate_tool(obj) for obj in data]
    dst_path.write_text(json.dumps(migrated, indent=4), encoding="utf-8")

    print(f"Migrated {len(migrated)} tools to {dst_path}")


if __name__ == "__main__":
    migrate_json_file(OLD_TOOLS_FILE, NEW_TOOLS_FILE)
