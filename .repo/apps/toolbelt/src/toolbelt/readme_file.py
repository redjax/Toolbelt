from __future__ import annotations

import logging
from pathlib import Path
import re
import typing as t

from toolbelt.classes import Tool
from toolbelt.constants import MARKER_END_STR, MARKER_START_STR, README_FILE

log = logging.getLogger(__name__)


__all__ = ["ReadmeTableManager"]


class ReadmeTableManager:
    def __init__(self, readme_path: t.Union[str, Path] = README_FILE):
        self.readme_path = Path(readme_path)

    @staticmethod
    def escape_pipe(text: str) -> str:
        """Escape pipe characters in Markdown tables."""
        return text.replace("|", "\\|")

    def update_readme_with_table(
        self,
        tools: list[t.Union[dict, Tool]],
        as_table: bool = True,
        render_tags: bool = False,
        render_notes: bool = False,
    ):
        try:
            content = self.read_readme()

            if as_table:
                new_section = self.render_markdown_table(
                    tools, render_tags, render_notes
                )
            else:
                new_section = self.render_markdown_list(
                    tools, render_tags, render_notes
                )

            updated_content = self.replace_marker_section(content, new_section)

            self.write_readme(updated_content)
        except Exception as e:
            log.error(f"Error updating README: {e}")

            raise

    def read_readme(self) -> str:
        return self.readme_path.read_text(encoding="utf-8")

    def write_readme(self, content: str):
        self.readme_path.write_text(content, encoding="utf-8")

    def replace_marker_section(self, content: str, new_section: str) -> str:
        pattern = re.compile(
            rf"({re.escape(MARKER_START_STR)})(.*)({re.escape(MARKER_END_STR)})",
            re.DOTALL,
        )

        if not pattern.search(content):
            raise ValueError(
                f"Markers {MARKER_START_STR} and/or {MARKER_END_STR} not found in README"
            )

        return pattern.sub(f"\\1\n\n{new_section}\n\n\\3", content)

    def render_markdown_table(
        self,
        tools: list[t.Union[dict, Tool]],
        render_tags: bool = False,
        render_notes: bool = False,
    ) -> str:
        headers = ["Name", "Description", "URLs"]
        if render_tags:
            headers.append("Tags")
        if render_notes:
            headers.append("Notes")

        rows = []
        for tool in tools:
            name = tool["name"] if isinstance(tool, dict) else tool.name
            description = (
                tool.get("description", "")
                if isinstance(tool, dict)
                else tool.description
            )

            # Extract URLs and separate 'home' link
            urls = tool.get("urls", []) if isinstance(tool, dict) else tool.urls

            home_url = None
            other_urls = []
            for u in urls:
                url_val = (
                    u.get("url", "") if isinstance(u, dict) else getattr(u, "url", "")
                )
                if url_val == "" or url_val is None:
                    continue
                is_home = (
                    u.get("name", "") if isinstance(u, dict) else getattr(u, "name", "")
                ) == "home"
                if is_home:
                    home_url = url_val
                else:
                    other_urls.append(u)

            if not home_url:
                raise ValueError(f"Tool '{name}' does not have a 'home' URL.")

            # Markdown link for the Name column
            name_link = f"[{name}]({home_url})"

            # Format other URLs as markdown links [name](url) or plain url
            def format_url(u):
                url_val = (
                    u.get("url", "") if isinstance(u, dict) else getattr(u, "url", "")
                )
                name_val = (
                    u.get("name", "") if isinstance(u, dict) else getattr(u, "name", "")
                )
                return f"[{name_val}]({url_val})" if name_val else url_val

            url_list_md = (
                ", ".join(format_url(u) for u in other_urls) if other_urls else ""
            )

            row = [name_link, description, url_list_md]

            if render_tags:
                tags = tool.get("tags", []) if isinstance(tool, dict) else tool.tags
                tag_str = ", ".join(tags)
                row.append(tag_str)

            if render_notes:
                notes = tool.get("notes", []) if isinstance(tool, dict) else tool.notes
                notes_str = ", ".join(notes)
                row.append(notes_str)

            rows.append(row)

        header_line = "| " + " | ".join(headers) + " |"
        separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
        row_lines = [
            "| " + " | ".join(self.escape_pipe(str(cell)) for cell in row) + " |"
            for row in rows
        ]

        return "\n".join([header_line, separator_line] + row_lines)

    def render_markdown_list(
        self,
        tools: list[t.Union[dict, Tool]],
        render_tags: bool = False,
        render_notes: bool = False,
    ) -> str:
        lines = []

        for tool in tools:
            name = tool["name"] if isinstance(tool, dict) else tool.name

            description = (
                tool.get("description", "")
                if isinstance(tool, dict)
                else tool.description
            )

            urls = tool.get("urls", []) if isinstance(tool, dict) else tool.urls

            home_url = None

            other_urls = []

            for u in urls:
                url_val = (
                    u.get("url", "") if isinstance(u, dict) else getattr(u, "url", "")
                )

                if url_val == "" or url_val is None:
                    continue

                is_home = (
                    u.get("name", "") if isinstance(u, dict) else getattr(u, "name", "")
                ) == "home"

                if is_home:
                    home_url = url_val
                else:
                    other_urls.append(u)

            if not home_url:
                raise ValueError(f"Tool '{name}' does not have a 'home' URL.")

            ## Name linked to home URL
            lines.append(f"### [{name}]({home_url})")

            if description:
                lines.append(f"{description}\n")

            if other_urls:
                url_lines = []

                for u in other_urls:
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

            if render_tags and (
                tags := (tool.get("tags", []) if isinstance(tool, dict) else tool.tags)
            ):
                lines.append("**Tags:** " + ", ".join(tags) + "\n")

            if render_notes and (
                notes := (
                    tool.get("notes", []) if isinstance(tool, dict) else tool.notes
                )
            ):
                lines.append("**Notes:** " + ", ".join(notes) + "\n")

        return "\n".join(lines)
