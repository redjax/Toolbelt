import re
import typing as t
from pathlib import Path

from toolbelt.constants import README_FILE, MARKER_END_STR, MARKER_START_STR
from toolbelt.classes import Tool


__all__ = ["ReadmeTableManager"]


class ReadmeTableManager:
    def __init__(self, readme_path: t.Union[str, Path] = README_FILE):
        self.readme_path = Path(readme_path)

    def update_readme_with_table(
        self, tools: list[t.Union[dict, Tool]], as_table: bool = True
    ):
        content = self.read_readme()

        new_section = (
            self.render_markdown_table(tools)
            if as_table
            else self.render_markdown_list(tools)
        )

        updated_content = self.replace_marker_section(content, new_section)

        self.write_readme(updated_content)

    def read_readme(self) -> str:
        return self.readme_path.read_text(encoding="utf-8")

    def write_readme(self, content: str):
        self.readme_path.write_text(content, encoding="utf-8")

    def replace_marker_section(self, content: str, new_section: str) -> str:
        """Replace the section between the markers with the new section."""
        pattern = re.compile(
            rf"({re.escape(MARKER_START_STR)})(.*)({re.escape(MARKER_END_STR)})",
            re.DOTALL,
        )

        if not pattern.search(content):
            raise ValueError(
                f"Markers {MARKER_START_STR} and/or {MARKER_END_STR} not found in README"
            )

        return pattern.sub(f"\\1\n\n{new_section}\n\n\\3", content)

    def render_markdown_table(self, tools: list[t.Union[dict, Tool]]) -> str:
        """Convert list of tools to markdown table."""
        headers = ["Name", "Description", "URLs", "Tags", "Notes"]
        rows = []

        for tool in tools:
            ## Access fields whether dict or Tool class
            name = tool["name"] if isinstance(tool, dict) else tool.name

            description = (
                tool.get("description", "")
                if isinstance(tool, dict)
                else tool.description
            )

            urls = tool.get("urls", []) if isinstance(tool, dict) else tool.urls
            tags = tool.get("tags", []) if isinstance(tool, dict) else tool.tags
            notes = tool.get("notes", []) if isinstance(tool, dict) else tool.notes

            ## Format URLs as comma-separated list or joined by space
            if urls and isinstance(urls[0], dict):
                url_list = ", ".join(u.get("url", "") for u in urls)
            elif urls:
                url_list = ", ".join(getattr(u, "url", str(u)) for u in urls)
            else:
                url_list = ""

            ## Format tags and notes as comma-list strings
            tag_str = ", ".join(tags)
            notes_str = ", ".join(notes)

            rows.append([name, description, url_list, tag_str, notes_str])

        ## Build markdown table string
        header_line = "| " + " | ".join(headers) + " |"
        separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"

        row_lines = [
            "| " + " | ".join(self.escape_pipe(str(cell)) for cell in row) + " |"
            for row in rows
        ]

        table_md = "\n".join([header_line, separator_line] + row_lines)

        return table_md

    def render_markdown_list(self, tools: list[t.Union[dict, Tool]]) -> str:
        """Render as list with name and description, URLs, tags, notes under each entry."""
        lines = []
        for tool in tools:
            name = tool["name"] if isinstance(tool, dict) else tool.name

            description = (
                tool.get("description", "")
                if isinstance(tool, dict)
                else tool.description
            )

            urls = tool.get("urls", []) if isinstance(tool, dict) else tool.urls
            tags = tool.get("tags", []) if isinstance(tool, dict) else tool.tags
            notes = tool.get("notes", []) if isinstance(tool, dict) else tool.notes

            lines.append(f"### {name}")

            if description:
                lines.append(f"{description}\n")

            if urls:

                url_lines = []

                for u in urls:
                    url_val = (
                        u.get("url", "")
                        if isinstance(u, dict)
                        else getattr(u, "url", "")
                    )

                    name_val = (
                        u.get("name", "")
                        if isinstance(u, dict)
                        else getattr(u, "name", "")
                    )

                    url_lines.append(
                        f"- [{name_val}]({url_val})" if name_val else f"- {url_val}"
                    )

                lines.append("**URLs:**\n" + "\n".join(url_lines) + "\n")

            if tags:
                lines.append("**Tags:** " + ", ".join(tags) + "\n")

            if notes:
                lines.append("**Notes:** " + ", ".join(notes) + "\n")

        return "\n".join(lines)

    @staticmethod
    def escape_pipe(text: str) -> str:
        """Escape pipes '|' for markdown tables."""
        return text.replace("|", "\\|")
