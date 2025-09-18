from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError, field_validator

__all__ = ["Tool", "Tools"]


class ToolUrl(BaseModel):
    name: str
    url: str


class Tool(BaseModel):
    name: str
    urls: list[ToolUrl] = Field(default_factory=list)
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @property
    def has_urls(self):
        return len(self.urls) > 0

    @property
    def has_tags(self):
        return len(self.tags) > 0

    @property
    def has_notes(self):
        return len(self.notes) > 0

    @property
    def num_urls(self):
        return len(self.urls)

    @property
    def num_tags(self):
        return len(self.tags)

    @property
    def num_notes(self):
        return len(self.notes)


class Tools(BaseModel):
    tools: list[Tool] = field(default_factory=list)

    @property
    def num_tools(self):
        return len(self.tools)

    @property
    def num_urls(self):
        return sum([tool.num_urls for tool in self.tools])

    @property
    def num_tags(self):
        return sum([tool.num_tags for tool in self.tools])

    @property
    def num_notes(self):
        return sum([tool.num_notes for tool in self.tools])
