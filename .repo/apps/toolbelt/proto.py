from __future__ import annotations

from toolbelt import REPO_ROOT, TOOLS_JSON, ToolsFileManager

tools_manager = ToolsFileManager(tools_file=TOOLS_JSON)

with tools_manager as tools_mgr:
    print(f"Tools: {tools_mgr.data[:5]}")

    tools_mgr.sort()

    print(f"Sorted tools: {tools_mgr.data[:5]}")
