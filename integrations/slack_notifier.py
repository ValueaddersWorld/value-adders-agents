"""Slack notification helper."""

from __future__ import annotations

import json
import logging
import os
from typing import Iterable

import requests

LOGGER = logging.getLogger(__name__)


class SlackNotifier:
    """Send messages to a Slack incoming webhook if configured."""

    def __init__(self, webhook_url: str | None = None) -> None:
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url)

    def send(self, message: str, *, blocks: Iterable[dict] | None = None) -> None:
        if not self.is_configured:
            return
        payload: dict[str, object] = {"text": message}
        if blocks:
            payload["blocks"] = list(blocks)
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Failed to send Slack notification: %s", exc)


__all__ = ["SlackNotifier"]
