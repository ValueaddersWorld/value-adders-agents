"""Notion logging utilities for Value Adders agents."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional

import requests

LOGGER = logging.getLogger(__name__)

_NOTION_API_URL = "https://api.notion.com/v1"
_DEFAULT_TITLE_PROPERTY = "Name"
_DEFAULT_STATUS_PROPERTY = "Status"
_DEFAULT_AGENT_PROPERTY = "Agent"
_DEFAULT_TASK_PROPERTY = "Task"


@dataclass(slots=True)
class NotionConfig:
    """Configuration for connecting to a Notion database."""

    api_key: str | None = None
    database_id: str | None = None
    title_property: str = _DEFAULT_TITLE_PROPERTY
    status_property: str | None = _DEFAULT_STATUS_PROPERTY
    agent_property: str | None = _DEFAULT_AGENT_PROPERTY
    task_property: str | None = _DEFAULT_TASK_PROPERTY

    @classmethod
    def from_env(cls) -> "NotionConfig":
        """Build configuration from environment variables."""
        return cls(
            api_key=os.getenv("NOTION_API_KEY"),
            database_id=os.getenv("NOTION_DATABASE_ID"),
            title_property=os.getenv("NOTION_TITLE_PROPERTY", _DEFAULT_TITLE_PROPERTY),
            status_property=os.getenv("NOTION_STATUS_PROPERTY", _DEFAULT_STATUS_PROPERTY) or None,
            agent_property=os.getenv("NOTION_AGENT_PROPERTY", _DEFAULT_AGENT_PROPERTY) or None,
            task_property=os.getenv("NOTION_TASK_PROPERTY", _DEFAULT_TASK_PROPERTY) or None,
        )


class NotionLogger:
    """Lightweight helper for recording orchestration activity in Notion."""

    def __init__(self, config: NotionConfig | None = None, session: Optional[requests.Session] = None) -> None:
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
        """Return True when all required settings are available."""
        return bool(self.config.api_key and self.config.database_id)

    def create_task_entry(self, agent_alias: str, task_description: str, status: str = "Assigned") -> str | None:
        """Create a Notion page representing an assigned task."""
        if not self.is_configured:
            return None

        properties = self._build_properties(agent_alias, task_description, status)
        children = self._build_children(agent_alias, task_description, status)

        payload = {
            "parent": {"database_id": self.config.database_id},
            "properties": properties,
            "children": children,
        }

        try:
            response = self._session.post(
                f"{_NOTION_API_URL}/pages",
                data=json.dumps(payload),
                timeout=15,
            )
            response.raise_for_status()
            page_id = response.json().get("id")
            if not page_id:
                LOGGER.warning("Notion response missing page id for agent '%s'", agent_alias)
            return page_id
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Unable to create Notion entry for %s: %s", agent_alias, exc)
            return None

    def update_task_entry(
        self,
        page_id: str,
        *,
        status: str,
        summary: str | None = None,
        extra_blocks: Optional[Iterable[dict]] = None,
    ) -> None:
        """Update a task entry with a new status and optional summary."""
        if not self.is_configured or not page_id:
            return

        properties = self._build_properties(
            None,
            None,
            status,
            include_task=False,
            include_title=False,
        )

        try:
            if properties:
                response = self._session.patch(
                    f"{_NOTION_API_URL}/pages/{page_id}",
                    data=json.dumps({"properties": properties}),
                    timeout=15,
                )
                response.raise_for_status()

            blocks_to_append = list(extra_blocks or [])
            if summary:
                blocks_to_append.append(self._paragraph_block(summary))

            if blocks_to_append:
                response = self._session.patch(
                    f"{_NOTION_API_URL}/blocks/{page_id}/children",
                    data=json.dumps({"children": blocks_to_append}),
                    timeout=15,
                )
                response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Unable to update Notion entry %s: %s", page_id, exc)

    def _build_properties(
        self,
        agent_alias: str | None,
        task_description: str | None,
        status: str,
        *,
        include_task: bool = True,
        include_title: bool = True,
    ) -> dict:
        properties: dict[str, dict] = {}

        title_property = self.config.title_property or _DEFAULT_TITLE_PROPERTY
        if include_title:
            if agent_alias and task_description:
                title_content = self._build_title(agent_alias, status, task_description)
            else:
                title_content = f"{status} - {datetime.now(timezone.utc).isoformat()[:19]}"

            properties[title_property] = {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": title_content[:200]},
                    }
                ]
            }

        if self.config.status_property:
            properties[self.config.status_property] = {"status": {"name": status[:100]}}

        if include_task and self.config.agent_property and agent_alias:
            properties[self.config.agent_property] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": agent_alias[:200]},
                    }
                ]
            }

        if include_task and self.config.task_property and task_description:
            properties[self.config.task_property] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": task_description[:2000]},
                    }
                ]
            }

        return properties

    def _build_children(self, agent_alias: str, task_description: str, status: str) -> list[dict]:
        timestamp = datetime.now(timezone.utc).isoformat()
        return [
            self._paragraph_block(f"Agent: {agent_alias}"),
            self._paragraph_block(f"Status: {status}"),
            self._paragraph_block(f"Task: {task_description}"),
            self._paragraph_block(f"Logged at: {timestamp}"),
        ]

    @staticmethod
    def _paragraph_block(content: str) -> dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content[:2000]},
                    }
                ]
            },
        }

    @staticmethod
    def _build_title(agent_alias: str, status: str, task_description: str) -> str:
        return f"{agent_alias} - {status} - {task_description[:70]}"


__all__ = ["NotionLogger", "NotionConfig"]
