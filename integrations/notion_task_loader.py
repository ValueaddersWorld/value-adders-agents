"""Utilities for reading latest agent tasks from Notion."""

from __future__ import annotations

import logging
from typing import Dict

import requests

from .notion_logger import NotionConfig, _NOTION_API_URL

LOGGER = logging.getLogger(__name__)


def _rich_text_to_plain(prop: dict | None) -> str:
    if not prop:
        return ""
    rich_text = prop.get("rich_text") or []
    return " ".join(block.get("plain_text", "") for block in rich_text).strip()


def _status_to_name(prop: dict | None) -> str:
    if not prop:
        return ""
    status = prop.get("status")
    if isinstance(status, dict):
        return status.get("name", "")
    return ""


class NotionTaskLoader:
    """Fetch the most recent task information from the Notion database."""

    def __init__(self, config: NotionConfig | None = None, session: requests.Session | None = None) -> None:
        self.config = config or NotionConfig.from_env()
        self._session = session or requests.Session()
        if self.is_configured:
            self._session.headers.update(
                {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json",
                }
            )

    @property
    def is_configured(self) -> bool:
        return bool(self.config.api_key and self.config.database_id)

    def fetch_latest_entries(self, page_size: int = 100) -> Dict[str, dict]:
        """Return the most recent entry per agent alias."""
        if not self.is_configured:
            return {}

        payload = {
            "page_size": page_size,
            "sorts": [
                {
                    "timestamp": "last_edited_time",
                    "direction": "descending",
                }
            ],
        }
        try:
            response = self._session.post(
                f"{_NOTION_API_URL}/databases/{self.config.database_id}/query",
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Failed to query Notion database: %s", exc)
            return {}

        results = response.json().get("results", [])
        latest: Dict[str, dict] = {}
        for page in results:
            properties = page.get("properties", {})
            alias = _rich_text_to_plain(properties.get(self.config.agent_property)) if self.config.agent_property else ""
            if not alias:
                alias = page.get("id", "")
            if alias in latest:
                continue
            task_text = _rich_text_to_plain(properties.get(self.config.task_property)) if self.config.task_property else ""
            summary_text = _rich_text_to_plain(properties.get(self.config.summary_property)) if self.config.summary_property else ""
            status_name = _status_to_name(properties.get(self.config.status_property)) if self.config.status_property else ""
            latest[alias] = {
                "task": task_text,
                "summary": summary_text,
                "status": status_name,
            }
        return latest

    def generate_follow_up_tasks(self, base_tasks: Dict[str, str]) -> Dict[str, str]:
        """Merge Notion context with default tasks to produce follow-up instructions."""
        entries = self.fetch_latest_entries()
        if not entries:
            return base_tasks

        merged = dict(base_tasks)
        for alias, info in entries.items():
            summary = info.get("summary", "").strip()
            status = (info.get("status") or "").strip()
            previous_task = info.get("task", "").strip()

            if status.lower() == "needs review":
                context = summary or previous_task
                if context:
                    merged[alias] = (
                        "Await human review before execution. Summarise any adjustments needed based on:\n"
                        f"{context}\n"
                        "Prepare a concise briefing for the reviewer and list pending actions."
                    )
                else:
                    merged[alias] = (
                        "Await human review before proceeding. Provide an update on current blockers and what approval is required."
                    )
                continue

            if summary:
                merged[alias] = (
                    "Build on the previous deliverable summarised below."
                    " Outline concrete next steps, decisions made, and new deliverables.\n\n"
                    f"Previous summary:\n{summary}"
                )
            elif previous_task:
                merged[alias] = previous_task
        return merged


__all__ = ["NotionTaskLoader"]
