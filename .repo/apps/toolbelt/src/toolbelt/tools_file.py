from __future__ import annotations

import copy
from enum import Enum
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


__all__ = ["ToolsFileManager"]


class ToolsFileManager:
    def __init__(self, tools_file: str | Path):
        self.tools_file = tools_file

        self.data = None
        self._original_data = None
        self._file_opened = False

    def __enter__(self):
        with open(self.tools_file, "r") as f:
            self.data = json.load(f)

        ## Store a copy of the original data
        self._original_data = copy.deepcopy(self.data)
        self._file_opened = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.data = self._original_data
            self._file_opened = False

            return False

        self._write()
        self._file_opened = False

        return False

    def exists(self) -> bool:
        return Path(str(self.tools_file)).exists()

    def read(self) -> list[dict]:
        if self.data is None:
            with open(self.tools_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            self._original_data = copy.deepcopy(self.data)
            self._file_opened = True

        return self.data

    def save(self) -> None:
        """Write current data to file immediately."""
        if self.data is not None:
            self._write()
        else:
            log.warning("No data to save, call read() or set data first.")

    def write(self, data: list[dict]) -> None:
        """Update data and save to file immediately."""
        self.data = data
        self._write()

    def _data_changed(self) -> bool:
        """Compare current data with original data to determine if changed."""
        return self.data != self._original_data

    def _write(self):
        if self._data_changed():
            with open(self.tools_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, default=str)

            ## Update original data after writing
            self._original_data = copy.deepcopy(self.data)
        else:
            log.debug("No changes detected, skipping write to file.")

    def close(self):
        if self._file_opened:
            self._write()
            self._file_opened = False

    def sort(
        self,
        sort_key: str = "name",
        sort_order: str = "asc",
    ) -> list[dict]:
        """Sort the tools in tools.json file.

        Params:
            sort_key (str): The key to sort by.
            sort_order (str): The order to sort in (asc or desc).
        """
        if self.data is None:
            self.read()

        key_funcs = {
            "name": lambda x: x.get("name", "").lower(),
            ## Extend with other keys if needed
        }

        if sort_key not in key_funcs:
            raise NotImplementedError(
                f"Sorting by key '{sort_key}' is not implemented."
            )

        sort_order = sort_order.lower()

        if sort_order == "asc":
            reverse = False
        elif sort_order == "desc":
            reverse = True
        else:
            raise ValueError("sort_order must be 'asc' or 'desc'")

        self.data.sort(key=key_funcs[sort_key], reverse=reverse)

        return self.data

    def dedupe(self):
        """Merge objects with the same name. Combine urls, tags, notes; keep longest description."""
        if self.data is None:
            self.read()

        merged = {}
        for obj in self.data:
            name = obj["name"]
            # Use lowercase name as the key for case-insensitive comparison
            name_key = name.lower()
            
            if name_key not in merged:
                ## Make a copy so we don't modify the original list
                merged[name_key] = copy.deepcopy(obj)
            else:
                m = merged[name_key]

                ## Combine and deduplicate 'urls', 'tags', and 'notes'
                m["urls"] = list(
                    {tuple(sorted(x.items())) for x in m.get("urls", [])}
                    | {tuple(sorted(x.items())) for x in obj.get("urls", [])}
                )

                m["urls"] = [dict(u) for u in m["urls"]]

                m["tags"] = list(set(m.get("tags", [])) | set(obj.get("tags", [])))
                m["notes"] = list(set(m.get("notes", [])) | set(obj.get("notes", [])))

                ## Keep the longer description
                desc1 = m.get("description", "")
                desc2 = obj.get("description", "")

                m["description"] = desc1 if len(desc1) >= len(desc2) else desc2
                
                ## Keep the name with better capitalization (prefer proper case over all lowercase)
                current_name = m.get("name", "")
                new_name = obj.get("name", "")
                
                # Prefer names that aren't all lowercase, or if both have same case style, prefer the one with more details
                if current_name.islower() and not new_name.islower():
                    m["name"] = new_name
                elif not current_name.islower() and new_name.islower():
                    # Keep current name (it has better capitalization)
                    pass
                elif len(obj.get("description", "")) > len(m.get("description", "")):
                    # If same case style, prefer the one with longer description and take its name
                    m["name"] = new_name

        ## Replace original data with the deduped and merged list
        self.data = list(merged.values())

        return self.data
