from __future__ import annotations

from dataclasses import field
from pydantic import BaseModel, Field, ValidationError, field_validator

__all__ = ["Tool", "Tools", "ToolUrl"]


class ToolUrl(BaseModel):
    name: str
    url: str


class Tool(BaseModel):
    name: str
    urls: list[ToolUrl] = Field(default_factory=list)
    description: str = ""
    category: str = Field(default="uncategorized")
    platforms: list[str] = Field(default_factory=list)
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
    def has_platforms(self):
        return len(self.platforms) > 0

    @property
    def num_urls(self):
        return len(self.urls)

    @property
    def num_tags(self):
        return len(self.tags)

    @property
    def num_notes(self):
        return len(self.notes)

    @property
    def num_platforms(self):
        return len(self.platforms)

    @field_validator("platforms", mode="before")
    @classmethod
    def normalize_platforms(cls, v):
        """Ensure platforms list exists and normalize capitalization."""
        if not v:
            return []
        if isinstance(v, str):
            v = [v]
        return [p.strip().lower() for p in v if isinstance(p, str) and p.strip()]

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v):
        if not v or not isinstance(v, str) or not v.strip():
            return "uncategorized"
        return v.strip()


class Tools(BaseModel):
    tools: list[Tool] = Field(default_factory=list)

    @property
    def num_tools(self):
        return len(self.tools)

    @property
    def num_urls(self):
        return sum(tool.num_urls for tool in self.tools)

    @property
    def num_tags(self):
        return sum(tool.num_tags for tool in self.tools)

    @property
    def num_notes(self):
        return sum(tool.num_notes for tool in self.tools)

    @property
    def num_platforms(self):
        return sum(tool.num_platforms for tool in self.tools)
