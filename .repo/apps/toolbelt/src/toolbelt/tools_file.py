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

    def read(self) -> list[dict]:
        if self.data is None:
            with open(self.tools_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            self._original_data = copy.deepcopy(self.data)
            self._file_opened = True

        return self.data

    def write(self, data: list[dict]) -> None:
        self.data = data

    def _write(self):
        with open(self.tools_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, default=str)

    def close(self):
        if self._file_opened:
            self._write()
            self._file_opened = False

    def sort(
        self,
        sort_key: str = "name",
        sort_order: str = "asc",
        save: bool = False,
    ) -> list[dict]:
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

        if save:
            self._write()

        return self.data
