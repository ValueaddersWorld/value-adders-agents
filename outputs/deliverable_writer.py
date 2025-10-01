"""Write agent deliverables to Markdown files."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class DeliverableWriter:
    """Persist agent outputs into the repository for human review."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        base_path = Path(base_dir) if base_dir else Path("outputs")
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write(self, agent_alias: str, content: str) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        safe_alias = agent_alias.replace("/", "-")
        agent_dir = self.base_path / safe_alias
        agent_dir.mkdir(parents=True, exist_ok=True)
        filename = agent_dir / f"{timestamp}.md"
        header = f"# {agent_alias} deliverable\n\nGenerated at {timestamp} UTC\n\n"
        filename.write_text(header + content, encoding="utf-8")
        return filename


__all__ = ["DeliverableWriter"]
