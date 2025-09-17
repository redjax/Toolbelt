import json
import logging
import copy
from enum import Enum
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
