"""Per-file processing status. A file is never silently skipped: it is processed, partial or failed."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FileCoverage:
    file_id: str
    rel_path: str
    kind: str
    adapter: str = ""
    status: str = "failed"      # processed | partial | failed
    observations: int = 0
    lines: int = 0
    unparsed: int = 0
    notes: list[str] = field(default_factory=list)


@dataclass
class Coverage:
    files: list[FileCoverage] = field(default_factory=list)
    tables: dict[str, int] = field(default_factory=dict)
